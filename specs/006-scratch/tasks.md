# Tasks: Scratch

**Input**: Design documents from `/specs/006-scratch/`

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Motor bidireccional (US1)

**Goal**: Render con tasa con signo + historial + spin

- [X] T001 Historial 262144 frames en `discardConsumed` (`src/deck.cpp`)
- [X] T002 Rama scratch/spin en `render()` + helper de rango bidireccional (`src/deck.cpp`)
- [X] T003 Estado y slots `scratchGrab/scratchTo/scratchRelease` + cancelación en cue/jump (`src/deck.h/.cpp`)

## Phase 2: Gestos (US1+US2)

**Goal**: Drag en waveform y plato, spin al soltar

- [X] T004 Drag→scratch en `waveTop/waveBottom` (`src/Main.qml`), click intacto
- [X] T005 Drag angular + velocidad en `JogWheel`/`src/DeckPanel.qml` (1 vuelta = 2 s)
- [X] T006 Autotest en `src/main.cpp`: ida/vuelta/spin/resume programático

## Phase 3: Evidencia

- [X] T007 Captura con scratch (forma desplazada + tick movido) + reabrir app

## Dependencies & Execution Order

T001 → T002 → T003 → T004/T005 (QML en paralelo) → T006 → T007.
