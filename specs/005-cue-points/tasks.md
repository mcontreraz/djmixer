# Tasks: Cue Points (CDJ) + Hot Cues

**Input**: Design documents from `/specs/005-cue-points/`

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Motor Deck (US1+US2)

**Goal**: Semántica CDJ + persistencia en el motor

- [X] T001 Estado cue en `src/deck.h` (pos, válido, preview, `hotCues[8]`, props + señales)
- [X] T002 Slots `cuePressed/cueReleased` + hot cues (`set/clear/jump`) en `src/deck.cpp`
- [X] T003 Sidecars `.cuepoint`/`.hotcues` (lectura en carga, escritura en set) en `src/deck.cpp`

## Phase 2: UI (US1+US3+US4)

**Goal**: Botón press/release, marcas y pads funcionales

- [X] T004 Botón CUE redondo a press/release en `src/DeckPanel.qml`
- [X] T005 Prop `cueTime` + marca en overview y scroll en `src/components/WaveformView.qml`
- [X] T006 Pasar `cueTime` + `cuePoints` desde decks en `src/DeckPanel.qml` y `src/Main.qml`
- [X] T007 Pads hot cue (guardar/saltar/borrar + números) en `src/DeckPanel.qml`

## Phase 3: Evidencia

- [X] T008 Autotest en `src/main.cpp`: return, preview, persist, hot set/jump/clear
- [X] T009 Captura con cue + pads + reabrir app

## Dependencies & Execution Order

T001 → T002 → T003 → T004/T005/T006/T007 (QML en paralelo conceptual, mismo turno) → T008 → T009.
