# Implementation Plan: Cue Points (CDJ)

**Branch**: `005-cue-points` | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-cue-points/spec.md`

## Summary

Semántica CDJ sobre el motor existente: `Deck` guarda un cue (segundos +
válido), preview con press/release, persistencia en sidecar `.cuepoint` y
marca visual en overview + grandes. Sin cambios al path de audio.

## Technical Context

**Language/Version**: C++17 + QML (Qt 6.5+)

**Primary Dependencies**: ninguna nueva.

**Storage**: sidecar `<CacheLocation>/waveforms/v1/<clave>.cuepoint` (texto,
segundos en double); misma clave/invalidez que `.wfcache`.

**Testing**: autotest (return-to-cue, persistencia, preview temporizado) +
captura (marca visual).

**Target Platform**: macOS arm64.

**Project Type**: desktop-app (Qt Quick).

**Performance Goals**: return-to-cue <100 ms de audio; preview arranca <200 ms.

**Constraints**: Constitución I (preview = play/pause/seek existentes, sin tocar
`render()`); el release fuera del botón también vuelve (MouseArea + `containsMouse` no basta: usar `onReleased` global del botón + `onCanceled`).

**Scale/Scope**: un cue por deck; hot-cues fuera (M4).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Audio-Thread Safety**: PASS — preview reusa `play()/pause()/seek()`.
- **II. Verification by Execution**: PASS — autotest + captura con marca.
- **III. Clean-Room**: PASS — semántica CDJ estándar, código propio.
- **IV. Simplicity**: PASS — un double persistido, sin DB nueva.
- **V. Bilingual Clarity**: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/005-cue-points/
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
├── deck.h/.cpp        # estado cue + preview + hotCues[8] + sidecars
├── DeckPanel.qml      # botón CUE press/release + pads hot cue
├── Main.qml           # (sin cambios: las grandes leen la marca del deck)
└── components/
    └── WaveformView.qml  # prop cueTime + cuePoints: marcas fijas
└── main.cpp           # autotest cue (return, preview, persist, hot, marca)
```

## Phases

### Phase 0: Outline & Research → [research.md](research.md)

### Phase 1: Design & Contracts → [data-model.md](data-model.md), [contracts/](contracts), [quickstart.md](quickstart.md)
