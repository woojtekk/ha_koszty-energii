"""Sensors for Koszty Energii."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import CONF_NAME, CONF_SOURCE_ENTITY, DEFAULT_NAME
from .schema import PLATFORM_SCHEMA, SCAN_INTERVAL


@dataclass(frozen=True)
class PeriodDef:
    key: str
    name: str
    period_id: Callable[[date], str]


PERIODS: list[PeriodDef] = [
    PeriodDef(
        key="daily",
        name="Dziennie",
        period_id=lambda d: d.isoformat(),
    ),
    PeriodDef(
        key="weekly",
        name="Tygodniowo",
        period_id=lambda d: f"{d.isocalendar().year}-W{d.isocalendar().week:02d}",
    ),
    PeriodDef(
        key="monthly",
        name="Miesiecznie",
        period_id=lambda d: f"{d.year}-{d.month:02d}",
    ),
    PeriodDef(
        key="quarterly",
        name="Kwartalnie",
        period_id=lambda d: f"{d.year}-Q{((d.month - 1) // 3) + 1}",
    ),
    PeriodDef(
        key="half_yearly",
        name="Polrocznie",
        period_id=lambda d: f"{d.year}-H{1 if d.month <= 6 else 2}",
    ),
    PeriodDef(
        key="yearly",
        name="Rocznie",
        period_id=lambda d: f"{d.year}",
    ),
]


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up sensors from YAML."""
    await _async_setup_common(hass, config, async_add_entities)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up sensors from config entry (not yet implemented)."""
    config = entry.data
    await _async_setup_common(hass, config, async_add_entities)


async def _async_setup_common(hass: HomeAssistant, config: ConfigType, async_add_entities):
    source_entity = config[CONF_SOURCE_ENTITY]
    name = config.get(CONF_NAME, DEFAULT_NAME)

    entities = [
        PeriodEnergySensor(
            hass=hass,
            source_entity=source_entity,
            name=f"{name} {period.name}",
            period=period,
        )
        for period in PERIODS
    ]

    async_add_entities(entities, update_before_add=True)


class PeriodEnergySensor(SensorEntity, RestoreEntity):
    """Energy usage for a given period based on a source meter entity."""

    _attr_should_poll = True
    _attr_icon = "mdi:flash"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hass: HomeAssistant, source_entity: str, name: str, period: PeriodDef):
        self.hass = hass
        self._source_entity = source_entity
        self._period = period
        self._attr_name = name

        self._attr_unique_id = f"{source_entity}_{period.key}"

        self._state: Optional[float] = None
        self._period_id: Optional[str] = None
        self._period_start_value: Optional[float] = None
        self._unit_of_measurement: Optional[str] = None

    @property
    def native_value(self) -> Optional[float]:
        return self._state

    @property
    def native_unit_of_measurement(self) -> Optional[str]:
        return self._unit_of_measurement

    async def async_added_to_hass(self) -> None:
        """Restore state from storage if available."""
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is None:
            return

        if last.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN, None):
            try:
                self._state = float(last.state)
            except ValueError:
                self._state = None

        attrs = last.attributes or {}
        self._period_id = attrs.get("period_id")
        try:
            if "period_start_value" in attrs:
                self._period_start_value = float(attrs["period_start_value"])
        except (TypeError, ValueError):
            self._period_start_value = None

    async def async_update(self) -> None:
        """Fetch state from the source entity and compute period usage."""
        state = self.hass.states.get(self._source_entity)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            self._state = None
            return

        try:
            source_value = float(state.state)
        except (TypeError, ValueError):
            self._state = None
            return

        self._unit_of_measurement = state.attributes.get("unit_of_measurement")

        today = date.today()
        current_period_id = self._period.period_id(today)

        reset = False
        if self._period_id is None or self._period_id != current_period_id:
            reset = True
        elif self._period_start_value is None:
            reset = True
        elif source_value < self._period_start_value:
            reset = True

        if reset:
            self._period_id = current_period_id
            self._period_start_value = source_value
            self._state = 0.0
            return

        self._state = max(0.0, source_value - self._period_start_value)

    @property
    def extra_state_attributes(self):
        return {
            "source_entity": self._source_entity,
            "period": self._period.key,
            "period_id": self._period_id,
            "period_start_value": self._period_start_value,
        }
