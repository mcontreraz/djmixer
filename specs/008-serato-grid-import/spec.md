# Feature Specification: Serato Grid Import

**Feature Branch**: `008-serato-grid-import`

**Created**: 2026-10-13

**Status**: Complete (2026-10-14, salvo T015 bit-de-lock: formato Markers2
no recuperado; plumbing listo)

**Medido**: oráculo 12/12; barrido DJ AB_SET 8059 archivos (5396 grids,
0 inválidas, 27/27 BPM vs sqlite); conversión 5337/5337; MP3 tageado
end-to-end exit=0 con gridSource Serato.

**Input**: User description: "importar los beatgrids de Serato (tags GEOB + átomos MP4) a nuestro BeatGrid en vez de detectar todo; lo detectado queda como fallback"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - MP3 con grid Serato usa su grid (Priority: P1)

Un MP3 analizado por Serato (con frame `Serato BeatGrid`) al cargarse usa su
grilla original (beats, BPM, downbeat, locked) en vez de la detectada: el
sync engancha sobre el mismo dato que Serato.

**Why this priority**: Es el caso con evidencia completa (payload v1
recuperado + parser + 12 pruebas en `replica/beatgrid-datos/`).

**Independent Test**: Cargar un MP3 con tag BeatGrid válido → `deck.bpm`
coincide con el BPM del tag (±0.01) y los beats vienen del tag, no del
detector (comparar contra `beatgrid_blob.py`).

**Acceptance Scenarios**:

1. **Given** MP3 con `Serato BeatGrid` válido, **When** se carga, **Then** BPM/beats/downbeat/locked son los del tag.
2. **Given** MP3 sin tag, **When** se carga, **Then** se usa detección propia (sin regresión).

---

### User Story 2 - M4A con grid Serato (Priority: P2)

Lo mismo para M4A (`----:com.serato.dj:beatgrid`). La librería del usuario es
mayoritariamente M4A, así que sin esto el P1 cubre poco.

**Why this priority**: Cobertura real de biblioteca; el wrapper MP4 está
pendiente en la réplica (hay que completarlo).

**Independent Test**: M4A con átomo beatgrid → misma verificación que US1.

**Acceptance Scenarios**:

1. **Given** M4A con beatgrid, **When** se carga, **Then** usa su grilla.
2. **Given** M4A sin beatgrid, **When** se carga, **Then** detección propia.

---

### User Story 3 - Locked se respeta + fallback (Priority: P2)

Si el grid importado viene bloqueado (`BpmLock`/lock), no se re-analiza ni se
sobrescribe nunca; si el tag está corrupto o ausente, detección propia sin
interrupciones.

**Why this priority**: "No pisar trabajo del usuario" es regla Serato
documentada (reanalizar respeta bloqueadas).

**Independent Test**: Marcar lock en fixture, forzar re-análisis → el grid
importado sobrevive intacto; tag corrupto → grid detectada.

**Acceptance Scenarios**:

1. **Given** grid locked importada, **When** se re-analiza, **Then** se conserva.
2. **Given** payload corrupto, **When** se carga, **Then** cae a detección y el deck suena igual.

---

### Edge Cases

- ¿Múltiples versiones de payload (v1 vs futuras)? → solo v1 verificada; otra versión = fallback a detección + log.
- ¿MP3 con markers pero sin BeatGrid? → markers solos no alcanzan: detección.
- ¿DB `asset_auxiliary` con blobs? → fuera de alcance (writes no trazados); solo tags de archivo.
- ¿Archivo m4a que no decodificamos? → el grid se importa igual pero el deck no suena: dependencia documentada (decode m4a es otro feature).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST parsear `Serato BeatGrid` (GEOB/MP3) según `serializer-v1.md` + validarlo contra `beatgrid_blob.py`.
- **FR-002**: El sistema MUST parsear `----:com.serato.dj:beatgrid` (MP4) completando el wrapper pendiente.
- **FR-003**: La grilla importada MUST poblar `BeatGrid` (beats, bpm, downbeat, locked, valid) y usarse en sync/waveforms como si fuera detectada.
- **FR-004**: Con tag ausente/corrupto/versión desconocida MUST usarse detección propia sin errores visibles.
- **FR-005**: Un grid locked MUST sobrevivir re-análisis.
- **FR-006**: La fuente de la grilla (serato/detectada) MUST ser observable (propiedad para UI/debug).

### Key Entities

- **SeratoGridPayload**: bytes del tag + versión + records de 8 B + terminal (ver `serializer-v1.md`); solo lectura.
- **BeatGrid (extensión)**: suma `locked: bool` + `source: enum {detected, serato}`.
- **Deck**: expone `gridSource`; el sync no cambia (consume `BeatGrid` igual).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: MP3 con fixture válido muestra el BPM del tag (±0.01) en el deck.
- **SC-002**: Los beats importados coinciden con `beatgrid_blob.py` al 100% en fixtures.
- **SC-003**: Sin tag, el comportamiento es idéntico al actual (autotest verde sin cambios).
- **SC-004**: Re-análisis con lock conserva la grilla importada.

## Assumptions

- Formato BeatGrid v1 (el recuperado); otras versiones = fallback.
- Solo lectura de tags (nunca escribimos archivos del usuario).
- M4A decode para *sonar* es otro feature; importar su grid no lo requiere... pero sin decode el sync no suena: documentado como dependencia.
- Referencia legal limpia: parser propio desde `serializer-v1.md` + Mixxx como contraste, sin copiar binario.
