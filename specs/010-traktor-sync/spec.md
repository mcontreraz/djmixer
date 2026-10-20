# Feature Specification: Traktor-parity Sync (010)

**Feature Branch**: `010-traktor-sync`

**Created**: 2026-10-14

**Status**: Draft

**Input**: "beatsync pro como Traktor: MasterClock explícito + pipeline de
detección por etapas, reimplementado clean-room (Traktor es propietario;
GPL no ampara copiarlo)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Maestro explícito (Priority: P1)

Veo qué deck manda (badge MASTER), lo fijo con un botón, y el sync sigue
al maestro en ambas direcciones sin flips sorpresa.

**Independent Test**: A→B y B→A con takeover + pausa-del-maestro (flip) en
autotest, todo exit=0.

**Acceptance Scenarios**:

1. **Given** A sonando, **When** SYNC en B, **Then** B sigue a A.
2. **Given** ambos con sync, **When** pauso al maestro, **Then** el otro toma el mando sin cazar.
3. **Given** botón MASTER en B, **When** lo pulso, **Then** B manda aunque A haya enganchado primero.

---

### User Story 2 - Detección por etapas (Priority: P2)

Temas difíciles (breaks, groove con swing, intros suaves) reportan BPM
correcto donde el detector actual falla.

**Independent Test**: set de temas conflictivos + BPMs DAW; el histograma
+ coherencia aciertan donde autocorrelación sola erraba.

**Acceptance Scenarios**:

1. **Given** tema con break a medio tempo, **When** se analiza, **Then** BPM correcto (no la mitad).
2. **Given** cadena completa, **When** falla todo, **Then** fallback a Beat This!/QM sin errores.

---

### User Story 3 - Sin regresión (Priority: P1)

Todo lo que hoy está verde sigue verde con los mismos números.

**Acceptance Scenarios**:

1. **Given** sync 120vs126, **When** ambas direcciones, **Then** lockMs ±20% de hoy y exit=0.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: MasterClock MUST tener dueño explícito (auto/manual) + badge por deck.
- **FR-002**: El offset de fase MUST medirse centralizado en beats contra el reloj.
- **FR-003**: `canPhaseSync` MUST gatear fase (grids válidas + sonando + rango + no scratch); si no, solo tempo.
- **FR-004**: El detector MUST sumar histograma de intervalos + coherencia + plantillas de octava (código propio, ideas ni::mir).
- **FR-005**: Ni una línea de código propietario en el repo. Referencia: solo comportamiento observado y documentacion publica.
- **FR-006**: Licencias de lo nuevo MUST ser GPL-compatibles (propio o MIT/BSD).

### Key Entities

- **MasterClock**: ownerDeck (-1), auto flag, tempo efectivo del dueño.
- **SyncUnit (por deck)**: offset en beats vs reloj, estado Off/Armed/Tempo/Beat (se conserva).
- **IntervalHistogram**: picos de período candidatos + score de coherencia.

## Success Criteria *(mandatory)*

- **SC-001**: A→B, B→A, flip-por-pausa: exit=0 con lockMs ±20%.
- **SC-002**: Set conflictivo: ≥AS actuales en BPM correcto (benchmark antes/después).
- **SC-003**: `grep -ri "ni::mir\|__ZN2ni" src/` vacío (cero rastro de copia).
- **SC-004**: Autotest completo + sync exit=0.

## Assumptions

- Downbeats siguen de Beat This! (su CNN propia es mejor atajo que reimplementar la de NI).
- Time-stretch/Élastique fuera (comercial; keylock futuro = Rubber Band GPL).
- BeatDetector en vivo (zapateo) es del spec 009-beat-detector en curso; aquí solo offline.
