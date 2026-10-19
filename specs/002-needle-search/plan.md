# Implementation Plan: Needle Search

**Branch**: `002-needle-search` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-needle-search/spec.md`

## Summary

Click en overview y waveforms grandes salta a ese punto vía el `Deck::seek()`
existente (thread-safe, preserva play/pausa). Cero cambios en el motor.

## Technical Context

**Language/Version**: C++17 + QML (Qt 6.5+)

**Primary Dependencies**: ninguna nueva (Qt Quick existente).

**Storage**: N/A.

**Testing**: autotest extendido (seek programático + verificación de posición) + captura.

**Target Platform**: macOS arm64.

**Project Type**: desktop-app (Qt Quick).

**Performance Goals**: el salto responde en <200 ms tras el click.

**Constraints**: Constitución I (seek ya es atómico, sin tocar); no auto-play/stop.

**Scale/Scope**: 2 vistas (overview por deck + 2 grandes con scroll).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Audio-Thread Safety**: PASS — solo se llama al slot `seek()` existente.
- **II. Verification by Execution**: PASS — autotest + captura.
- **III. Clean-Room**: PASS — gesto estándar, código propio.
- **IV. Simplicity**: PASS — ~15 líneas QML, sin C++ nuevo.
- **V. Bilingual Clarity**: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/002-needle-search/
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
├── DeckPanel.qml            # MouseArea click→seek en overview
├── Main.qml                 # MouseArea click→seek en waveTop/waveBottom
└── main.cpp                 # autotest: seek al 50% y verifica posición
```

## Phases

### Phase 0: Outline & Research → [research.md](./research.md)

### Phase 1: Design & Contracts → [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)
