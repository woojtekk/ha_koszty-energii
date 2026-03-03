# Koszty Energii

Integracja `koszty_energii` tworzy sensory zuzycia energii na podstawie encji licznika (narastajacej).

## Konfiguracja (YAML)

```yaml
sensor:
  - platform: koszty_energii
    source_entity: sensor.twoj_licznik
    name: Koszty Energii
```

Sensory:
- dziennie
- tygodniowo
- miesiecznie
- kwartalnie
- polrocznie
- rocznie
