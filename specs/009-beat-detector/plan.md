# Implementation Plan: Real-time Beat Detector + Zapateo

**Branch**: `009-beat-detector` | **Date**: 2026-10-14 | **Spec**: [spec.md](./spec.md)

## Summary

Un `BeatDetector` por deck detecta onsets (flujo de energía de graves) en
tiempo real dentro de `Deck::render()`, sin asignar ni bloquear. Expone
`lastBeatPosition` (atómico). Un `PhaseMeter` compara los beats de dos decks y
reporta el **zapateo** (desfase) en ms, independiente de la beatgrid.

## Technical Context

**Language/Version**: C++17 + Qt 6.5 (QML). Sin dependencias nuevas.

**Primary Dependencies**: miniaudio (ya en `third_party/`) para el audio; el
detector es aritmética simple sobre el buffer mono/mezclado.

**Storage**: nada persistente; el detector es estado volátil por deck.

**Testing**: autotest de audio existente (regresión) + fixture sintético de
clicks para verificar intervalo de beats. Captura de UI para el medidor.

**Target Platform**: macOS arm64, app Qt bundle.

**Performance Goals**: O(1) por frame de audio (un lowpass + flujo + peak); el
medidor corre en el hilo UI (QTimer ~50 ms).

**Constraints**: Constitución I (nada bloqueante en `render()`: solo atómicos y
buffers de tamaño fijo); III (clean-room); IV (sin deps).

**Scale/Scope**: 2 decks. No BPM real-time (eso sigue siendo offline); solo
detección de beats + desfase.

## Constitution Check

- **I. Audio-Thread Safety**: PASS — `BeatDetector` usa un buffer circular fijo,
  atomics y sin `new`/mutex en `render()`.
- **II. Verification by Execution**: PASS — quickstart define fixture de clicks
  + captura del medidor.
- **III. Clean-Room**: PASS — envolvente propia (reutiliza `waveformanalyzer`),
  no copia DSP de Serato/aubio.
- **IV. Simplicity**: PASS — un detector por deck, sin capas extra.
- **V. Bilingual Clarity**: PASS — código inglés, docs español.

## Project Structure

```text
specs/009-beat-detector/
├── plan.md, research.md, data-model.md, quickstart.md, tasks.md
├── contracts/beat-detector.md
└── checklists/requirements.md

src/
├── beatdetector.h/.cpp   # BeatDetector (por deck) + PhaseMeter
├── deck.h/.cpp           # instancia el detector y lo alimenta en render()
├── synclab.h/.cpp        # (opcional) expone offsetMs para el visor
├── SyncLabView.qml       # medidor de zapateo
└── main.cpp              # cablea si hace falta
```

## Phases

- Phase 0: research (onsets en tiempo real, umbral adaptativo, refractory)
- Phase 1: data-model + contracts + quickstart
- Phase 2: tasks (implementación)

## Riesgos y decisiones abiertas

1. **Falsos beats** con transientes débiles → umbral adaptativo + refractory
   (mínimo 200 ms entre beats). Se calibra con el fixture de clicks.
2. **Período de envoltura** para el zapateo: F1 usa el período del deck A
   (maestro). En octava (70/140) el offset se lee a medio período; documentado.
3. **Latencia**: el beat se detecta en el hop (~10 ms); el desfase medido tiene
   ese jitter. Tolerancia del test ±30 ms.
