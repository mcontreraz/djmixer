# Tasks: Real-time Beat Detector + Zapateo

**Input**: spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md

## Fase 1: Detector

- [ ] T001 `src/beatdetector.h/.cpp`: `BeatDetector` (lowpass, hop, flujo, umbral adaptativo, refractory, `lastBeatPosition` atómico)
- [ ] T002 `Deck`: instanciar `BeatDetector` y alimentarlo en `render()` (suma mono del buffer)
- [ ] T003 Exponer `Deck::lastBeatPosition()` y `Q_PROPERTY`

## Fase 2: Zapateo

- [ ] T004 `PhaseMeter` en `beatdetector.h/.cpp`: `offsetMs()` + `state()` entre dos detectores
- [ ] T005 Cablear `PhaseMeter` con `DeckA`/`DeckB` (hilo UI, QTimer 50 ms)

## Fase 3: UI

- [ ] T006 Medidor de zapateo en `SyncLabView.qml` (offset ms + estado al-compás/zapateo)
- [ ] T007 (opcional) indicador en el deck/GlobalBar

## Fase 4: Verificación

- [ ] T008 Fixture de clicks 120 BPM → intervalo de beats ≈ 0.5 s (SC-001)
- [ ] T009 Autotest de audio verde (SC-003) + captura del medidor (SC-004)

**Orden**: T001→T002→T003→T004→T005→T006→T008→T009. T007 paralelo tras T006.
