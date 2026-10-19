# Feature Specification: Cue Points (CDJ)

**Feature Branch**: `005-cue-points`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "cue points: hereda el needle search pero guarda los puntos de cue; el botón CUE del plato funciona como un CDJ Pioneer"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Botón CUE estilo CDJ (Priority: P1)

El botón CUE redondo del plato se comporta como un Pioneer CDJ:
sonando + pulsar CUE → vuelve al cue guardado y pausa; en pausa +
mantener CUE → suena desde el cue mientras se mantiene, al soltar vuelve
al cue y pausa; en pausa + pulsar CUE → guarda la posición actual como cue.

**Why this priority**: Es el corazón del feature y lo pedido explícito. Sin
esto no hay cue que guardar ni marcar.

**Independent Test**: Con el WAV sonando, pulsar CUE → pausa justo en el cue
(00:00 la primera vez). Pausado a los 30 s, pulsar CUE → queda guardado;
mantener → suena; soltar → vuelve.

**Acceptance Scenarios**:

1. **Given** reproducción en curso, **When** se pulsa CUE, **Then** vuelve al cue guardado y queda en pausa.
2. **Given** pausa en una posición sin cue previo, **When** se pulsa CUE, **Then** esa posición queda guardada como cue.
3. **Given** pausa sobre el cue, **When** se mantiene CUE 2 segundos y se suelta, **Then** sonó esos 2 segundos y volvió al cue en pausa.

---

### User Story 2 - El cue persiste entre cargas (Priority: P2)

El cue guardado sobrevive a recargar el tema (y a reiniciar la app): al
cargar un tema con cue previo, el deck lo recupera.

**Why this priority**: "Guarda los puntos" lo exige; sin persistencia el cue
muere al cambiar de tema.

**Independent Test**: Guardar cue a los 30 s, cargar otro tema, recargar el
primero → pulsar CUE devuelve a los 30 s.

**Acceptance Scenarios**:

1. **Given** cue guardado a los 30 s, **When** se recarga el mismo archivo sin cambios, **Then** el cue sigue en 30 s.
2. **Given** archivo modificado en disco, **When** se carga, **Then** el cue viejo se descarta (misma invalidez que la caché de waveform).

---

### User Story 3 - Marca visual del cue (Priority: P3)

El punto de cue se ve: marca en el overview y en las waveforms grandes a la
altura del tiempo guardado (el cuadradito prometido vuelve como marca fija,
no giratoria).

**Why this priority**: Cierra el círculo visual (needle + guardado + marca) y
cumple la promesa hecha al quitar el cuadradito.

**Independent Test**: Con cue a los 30 s, el overview y la grande muestran la
marca exactamente sobre esa posición.

**Acceptance Scenarios**:

1. **Given** cue guardado, **When** se mira el overview, **Then** hay una marca en la posición del cue.
2. **Given** sin cue (tema fresco), **When** se mira, **Then** no hay marca.

---

### User Story 4 - Hot cues en pads estilo Serato (Priority: P2)

Los 8 pads dejan de ser "+" decorativos: pad vacío + click guarda la posición
actual; pad con cue + click salta a ese punto y suena; click derecho borra.
Los pads muestran su número cuando tienen cue.

**Why this priority**: Pedido explícito (comportamiento Serato) y reutiliza
todo lo de US1/US2 (seek, persistencia por archivo).

**Independent Test**: Pausado a los 20 s, click en pad 3 → muestra "3"; click
de nuevo sonando → salta a 20 s y suena; click derecho → vuelve a "+".

**Acceptance Scenarios**:

1. **Given** pad vacío y tema cargado, **When** click, **Then** guarda la posición y el pad muestra su número.
2. **Given** pad con cue, **When** click, **Then** salta al cue y reproduce.
3. **Given** pad con cue, **When** click derecho, **Then** se borra (vuelve a "+").
4. **Given** hot cues guardados, **When** se recarga el tema, **Then** los pads recuperan sus números.

---

### Edge Cases

- ¿CUE sin tema cargado? → se ignora, sin crash.
- ¿CUE con archivo corrupto? → el deck degradado no guarda (sin caché válida no hay cue).
- ¿Soltar CUE fuera del botón tras mantener? → al soltar en cualquier lado vuelve al cue (release global mientras se mantiene).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST distinguir pulsar (click) de mantener (press-hold) en el botón CUE.
- **FR-002**: Sonando + CUE MUST volver al cue y pausar.
- **FR-003**: En pausa + CUE MUST guardar la posición actual y pre-escuchar mientras se mantiene.
- **FR-004**: Al soltar tras mantener MUST volver al cue y pausar.
- **FR-005**: El cue MUST persistir por archivo (misma invalidez que la caché: ruta + tamaño + fecha).
- **FR-006**: La UI MUST mostrar la marca del cue en overview y grandes cuando exista.
- **FR-007**: Sin tema o tema corrupto, CUE MUST no hacer nada.
- **FR-008**: Pad vacío + click MUST guardar la posición actual como hot cue de ese pad.
- **FR-009**: Pad con cue + click MUST saltar al cue y reproducir.
- **FR-010**: Pad con cue + click derecho MUST borrarlo.
- **FR-011**: Los hot cues MUST persistir por archivo igual que el cue principal.

### Key Entities

- **CuePoint**: tiempo en segundos + flag válido; vive en `Deck`, persiste en sidecar `<clave>.cuepoint` (texto con segundos).
- **HotCue[8]**: lista por deck (`-1` = vacío); persiste en sidecar `<clave>.hotcues` (líneas `índice segundos`).
- **Deck (extensión)**: estado cue (posición, preview-activo), slots de preview, API de hot cues.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Pulsar CUE sonando devuelve al cue con error menor a 100 ms de audio.
- **SC-002**: Recargar el tema recupera el cue con error menor a 100 ms.
- **SC-003**: La marca visual coincide con la posición guardada (verificación en captura).
- **SC-004**: Mantener CUE 2 s suena 2 s (±200 ms) y al soltar pausa en el cue.
- **SC-005**: Click en pad con cue salta a ±100 ms y reproduce; recargar recupera los pads.

## Assumptions

- Un solo cue principal por deck (hot-cues múltiples = M4, fuera).
- Preview = play normal mientras se mantiene (sin salida de audífonos separada; bus cue-mix = F3).
- El formato `.cuepoint` es texto simple con segundos (legible y debuggeable).
- `Deck::cue()` actual (stop+seek 0) se reemplaza por la semántica CDJ.
