# Implementation Plan: Beat Sync

**Branch**: `004-beat-sync` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification + referencias `docs/referencia-serato/beat-sync/` (resumen +
funciones decompiladas de Serato). La detección de BPM (003) ya entrega el `BeatGrid`.

## Summary

Un `SyncEngine` (QObject, hilo UI) mantiene el deck primario y el estado de sync por deck
(`Off/Armed/Tempo/Beat`) y corre un lazo proporcional cada ~50 ms: ajusta el `rate` atómico del
esclavo para igualar el tempo del primario (con octava) y alinea la fase con un PLL proporcional +
nudge de `seek`. Nunca toca el hilo de audio. Clean-room: las ganancias del `SyncLogic` de Serato
no están en las referencias, así que el lazo es nuestro.

## Technical Context

**Language/Version**: C++17 + QML (Qt 6.5+)

**Primary Dependencies**: Qt6 (existente). **Cero dependencias nuevas**: el lazo es aritmética
sencilla sobre `Deck::setPitch` (rate atómico) y `Deck::seek` (seek pendiente).

**Storage**: nada nuevo — consume el `BeatGrid` del sidecar v6 existente.

**Testing**: `DJMIXER_AUTOTEST` (convergencia de fase acotada + octava + restauración de rate) +
`DJMIXER_SCREENSHOT` (visual). El autotest usa el WAV de prueba en ambos decks.

**Target Platform**: macOS arm64, app Qt bundle.

**Project Type**: desktop-app (Qt Quick).

**Performance Goals**: tick de sync O(1) cada 50 ms; converge en < 3 s; UI responde < 200 ms.

**Constraints**: Constitución I (nada bloqueante en `render()`); III (clean-room: el decompilado
informa *comportamiento* —estados, octava, primario—, nunca código copiado); IV (sin deps).

**Scale/Scope**: 2 decks (A/B). Multi-deck y downbeat musical (Smart real) quedan fuera (F4b).

## Constitution Check

- **I. Audio-Thread Safety**: PASS — `SyncEngine` en `QTimer` del hilo UI; solo escribe `rate`
  (atómico, vía `setPitch`) y `seek` (atómico `m_pendingSeek`). `render()` intacto.
- **II. Verification by Execution**: PASS — quickstart define autotest de convergencia + captura.
- **III. Clean-Room**: PASS — PLL propio; estados/octava/primario deducidos del comportamiento.
- **IV. Simplicity**: PASS — sin dependencias nuevas; PLL proporcional, no PID.
- **V. Bilingual Clarity**: PASS — código inglés, docs español.

## Project Structure

### Documentation (this feature)

```text
specs/004-beat-sync/
├── plan.md              # This file
├── research.md          # Phase 0 (PLL, alineación de fase, tempo, octava)
├── data-model.md        # Phase 1 (SyncEngine, estado de sync)
├── quickstart.md        # Phase 1 (validación punta a punta)
├── contracts/           # Phase 1 (QML ⟷ C++)
├── checklists/          # Calidad del spec
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── syncengine.h/.cpp    # SyncEngine: primario, estados, PLL (tempo + fase)
├── deck.h/.cpp          # estado de sync + rate ya atómico (pitch); expone beatGrid
├── components/
│   └── SyncButton.qml   # (o reutiliza el SYNC existente en DeckPanel)
└── main.cpp             # cablea SyncEngine(DeckA, DeckB) + extiende autotest

CMakeLists.txt           # + syncengine.cpp
```

## Phases

### Phase 0: Outline & Research → [research.md](./research.md)

### Phase 1: Design & Contracts → [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

### Phase 2: Tasks → [tasks.md](./tasks.md)

## Riesgos y decisiones abiertas

1. **Ganancias del PLL**: no están en la referencia ("Pendiente" en beat-sync.md). Nuestro lazo
   es proporcional + nudge, calibrado con el autotest de convergencia (SC-001).
2. **Downbeat (Smart)**: MIR difícil; en el MVP `Smart` ≈ `Simple` (fase de beat). F4b.
3. **Fase de beat como referencia**: usamos `BeatGrid.beats[]` + `phaseAt(t)` (ya en `beatgrid.h`)
   para calcular el error de fase en beats; no reanalizamos nada.
