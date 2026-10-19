# Implementation Plan: Sync Engine v2

**Branch**: `007-sync-engine-v2` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-sync-engine-v2/spec.md`

## Summary

Recalibrar el `SyncEngine` mergeado con las bandas Mixxx, sumar beat-match
por seek al enganchar, gatear fase por quantize, absorber bend manual y medir
convergencia. Se elimina el umbral-sin-fuente sin fuente.

## Technical Context

**Language/Version**: C++17 + QML (Qt 6.5+)

**Primary Dependencies**: ninguna nueva.

**Storage**: N/A (estado en memoria; métricas solo en log de test).

**Testing**: autotest con escenario de convergencia (dos decks, desfase conocido).

**Target Platform**: macOS arm64.

**Project Type**: desktop-app (Qt Quick).

**Performance Goals**: lock <4 s; corrector corriendo en timer UI 50 ms (fuera del hilo de audio, como hoy).

**Constraints**: Constitución I (el corrector ajusta `rate` vía slots, nunca toca `render()`); clean-room (reimplementar, no pegar Mixxx GPL).

**Scale/Scope**: 2 decks; 4 decks y BPM Transition siguen fuera.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Audio-Thread Safety**: PASS — corrector en timer UI, actúa por `setPitch`/`seek`.
- **II. Verification by Execution**: PASS — métricas lockMs/phaseErr en autotest.
- **III. Clean-Room**: PASS — constantes e ideas, código propio; citar orígenes en comentarios.
- **IV. Simplicity**: PASS — recalibración sobre el motor existente.
- **V. Bilingual Clarity**: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/007-sync-engine-v2/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── syncengine.h/.cpp  # recalibrar bandas, beat-match seek, gate quantize, user offset, métricas
├── DeckPanel.qml      # pill Q cableado a quantize del sync (si no lo está)
└── main.cpp           # escenario de convergencia en autotest
```

## Phases

### Phase 0: Outline & Research → [research.md](./research.md)

### Phase 1: Design & Contracts → [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)
