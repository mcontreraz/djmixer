# Implementation Plan: Serato Grid Import

**Branch**: `008-serato-grid-import` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-serato-grid-import/spec.md`

## Summary

Parser propio del payload BeatGrid v1 (MP3 GEOB + átomo MP4) que puebla
nuestro `BeatGrid` (beats, bpm, downbeat, locked, source); la detección
actual queda como fallback intacto.

## Technical Context

**Language/Version**: C++17 + Qt 6.5 (TagLib ya linkeado para leer frames/átomos)

**Primary Dependencies**: ninguna nueva (TagLib lee GEOB y MP4 freeform).

**Storage**: sin sidecar nuevo (el `BeatGrid` ya persiste en `.wfcache` v7; suma `locked`+`source` con bump a v8).

**Testing**: fixtures de `replica/beatgrid-datos/` (ground truth) + autotest con MP3 tageado.

**Target Platform**: macOS arm64.

**Project Type**: desktop-app (Qt Quick).

**Performance Goals**: parseo <50 ms por archivo (solo cabeceras/tags, sin decode).

**Constraints**: Constitución I (parseo en worker, ya existe el hilo) y III (parser escrito desde `serializer-v1.md`, verificado contra `beatgrid_blob.py`, sin copiar binario).

**Scale/Scope**: MP3 + M4A lectura; sin escritura de tags; sin DB opaca.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Audio-Thread Safety**: PASS — parseo en worker de análisis.
- **II. Verification by Execution**: PASS — fixtures + autotest con MP3 real.
- **III. Clean-Room**: PASS — implementación desde spec de formato + contraste Mixxx.
- **IV. Simplicity**: PASS — un parser (~150 líneas), sin DB.
- **V. Bilingual Clarity**: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/008-serato-grid-import/
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
├── seratogrid.h/.cpp      # NUEVO: parser v1 (GEOB + MP4) → BeatGrid
├── waveformanalyzer.cpp   # intentar import antes de detectar
├── waveformcache.h/.cpp   # v8: locked + source en sidecar
├── deck.h/.cpp            # exponer gridSource (solo lectura QML)
└── main.cpp               # autotest: fixture + MP3 tageado
```

## Phases

### Phase 0: Outline & Research → [research.md](./research.md)

### Phase 1: Design & Contracts → [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)
