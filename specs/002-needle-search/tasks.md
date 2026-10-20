# Tasks: Needle Search

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Input**: Design documents from `/specs/002-needle-search/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Sin setup (cero archivos nuevos, cero dependencias)

- [X] T001 Verificar que `Deck::seek` existe y es slot (lectura `deck.h` (no publicado))

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Sin fundación (el motor ya expone todo)

**Checkpoint**: Foundation ready - no blocking work needed

## Phase 3: User Story 1 - Click en overview (Priority: P1) 🎯 MVP

**Goal**: Click en overview salta a ese punto del tema

**Independent Test**: Click al 50% → posición en 48–52% (jog + playhead)

- [X] T002 [US1] `MouseArea` click→`seek` en overview de `DeckPanel.qml` (no publicado)
- [X] T003 [US1] Verificar con captura: playhead salta al punto clickeado

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

## Phase 4: User Story 2 - Click en grande (Priority: P2)

**Goal**: Click en waveform con scroll salta al tiempo visible

**Independent Test**: Click al borde derecho sonando → salto al tiempo visible

- [X] T004 [US2] `MouseArea` click→`seek` con fórmula scroll en `waveTop`/`waveBottom` de `Main.qml` (no publicado)
- [X] T005 [US2] Ignorar clicks fuera de `[0, duration]` (rama `return` en el handler)

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Evidencia automática

- [X] T006 Extender autotest en `main.cpp` (no publicado): `seek(50%)` + assert posición 48–52%
- [X] T007 Captura final + reabrir app

## Dependencies & Execution Order

T001 → T002 → T003 → T004 (+T005 mismo bloque) → T006 → T007. Todo secuencial (mismos archivos QML salvo T006).

## Implementation Strategy

MVP = T001–T003 (overview). Luego grandes (T004–T005) y evidencia (T006–T007).
