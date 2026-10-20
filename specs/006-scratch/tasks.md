# Tasks: Scratch

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Input**: Design documents from `/specs/006-scratch/`

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Motor bidireccional (US1)

**Goal**: Render con tasa con signo + historial + spin

- [X] T001 Historial 262144 frames en `discardConsumed` (`deck.cpp` (no publicado))
- [X] T002 Rama scratch/spin en `render()` + helper de rango bidireccional (`deck.cpp` (no publicado))
- [X] T003 Estado y slots `scratchGrab/scratchTo/scratchRelease` + cancelación en cue/jump (`deck.h/.cpp` (no publicado))

## Phase 2: Gestos (US1+US2)

**Goal**: Drag en waveform y plato, spin al soltar

- [X] T004 Drag→scratch en `waveTop/waveBottom` (`Main.qml` (no publicado)), click intacto
- [X] T005 Drag angular + velocidad en `JogWheel`/`DeckPanel.qml` (no publicado) (1 vuelta = 2 s)
- [X] T006 Autotest en `main.cpp` (no publicado): ida/vuelta/spin/resume programático

## Phase 3: Evidencia

- [X] T007 Captura con scratch (forma desplazada + tick movido) + reabrir app

## Dependencies & Execution Order

T001 → T002 → T003 → T004/T005 (QML en paralelo) → T006 → T007.
