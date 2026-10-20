# Implementation Plan: Scratch

**Branch**: `006-scratch` | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-scratch/spec.md`

## Summary

Scratch vinílico: rama de render con tasa con signo (adelante/atrás) gobernada
por la mano, historial de ~5 s para reversa sin re-seek, spin con decaimiento
al soltar, y gestos en waveform (drag→tiempo) y plato (ángulo→tiempo).

## Technical Context

**Language/Version**: C++17 + QML (Qt 6.5+)

**Primary Dependencies**: ninguna nueva.

**Storage**: N/A (el historial vive en `m_src` existente, con margen ampliado).

**Testing**: autotest (scratch adelante/atrás programático, spin, resume) + captura.

**Target Platform**: macOS arm64.

**Project Type**: desktop-app (Qt Quick).

**Performance Goals**: gestos a 60 Hz sin clicks nuevos; re-seek solo fuera del historial.

**Constraints**: Constitución I (todo el estado compartido UI→audio por atómicos;
el worker de análisis no se toca); seek existente intacto para needle.

**Scale/Scope**: 2 decks independientes; sin DVS/hardware.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Audio-Thread Safety**: PASS — `grabbed/handPos/spinVel` atómicos; el render solo lee; historial acotado (5.5 s ≈ 2 MB/deck).
- **II. Verification by Execution**: PASS — autotest de ida/vuelta/spin + captura.
- **III. Clean-Room**: PASS — física DJ estándar; de la referencia solo consta que no hay intel de scratch (nombres Slip/ScratchBank).
- **IV. Simplicity**: PASS — una rama más en `render()` + helper de rango; sin libs.
- **V. Bilingual Clarity**: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/006-scratch/
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
├── deck.h/.cpp        # ScratchState, renderRange bidireccional, spin, historial 5 s
├── components/
│   └── WaveformView.qml  # drag→scratchTo/scratchRelease (click intacto = needle)
├── DeckPanel.qml      # drag angular en JogWheel (1 vuelta = 2 s)
└── main.cpp           # autotest scratch (ida, vuelta, spin, resume)
```

## Phases

### Phase 0: Outline & Research → [research.md](research.md)

### Phase 1: Design & Contracts → [data-model.md](data-model.md), [contracts/](contracts), [quickstart.md](quickstart.md)
