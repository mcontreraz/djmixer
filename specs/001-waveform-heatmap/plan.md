# Implementation Plan: Waveform Heatmap

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Branch**: `001-waveform-heatmap` | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-waveform-heatmap/spec.md`

## Summary

Picos y colores reales por tema, calculados en un worker fuera de los hilos de
audio/UI, cacheados en disco y dibujados por `WaveformView` (overview + grandes).
Sin dependencias nuevas: decode con miniaudio (ya vendorizado) y bandas
espectrales con banco de filtros biquad propio.

## Technical Context

**Language/Version**: C++17 + QML (Qt 6.5+)

**Primary Dependencies**: Qt6 Quick/QuickDialogs2, miniaudio (`third_party/` (no publicado), existente).
Sin FFT externa: banco de 3 biquads (lowpass 250 Hz / bandpass / highpass 4 kHz)
para energía por banda. Essentia/aubio quedan para beatgrid (otra feature).

**Storage**: sidecars binarios versionados en `QStandardPaths::CacheLocation`
(`waveforms/v1/<sha1(ruta+tamaño+mtime)>.wfcache`). Sin SQLite (evita módulo QtSql).

**Testing**: `DJMIXER_AUTOTEST` (cadena audio) + `DJMIXER_SCREENSHOT` (verificación
visual de overview real vs simulado) + asserts de determinismo (mismo archivo =
mismos bytes de caché).

**Target Platform**: macOS arm64, app Qt bundle.

**Project Type**: desktop-app (Qt Quick).

**Performance Goals**: análisis ≤3× duración del tema en decode (típico: WAV 45 MB
en <10 s); UI responde <200 ms durante análisis; recarga cacheada <300 ms.

**Constraints**: Constitución I (nada bloqueante en `render()` ni en hilo UI);
TCC: el worker solo lee archivos que la app ya puede leer; cancelación por
contador generacional por deck.

**Scale/Scope**: 67–9000 temas en librería; caché acotada con LRU simple por
fecha (techo 500 MB, limpieza al arrancar).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Audio-Thread Safety**: PASS — el worker es un tercer hilo (ni UI ni audio);
  el deck solo recibe el caché terminado por señal queued. `render()` no se toca.
- **II. Verification by Execution**: PASS — quickstart define autotest + captura.
- **III. Clean-Room**: PASS — algoritmo propio (picos + biquads); paleta inspirada en
  Serato, ningún asset suyo.
- **IV. Simplicity**: PASS — cero dependencias nuevas; sidecar binario en vez de
  SQLite; FFT externa descartada para F2.
- **V. Bilingual Clarity**: PASS — código inglés, docs/especificación español.

## Project Structure

### Documentation (this feature)

```text
specs/001-waveform-heatmap/
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
├── waveformcache.h/.cpp   # Entidad + lector/escritor de sidecar (hilo worker)
├── waveformanalyzer.h/.cpp# Worker: decode miniaudio + picos + biquads + colores
├── deck.h/.cpp            # Expone cache lista (propiedad + señal), cancela por generación
├── tracklistmodel.h/.cpp  # (sin cambios en F2; la caché vive por archivo, no por fila)
├── components/
│   └── WaveformView.qml   # Dibuja buckets reales; fallback a vacío (NO simulado)
└── main.cpp               # Registra tipos + extiende autotest (caché determinista)

resources.qrc               # (sin cambios: no hay assets nuevos)
```

## Phases

### Phase 0: Outline & Research → [research.md](research.md)

### Phase 1: Design & Contracts → [data-model.md](data-model.md), [contracts/](contracts), [quickstart.md](quickstart.md)
