# Tasks: Cue Points (CDJ) + Hot Cues

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Input**: Design documents from `/specs/005-cue-points/`

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Motor Deck (US1+US2)

**Goal**: Semántica CDJ + persistencia en el motor

- [X] T001 Estado cue en `deck.h` (no publicado) (pos, válido, preview, `hotCues[8]`, props + señales)
- [X] T002 Slots `cuePressed/cueReleased` + hot cues (`set/clear/jump`) en `deck.cpp` (no publicado)
- [X] T003 Sidecars `.cuepoint`/`.hotcues` (lectura en carga, escritura en set) en `deck.cpp` (no publicado)

## Phase 2: UI (US1+US3+US4)

**Goal**: Botón press/release, marcas y pads funcionales

- [X] T004 Botón CUE redondo a press/release en `DeckPanel.qml` (no publicado)
- [X] T005 Prop `cueTime` + marca en overview y scroll en `components/WaveformView.qml` (no publicado)
- [X] T006 Pasar `cueTime` + `cuePoints` desde decks en `DeckPanel.qml` (no publicado) y `Main.qml` (no publicado)
- [X] T007 Pads hot cue (guardar/saltar/borrar + números) en `DeckPanel.qml` (no publicado)

## Phase 3: Evidencia

- [X] T008 Autotest en `main.cpp` (no publicado): return, preview, persist, hot set/jump/clear
- [X] T009 Captura con cue + pads + reabrir app

## Dependencies & Execution Order

T001 → T002 → T003 → T004/T005/T006/T007 (QML en paralelo conceptual, mismo turno) → T008 → T009.
