# Tasks: Sync Engine v2

**Input**: Design documents from `/specs/007-sync-engine-v2/`

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Recalibración (US1)

**Goal**: Corrector con bandas verificadas, fuera el umbral-sin-fuente

- [X] T001 Reemplazar ganancias por bandas 0.01/0.2/±5%/delta 0.02, k=0.7 en `src/syncengine.cpp` (citar `Mixxx bpmcontrol.cpp`)
- [X] T002 Eliminar toda mención al umbral-sin-fuente en código y docs (grep de verificación)
- [X] T003 Excluir scratch/spin del sync de seguidores en `src/syncengine.cpp`

## Phase 2: Enganche + gates (US2+US3)

**Goal**: Beat-match seek, quantize gate, user offset

- [X] T004 Beat-match seek al enganchar con regla 1/8 usando `BeatGrid` en `src/syncengine.cpp`
- [X] T005 Gatear fase por quantize + cablear pill Q en `src/DeckPanel.qml`
- [X] T006 Absorber bend manual como offset en `src/syncengine.cpp`

## Phase 3: Métricas (US4)

**Goal**: Convergencia medible en autotest

- [X] T007 Escenario de convergencia en `src/main.cpp`: lockMs/phaseErr con umbrales 4000 ms/0.02
- [X] T008 Captura + reabrir app

## Dependencies & Execution Order

T001 → T002 (grep) → T003 → T004 → T005 → T006 → T007 → T008. Secuencial (mismo motor).
