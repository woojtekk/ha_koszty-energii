# Koszty Energii

Integracja `koszty_energii` tworzy sensory zuzycia energii dla okresow:
- dziennie
- tygodniowo (ISO, poniedzialek = pierwszy dzien tygodnia)
- miesiecznie
- kwartalnie
- polrocznie
- rocznie

Bazuje na encji licznika narastajacego (np. kWh). Wartosci sa liczone jako roznica od poczatku okresu. Jesli licznik sie zresetuje (spadek wartosci), okres startuje od nowa.

## Instalacja (HACS)

1. HACS -> Integrations -> ... -> Custom repositories
2. Dodaj repozytorium `https://github.com/woojtekk/ha_koszty-energii` jako **Integration**
3. Zainstaluj `Koszty Energii`
4. Zrestartuj Home Assistant

## Konfiguracja (YAML)

```yaml
sensor:
  - platform: koszty_energii
    source_entity: sensor.twoj_licznik
    name: Koszty Energii
```

### Parametry
- `source_entity` (wymagane): encja licznika narastajacego
- `name` (opcjonalne): prefix nazwy sensora (domyslnie `Koszty Energii`)

## Sensory
Dla podanego `name` powstaja sensory:
- `Koszty Energii Dziennie`
- `Koszty Energii Tygodniowo`
- `Koszty Energii Miesiecznie`
- `Koszty Energii Kwartalnie`
- `Koszty Energii Polrocznie`
- `Koszty Energii Rocznie`

## Uwagi
- Jednostka jest dziedziczona z encji licznika.
- Aktualizacja co 1 minute.
- Sensory przechowuja stan po restarcie (RestoreEntity).

## Wsparcie
- Issues: https://github.com/woojtekk/ha_koszty-energii/issues
- Dokumentacja: https://github.com/woojtekk/ha_koszty-energii
