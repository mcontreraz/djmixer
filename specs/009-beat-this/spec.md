# Feature Specification: Beat This! (009)

**Feature Branch**: `009-beat-this`

**Created**: 2026-10-14

**Status**: Complete (2026-10-14)

**Medido**: Mainframe 124.29 (real 124.17); 17/17 sin fallback; autotest
exit=0; sync 120vs126 LOCK 46 ms + hold 25 s exit=0. Notas: BPM nominal con
refinado al 4% (modelos cuantizan: BT frames 20 ms, QM lags enteros);
sesión ORT única fugada a propósito (bug teardown 1.31); harness espera
análisis con deadline en vez de sleeps fijos.

**Input**: "beatsync pro: detector neuronal SOTA (Beat This!, MIT) vía ONNX como primario"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - BPM exacto en temas propios (Priority: P1)

Los 17 wavs de McBaez reportan el BPM de DAW (±0.15) sin corrección manual.

**Independent Test**: batch sobre la carpeta; comparar contra BPMs de DAW conocidos (Mainframe 124.17 medido).

**Acceptance Scenarios**:

1. **Given** Mainframe (124.17 real), **When** se analiza, **Then** BPM ∈ [124.0, 124.35] directo del modelo (sin fusión).
2. **Given** los 17 temas, **When** se analizan, **Then** 0 fallbacks a QM.

---

### User Story 2 - Downbeats reales (Priority: P1)

El downbeat viene del modelo (no de votación por energía): el snap de sync clava compás correcto a la primera.

**Independent Test**: sync 120vs126 con grids Beat This! → eBar ≈ 0 tras el snap sin corrección posterior.

**Acceptance Scenarios**:

1. **Given** dos temas, **When** sync, **Then** lock con downbeats alineados (eBar < 0.02) desde el enganche.

---

### User Story 3 - Sin regresión (Priority: P2)

Si el modelo falla o falta, QM → detector propio (cadena intacta). Sin modelo, la app funciona igual que hoy.

**Acceptance Scenarios**:

1. **Given** modelo ausente, **When** se analiza, **Then** se usa QM sin errores visibles.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST correr `beat_this.onnx` vía ONNX Runtime en el worker (nunca en audio/UI).
- **FR-002**: El wrapper MUST devolver beats + downbeats + beat_counts → `BeatGrid`.
- **FR-003**: Cadena de fallback MUST ser: Serato tag → Beat This! → QM → propio.
- **FR-004**: El modelo (79 MB) MUST vivir en submódulo, no en el repo.
- **FR-005**: Licencias MUST documentarse (MIT: beat_this_cpp, ORT, r8brain; BSD: pocketfft).

### Key Entities

- **BeatThisResult**: beats[], downbeats[], beat_counts[] (segundos).
- **BeatGrid**: sin cambios (beats + bpm mediano + downbeatIdx del primer downbeat).

## Success Criteria *(mandatory)*

- **SC-001**: Mainframe ∈ [124.0, 124.35] directo del modelo.
- **SC-002**: 17/17 temas sin fallback.
- **SC-003**: Autotest + sync 120vs126 verdes (exit=0).
- **SC-004**: Sin modelo presente, comportamiento idéntico al actual.

## Assumptions

- Inferencia offline en worker (segundos por tema, cacheada); no tiempo real.
- Modelo beat_this.onnx tal cual (sin reentrenar).
- Modo Minimal primero; DBN solo si Minimal no cumple SC-001.
