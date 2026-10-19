# Tasks: Beat Sync

**Input**: spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md

## Fase 1: Setup

- [ ] T001 Agregar `syncengine.cpp/.h` a `CMakeLists.txt`

## Fase 2: SyncEngine (foundation)

- [ ] T002 Definir `SyncState`/`SyncMode` y el esqueleto de `SyncEngine` (QObject, QTimer 50 ms)
- [ ] T003 `setSync(deck, on)`: máquina de estados `Off/Armed/Tempo/Beat` + elección de primario
- [ ] T004 `tick()`: Tempo Sync — rate = primaryEffectiveBpm / slaveBpm con plegado de octava
- [ ] T005 `tick()`: Beat Sync — PLL proporcional + nudge (`phaseAt`, `kp` calibrado)
- [ ] T006 Desactivar → restaurar rate manual (capturar al activar)

## Fase 3: Wiring

- [ ] T007 Cablear `SyncEngine(DeckA, DeckB)` en `main.cpp` + exponer a QML
- [ ] T008 Conectar el botón SYNC de `DeckPanel` al `SyncEngine` (modo global + estado por deck)

## Fase 4: Autotest

- [ ] T009 Autotest: convergencia de fase acotada (dos decks, mismo WAV, fases distintas)
- [ ] T010 Autotest: octava 70/140 → tempo correcto
- [ ] T011 Autotest: desactivar restaura rate; deck sin grid → solo tempo (no crash)

## Fase 5: Polish

- [ ] T012 Ejecutar las 5 validaciones de `quickstart.md` + captura
- [ ] T013 Actualizar `README.md` (hito beat sync)

**Orden**: T001 → T002→T003→T004→T005→T006 (secuencial); T009–T011 en paralelo tras T006.
