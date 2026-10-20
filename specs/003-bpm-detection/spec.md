# Feature Specification: BPM Detection

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Feature Branch**: `003-bpm-detection`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "El análisis de un file (cuando no está en caché/DB) produce TODA la info
necesaria en una sola pasada: metadata (título/artista/key) + BPM + waveform. En esta pasada se
actualiza la info del plato (BPM real) y la key de la canción en los decks. Determinista, cacheada
y con degradación limpia."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - BPM estimado del audio (Priority: P1)

Al cargar un tema, el deck estima su **BPM** desde el audio (no del tag `TBPM`), de forma
determinista: el mismo archivo produce siempre el mismo BPM.

**Why this priority**: Es el cimiento del beat sync y del display de tempo real. Hoy el "88/134"
del QML es texto fijo que miente. Sin BPM real nada más tiene sentido.

**Independent Test**: Cargar el WAV de prueba → el deck expone un BPM estable (ej. 120–140) y el
mismo archivo analizado dos veces devuelve idéntico BPM.

**Acceptance Scenarios**:

1. **Given** un tema cargado, **When** termina el análisis, **Then** `deck.beatGrid.bpm > 0` y coincide con el tempo audible.
2. **Given** el mismo archivo analizado dos veces, **When** se comparan los BPM, **Then** son idénticos.
3. **Given** un tema con BPM en octava (70 vs 140 real), **When** se estima, **Then** se resuelve al tempo musical correcto (plegado de octava).

---

### User Story 2 - Posiciones de beat y fase (Priority: P1)

El análisis también ubica **dónde caen los beats** (tiempos de beat) y la **fase** (referencia del
beat 1). Es lo que el futuro beat sync alineará.

**Why this priority**: El beat sync necesita no solo "cuántos BPM" sino "dónde están los beats".
Se calcula junto con el BPM en la misma pasada.

**Independent Test**: Cargar un tema → `beatGrid.beats[]` es una lista creciente y equidistante
(periodo = 60/BPM) que cubre la pista.

**Acceptance Scenarios**:

1. **Given** BPM detectado, **When** se inspecciona `beats[]`, **Then** los beats están espaciados `60/bpm` segundos (tolerancia de un frame).
2. **Given** un beat conocido (kick), **When** se alinea la grilla, **Then** los beats caen sobre los transientes (la fase maximiza la energía de onsets).

---

### User Story 3 - Una pasada y nodos (Priority: P2)

El análisis de tempo corre **dentro del mismo decode del waveform** (una sola pasada sobre el
audio), emitiendo **nodos** de onset/beat de forma streaming, sin un segundo scan del archivo.

**Why this priority**: Un segundo decode duplicaría I/O y CPU por tema. La arquitectura F2 ya
decodifica una vez; el tempo debe colgarse de esa misma pasada.

**Independent Test**: Medir que el tiempo de análisis con BPM ≈ tiempo de análisis sin BPM (el
overhead del tempo es despreciable, no un segundo decode).

**Acceptance Scenarios**:

1. **Given** un análisis en curso, **When** se decodifica, **Then** el mismo bucle produce waveform y acumula onsets (no se reabre el archivo).
2. **Given** el decode terminó, **When** se corre la autocorrelación, **Then** BPM y beats salen del envolvente de onsets ya acumulado.

---

### User Story 4 - Caché y degradación limpia (Priority: P2)

El BeatGrid se cachea con el waveform (mismo sidecar v5) y un fallo de análisis degrada a "sin
BPM" sin romper la carga ni la reproducción.

**Why this priority**: Evita re-analizar el tempo cada vez y cumple la constitución II (no
bloquear). El BeatGrid v5 ya está integrado al cache.

**Independent Test**: Recargar un tema analizado → BPM disponible al instante; cargar un archivo
corrupto → `valid=false`, deck operativo.

**Acceptance Scenarios**:

1. **Given** un tema ya analizado, **When** se recarga, **Then** el BPM aparece de inmediato (cache).
2. **Given** un archivo corrupto/ruido, **When** falla la autocorrelación, **Then** `beatGrid.valid=false` y el deck sigue operativo.

---

### User Story 5 - Metadata + key al deck (Priority: P2, referencia)

Al analizar un file, el deck recibe también **metadata** (título, artista, key) y la UI deja de
mostrar texto fijo: el **plato** muestra el BPM real, la **key badge** muestra la key real y el
**header** el título/artista real.

**Why this priority**: Es referencia (no bloquea el beat sync ni el BPM). El usuario pidió que el
BPM sea estricto como prioridad; la key es secundaria (se lee de tags, sin detección armónica).

**Independent Test**: Cargar un tema taggeado → el plato muestra su BPM detectado, la badge su key
y el header su título/artista (no los valores de ejemplo).

**Acceptance Scenarios**:

1. **Given** un tema analizado, **When** se mira el deck, **Then** el plato muestra `bpm` detectado (no "88/134" fijo).
2. **Given** un tema con key en tag, **When** se carga, **Then** la badge muestra esa key (ej. "7A").
3. **Given** un tema sin key en tag, **When** se carga, **Then** la badge muestra "—" (desconocida), sin romper.

---

### Edge Cases

- ¿Silencio o ruido (sin onset claro)? → autocorrelación plana → `valid=false`, sin crash.
- ¿BPM fuera de 70–180? → se pliega por octava (×2/×0.5) hasta el rango.
- ¿Tema con cambios de tempo? → la autocorrelación global devuelve el tempo dominante (documentado como limitación).
- ¿Dos decks analizan el mismo archivo a la vez? → escritura atómica (QSaveFile + mutex, ya en v5).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST estimar el BPM de cada tema cargado desde el audio (onsets + autocorrelación), de forma determinista.
- **FR-002**: El sistema MUST calcular las posiciones de beat (`beats[]`) y la fase (referencia del beat 1).
- **FR-003**: El análisis de tempo MUST correr en **una sola pasada** (el mismo decode del waveform), emitiendo nodos de onset de forma streaming; no se reabre el archivo.
- **FR-004**: El sistema MUST plegar la octava (×2/×0.5) para resolver BPM equivalentes.
- **FR-005**: El BeatGrid MUST cachearse con el waveform (sidecar v5 existente, misma clave).
- **FR-006**: Un fallo de análisis MUST degradar a `BeatGrid.valid=false`, nunca bloquear carga ni reproducción.
- **FR-007**: El análisis MUST correr fuera de los hilos de audio y UI (worker existente).
- **FR-008**: El análisis de un file MUST producir, en la misma pasada, metadata (título/artista/key) + BPM + waveform, cacheados juntos bajo una sola clave.
- **FR-009**: La UI MUST actualizar el plato (BPM real), la key badge (key real o "—") y el header (título/artista) desde el resultado del análisis, no desde texto fijo.

### Key Entities

- **BeatGrid** (`beatgrid.h` (no publicado), ya existe): `bpm`, `beats[]`, `downbeat`, `valid`, `phaseAt(t)`, `nextBeatAtOrAfter(t)`.
- **TrackMeta**: título, artista, key (Camelot) leídos de tags; vacíos si no hay tag.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El mismo archivo produce el mismo BPM en análisis repetidos (determinismo píxel a píxel del BeatGrid).
- **SC-002**: El BPM estimado del WAV de prueba está a ±0.5 BPM de su valor real **y con la octava correcta** (no el doble/mitad).
- **SC-003**: El overhead del análisis de tempo sobre el waveform es < 5% (una pasada, sin segundo decode).
- **SC-004**: Recargar un tema analizado muestra su BPM en < 300 ms.
- **SC-005**: Cargar silencio/corrupción devuelve `valid=false` sin crash y el deck sigue operativo.

## Assumptions

- El análisis se dispara al cargar al deck (lazy), igual que F2.
- Rango de búsqueda: 70–180 BPM con plegado de octava (cubre dance music).
- El **downbeat musical** (inicio de compás) se aproxima con el primer onset fuerte; la detección armónica real queda fuera (F3b).
- **Key**: en este incremento se **lee de tags** (TKEY/initialkey); la **detección armónica de key** (chroma/Camelot) es una feature aparte posterior. Sin tag → "—".
- **Metadata** (título/artista/key): se lee con **TagLib** (dependencia justificada en el plan, constitución IV).
- Formatos: los que ya decodifica el motor (wav/mp3/flac/m4a).
