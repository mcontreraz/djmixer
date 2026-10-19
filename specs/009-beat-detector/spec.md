# Feature Specification: Real-time Beat Detector + Zapateo

**Feature Branch**: `009-beat-detector`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "el motor debe detectar el desfase (zapateo) entre 2
canciones; hoy la app no tiene un beat detector en tiempo real"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Detector de beats en tiempo real (Priority: P1)

Cada deck detecta sus propios beats **mientras suena**, sin análisis previo ni
grid. Detecta los golpes (onsets de graves) en el stream de audio y expone la
posición del último beat.

**Why this priority**: Es la base. Sin beats detectados no se puede medir el
zapateo; y el detector offline (`detectTempo`) corre una sola vez, no sirve
para comparar dos señales en vivo.

**Independent Test**: Reproducir un track con BPM conocido (o el WAV de
prueba) → el intervalo medio entre beats detectados ≈ `60/BPM` (±5%).

**Acceptance Scenarios**:

1. **Given** un deck sonando, **When** se reproduce, **Then** `lastBeatPosition` avanza con cada golpe (no queda fijo ni salta a lo loco).
2. **Given** un track a 120 BPM, **When** se mide el intervalo medio entre beats, **Then** ≈ 0.5 s (±5%).
3. **Given** silencio/cola sin golpes, **When** no hay onsets, **Then** no se emiten beats falsos.

---

### User Story 2 - Detección de zapateo entre 2 decks (Priority: P2)

Con dos decks sonando, se mide el **desfase real** entre sus beats detectados:
la diferencia de tiempo entre el beat de A y el beat más cercano de B, envuelta
a medio período. Es el "zapateo" audible (golpe doble) cuando no están al
compás.

**Why this priority**: Es el objetivo del feature: confirmar con la señal (no
solo con la grid) si dos canciones están o no alineadas.

**Independent Test**: Dos decks al mismo BPM, B adelantado 120 ms → el medidor
lee ~120 ms; alineados → ~0 ms.

**Acceptance Scenarios**:

1. **Given** dos decks con beats detectados, **When** están alineados, **Then** el desfase es ~0 ms (±30 ms).
2. **Given** B adelantado X ms (mismo BPM), **When** se mide, **Then** el desfase ≈ X ms.
3. **Given** BPM distintos (120 vs 128), **When** se mide, **Then** el desfase varía (señal de que no están sincronizados).

---

### User Story 3 - Medidor de zapateo en la UI (Priority: P3)

Un indicador visual muestra el desfase (ms) y si está "al compás" o "zapateo"
(fuera de tolerancia). Se integra al SyncLab (y/o al deck) para ver el
resultado real, no solo el de la grid.

**Why this priority**: Hace visible el feature; sin visual no hay forma de
verificarlo a ojo.

**Independent Test**: Captura con dos decks desfasados → el medidor muestra un
offset no nulo y el estado "zapateo".

**Acceptance Scenarios**:

1. **Given** desfase > umbral, **When** se observa el medidor, **Then** muestra offset y estado "zapateo".
2. **Given** alineados, **When** se observa, **Then** estado "al compás".

---

### Edge Cases

- ¿Track sin transientes claros (pads/voces)? → detector se calla (umbral adaptativo) y el medidor muestra "sin beat".
- ¿Un deck en pausa? → no hay beats nuevos; el comparador congela o marca inválido.
- ¿BPM en octava (70 vs 140)? → el comparador usa el período del deck de referencia (o el menor) para envolver; documentar elección.
- ¿Clicks/spikes? → refractory (mínimo entre beats) evita dobles detecciones.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST detectar beats en tiempo real (streaming por buffer) usando la envolvente de onsets de graves, sin análisis previo de la pista completa.
- **FR-002**: El detector MUST correr sin bloquear el hilo de audio: O(1) por frame, sin `new`/mutex/I-O (Constitución I).
- **FR-003**: Cada deck MUST exponer la posición del último beat detectado (tiempo de fuente, en segundos).
- **FR-004**: El sistema MUST calcular el desfase entre dos decks: `|beatA − beatB|` envuelto a `[−período/2, +período/2)`, en ms.
- **FR-005**: El sistema MUST clasificar el estado "al compás" vs "zapateo" con un umbral configurable.
- **FR-006**: El medidor MUST funcionar independientemente de la beatgrid (usa la señal, no el grid).

### Key Entities

- **BeatDetector** (por deck): envolvente de onsets (bajos), umbral adaptativo, refractory, `lastBeatPosition` atómico.
- **PhaseMeter** (comparador): dado dos `BeatDetector`, produce `offsetMs` y `state {in-sync, zapateo, no-beat}`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Intervalo medio de beats detectados a BPM conocido dentro de ±5%.
- **SC-002**: Dos señales desfasadas X ms se leen ~X ms (error < ±30 ms); alineadas ~0 ms.
- **SC-003**: El autotest de audio existente sigue en verde (el detector no rompe `render()`).
- **SC-004**: Captura con zapateo muestra el offset y el estado correcto.

## Assumptions

- Señales con golpes claros (dance/electrónica); transientes débiles = "sin beat" aceptable.
- El detector de onsets reutiliza el flujo de graves de `waveformanalyzer.cpp` (clean-room, no aubio).
- El período de referencia para envolver es el del deck maestro (o el de mayor confianza); F1 usa un período fijo por deck.
- Sin dependencias nuevas (Constitución IV): no entra aubio/SoundTouch.
