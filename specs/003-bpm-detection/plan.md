# Implementation Plan: BPM Detection

**Branch**: `003-bpm-detection` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-bpm-detection/spec.md`.

## Summary

Detección de tempo **en una sola pasada** (el mismo decode del worker F2), emitiendo **nodos** de
onset de forma streaming: el bucle de decode acumula un envolvente de onsets (energía de graves +
flujo positivo) y, al terminar, una **autocorrelación** lo convierte en BPM + `beats[]`. El
resultado puebla el `BeatGrid` que ya existe (`src/beatgrid.h`) y se cachea en el sidecar v5 ya
integrado. Cero dependencias nuevas, cero segundo decode.

## Technical Context

**Language/Version**: C++17 + QML (Qt 6.5+)

**Primary Dependencies**: Qt6 Quick/QuickDialogs2, miniaudio (existente), **TagLib** (nueva, para
metadata de tags). **Sin FFT/aubio**: BPM por autocorrelación del envolvente de onsets; onsets por
energía del lowpass 250 Hz (biquad ya existente en `waveformanalyzer.cpp`) + flujo positivo.

**Storage**: reutiliza el sidecar v5 `waveforms/v1/<sha1>.wfcache` (ya guarda `BeatGrid`), misma
clave `sha1(ruta|tamaño|mtime)`. Sin sidecar nuevo.

**Testing**: `DJMIXER_AUTOTEST` (determinismo de BPM + `beats[]` equidistante + `valid` en
corrupción) + `DJMIXER_SCREENSHOT` (el BPM real sustituye al texto fijo en pantalla).

**Target Platform**: macOS arm64, app Qt bundle.

**Project Type**: desktop-app (Qt Quick).

**Performance Goals**: overhead del tempo < 5% sobre el análisis F2 (autocorrelación sobre
~7000 frames es O(n·k), trivial); recarga cacheada < 300 ms; UI responde < 200 ms.

**Constraints**: Constitución I (worker, sin tocar `render()`); III (clean-room: autocorrelación
propia); IV (una pasada, sin deps).

**Scale/Scope**: 2 decks; un `BeatGrid` por archivo. Beat sync (alineación) es la feature
siguiente (`004-beat-sync`), no parte de esta.

## Constitution Check

*GATE: Must pass before Phase 0 research.*

- **I. Audio-Thread Safety**: PASS — todo corre en el worker existente; `render()` y el hilo UI
  no se tocan. El BeatGrid vuelve por señal queued.
- **II. Verification by Execution**: PASS — autotest (BPM determinista + equidistancia de beats +
  degradación) y captura.
- **III. Clean-Room**: PASS — onsets + autocorrelación propios; el decompilado de Serato solo
  informa *qué* (BPM + beats + octava), no *cómo*.
- **IV. Simplicity**: PASS — BPM sin dependencias (autocorrelación). **TagLib es la única dep nueva**
  y se justifica: leer título/artista/key de tags ID3/FLAC a mano es frágil (muchos frame types);
  TagLib es el estándar maduro para esto. Reusa biquad, worker y sidecar v5.
- **V. Bilingual Clarity**: PASS — código inglés, docs español.

## Project Structure

### Documentation (this feature)

```text
specs/003-bpm-detection/
├── plan.md              # This file
├── research.md          # Phase 0 (onsets/autocorr, plegado de octava, fase)
├── data-model.md        # Phase 1 (BeatGrid ya existe; contrato deck→QML)
├── quickstart.md        # Phase 1 (validación punta a punta)
├── contracts/           # Phase 1 (QML ⟷ C++)
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── beatgrid.h           # Ya existe: BeatGrid (bpm, beats[], downbeat, phaseAt)
├── waveformanalyzer.cpp # ★ Extiende el decode F2: acumula onsets + autocorrelación → BeatGrid
├── waveformcache.h/.cpp # Sin cambios (v5 ya guarda/lee BeatGrid)
├── deck.h/.cpp          # Expone beatGrid a QML (propiedad + señal waveformChanged)
├── components/
│   └── (display BPM real en el deck en vez del texto fijo)
└── main.cpp             # Autotest: determinismo BPM + equidistancia beats + degradación

CMakeLists.txt           # sin cambios (no hay archivos nuevos)
```

## Phases

### Phase 0: Outline & Research → [research.md](./research.md)

Decisiones: función de onset (graves + flujo), autocorrelación + rango 70–180 + plegado de octava,
cálculo de fase (offset que maximiza energía de onsets), integración "una pasada y nodos".

### Phase 1: Design & Contracts → [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

### Phase 2: Tasks → [tasks.md](./tasks.md)

## Riesgos y decisiones abiertas

1. **Plegado de octava**: la autocorrelación puede piquear en el doble/mitad. Se evalúa el pico y
   sus octavas (±1) y se elige el de mayor autocorrelación. Cubre el caso 70/140 (SC/FR-004).
2. **Precisión estricta del BPM**: la autocorrelación por lag entero da pasos de ~2-3 BPM. Para el
   ±0.5 BPM (SC-002) se hace **interpolación parabólica** del pico de autocorrelación (sub-lag).
2. **Cambios de tempo / breakdowns**: la autocorrelación global devuelve el tempo dominante.
   Documentado como limitación (no bloquea el MVP).
3. **Downbeat musical**: se aproxima al primer onset fuerte; la detección armónica real queda en
   F3b (fuera de alcance).
4. **Key**: en este incremento se lee de **tags** (TagLib); la detección armónica (chroma/Camelot)
   es una feature aparte. Sin tag → "—". El mapeo Camelot→color se hardcodea (24 claves).
5. **`beats[]` en memoria**: ~4 beats/s × duración → para 1 h son ~14k doubles (~112 KB). Aceptable;
   el sidecar v5 ya lo serializa.
