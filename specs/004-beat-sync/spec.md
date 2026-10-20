# Feature Specification: Beat Sync

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

**Feature Branch**: `004-beat-sync`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Beat sync estilo Serato usando las referencias
(docs/referencia-serato/beat-sync/). Alinear tempo y fase entre dos decks; el primero en sync
es el primario. La detección de BPM ya vive en 003."

Las `referencia-serato/beat-sync/` (no publicado) que cita el enunciado son
referencia local, no publicada: solo existen en la máquina de desarrollo
(ver `referencia-local.md` (no publicado) (../../docs/referencia-local.md, no publicado)).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tempo Sync (Priority: P1)

El deck esclavo iguala el **tempo** del primario ajustando su `rate`, con **equivalencia de
octava** (×2/×0.5): 70 y 140 BPM se tratan como el mismo tempo.

**Why this priority**: Es la mitad del beat sync. Serato lo documenta como estado `Tempo` (solo
BPM, sin fase). Sin tempo alineado no hay mezcla posible.

**Independent Test**: Deck A a 128, deck B a 64 (octava) → al sincronizar, B adopta el tempo de
A (no se queda en 64).

**Acceptance Scenarios**:

1. **Given** dos temas con BPM conocidos, **When** se activa sync en B, **Then** el `rate` de B converge para que su BPM efectivo iguale al de A.
2. **Given** BPMs en octava (70/140), **When** se comparan, **Then** se reconocen equivalentes (FR-003).
3. **Given** sync activo y el primario cambia pitch, **When** el primario ajusta, **Then** el esclavo sigue el nuevo tempo.

---

### User Story 2 - Beat Sync (fase alineada) (Priority: P1)

Además del tempo, el esclavo **alinea la fase** (los beats caen juntos) mediante un lazo continuo
(phase-lock) que corrige el `rate` y/o emite `seek` pendiente, sin tocar el hilo de audio.

**Why this priority**: Es la firma del beat sync real. Serato lo llama `Beat` (tempo + fase +
downbeat). Las ganancias exactas del `SyncLogic` de Serato **no están** en las referencias (ver
"Pendiente" en beat-sync.md), así que el lazo es propio (proporcional + nudge), clean-room.

**Independent Test**: Dos temas a igual BPM, fases distintas → los beats convergen y quedan
alineados (sin drift) mientras ambos suenan.

**Acceptance Scenarios**:

1. **Given** dos temas a igual BPM con fases distintas, **When** se activa beat sync, **Then** la fase converge (error → 0) y se mantiene estable.
2. **Given** beat sync activo 10 s, **When** se observa, **Then** no hay drift acumulado (error de fase acotado).
3. **Given** beat sync activo y el primario hace seek, **When** el primario salta, **Then** el esclavo re-alinea.

---

### User Story 3 - Estados y deck primario (Priority: P2)

Estados por deck `Off / Armed / Tempo / Beat` y **deck primario** (el primero en sync impone el
tempo; los demás siguen). Ref: modelo de comportamiento en `beat-sync.md` §"Modelo de comportamiento".

**Why this priority**: Es el modelo de interacción de Serato (un deck manda, los demás obedecen) y
hace predecible quién mueve a quién.

**Independent Test**: Activar sync en A (primario) y luego en B → B sigue a A; desactivar A y
activar solo B → B es el nuevo primario.

**Acceptance Scenarios**:

1. **Given** A en sync y luego B, **When** se mueve el tempo, **Then** B sigue a A.
2. **Given** sync desactivado, **When** se desactiva, **Then** el deck vuelve a su rate manual sin saltos.
3. **Given** estado `Armed`, **When** el deck da Play, **Then** entra a sync al arrancar.

---

### User Story 4 - Modos Off / Simple / Smart (Priority: P2)

Modo global `Off / Simple / Smart` (entero de 3 estados, valor observado). En el MVP
`Simple` = alineación de beat (transients), `Smart` = grid + downbeat (downbeat real queda F4b).

**Why this priority**: Refleja la preferencia de Serato; el downbeat musical es MIR difícil y se
difire, pero el switch debe existir.

**Independent Test**: Cambiar el modo en la UI y ver que `Simple`/`Smart` altera si se alinea
solo beat o beat+downbeat.

**Acceptance Scenarios**:

1. **Given** modo `Off`, **When** se activa sync, **Then** no sincroniza.
2. **Given** modo `Simple`, **When** beat sync, **Then** alinea fase de beat.
3. **Given** modo `Smart`, **When** beat sync, **Then** alinea beat + downbeat (F4b cuando exista).

---

### Edge Cases

- ¿Deck sin `BeatGrid.valid`? → solo Tempo Sync (nunca Beat), sin crash (FR-007).
- ¿BPM en octava (70 vs 140)? → normalizados antes de comparar (FR-003).
- ¿Seek del primario mientras B sincroniza? → B re-alinea (US2.3).
- ¿Activar sync sin track cargado? → se ignora o queda `Armed`.
- ¿Dos decks quieren ser primarios? → el primero gana; el segundo es esclavo.
- ¿El primario se desactiva? → el siguiente en sync (si hay) pasa a primario.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST ajustar el `rate` del esclavo para igualar el tempo del primario (Tempo Sync).
- **FR-002**: El sistema MUST alinear la fase del esclavo al primario con un lazo continuo (Beat Sync).
- **FR-003**: El sistema MUST normalizar BPMs equivalentes por octava (×2/×0.5) antes de comparar.
- **FR-004**: El primer deck en activar sync es el **primario**; los demás son esclavos.
- **FR-005**: Cada deck tiene un estado `Off / Armed / Tempo / Beat` y un modo global `Off / Simple / Smart`.
- **FR-006**: La corrección de sync MUST correr fuera del hilo de audio (timer UI + `rate` atómico + `seek` pendiente).
- **FR-007**: Un deck sin `BeatGrid.valid` degrada a solo Tempo Sync, nunca bloquea ni crashea.
- **FR-008**: Desactivar sync MUST restaurar el `rate` manual sin saltos.

### Key Entities

- **SyncEngine** (`syncengine.h/.cpp` (no publicado)): deck primario, estados por deck, lazo de corrección.
- **BeatGrid** (existente, 003): BPM + `beats[]` + fase; la referencia de beat.
- **Deck** (extensión): estado de sync + `rate` atómico (ya expuesto como `pitch`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Dos temas a igual BPM quedan con fase alineada (error < ±20 ms) y sin drift 30 s.
- **SC-002**: BPMs en octava (70/140) sincronizan al tempo correcto.
- **SC-003**: La UI responde durante la corrección (play/pausa < 200 ms con sync activo).
- **SC-004**: Desactivar sync restaura el `rate` manual sin click.
- **SC-005**: Un deck sin BeatGrid sincroniza solo tempo y no crashea.

## Assumptions

- El BeatGrid ya existe (003); esta feature solo lo **consume** para alinear.
- El downbeat musical (Smart real) es F4b: en el MVP `Smart` ≈ `Simple`.
- La corrección corre en un `QTimer` de ~50 ms del hilo UI (misma cadencia que el refresh).
- Multi-deck (3–4) queda fuera; dos decks A/B en esta fase.
