# Feature Specification: Key Lock + Key Analysis

**Feature**: `016-key-lock` · **Creada**: 2026-10-19
**Estado**: Especificada; implementación pendiente
**Base revisada**: `23bfe59` · **Rama de implementación propuesta**: `016-key-lock`
**Solicitud**: «Key Lock (pitch fijo al cambiar tempo) + análisis de tonalidad
(Camelot), revisando cómo lo hace Serato en la REA ya guardada».

## Objetivo y alcance

Dos capacidades independientes sobre el motor de audio y el pipeline de análisis:

1. **Key Lock** (por deck): con el botón **KEY** activo, el tono del audio se
   conserva cuando `m_rate ≠ 1` — lo mueva el pitch slider, el sync, el pitch
   bend o el spin del jog. Apagado = comportamiento actual (remuestreo/varispeed:
   el tono baja y sube con el tempo, como un vinilo).
2. **Key Analysis** (por pista): al terminar el análisis de una pista, detectar
   la tonalidad, mapearla a notación Camelot (`1A`–`12B`) y mostrarla en el deck
   y en la biblioteca junto al BPM, reutilizando el campo `key`/`meta` existente.

"Conservar el pitch" significa conservar la frecuencia fundamental percibida del
material armónico mientras cambia el tempo; no promete transparencia total sobre
material percusivo a ratios extremos. "Key detectado" es una estimación
(Chromagram + correlación), no un dato de verdad absoluta; se distingue de la
key del tag.

Se revisaron las cadenas REA ya guardadas de Serato DJ Pro 4.0.10.213.
[Research](research.md) separa observaciones, inferencias y decisiones propias.
No se afirma haber recuperado ni medido el algoritmo propietario de time-stretch
ni el de detección de key.

V1 incluye: toggle KEY por deck con crossfade de entrada/salida, time-stretch
WSOLA en el path normal (no-scratch), detección de key al finalizar el análisis,
mapeo Camelot y persistencia en caché. **No incluye**: key shift/transposición
(±12 semitonos), Pitch-Shift independiente, key lock dentro de loops activos,
ni edición manual de la key.

## User Scenarios & Testing

### US1 — Key Lock conserva el pitch al variar el tempo (P1)

Con una pista sonando y KEY activo, muevo el pitch slider, el sync ajusta el
rate o aplico pitch bend: el tempo cambia pero la nota/frecuencia percibida se
mantiene. Apago KEY y vuelve el comportamiento vinílico.

**Aceptación**:
1. Sobre un seno puro de 440 Hz, un barrido de `rate` 0.5→1.5 con KEY ON mantiene
   la fundamental de salida en ~440 Hz (desviación < ±5 cents en estado estable,
   excluyendo el transitorio del propio barrido), mientras el tempo (BPM de un
   patrón rítmico) escala con `rate`.
2. Con KEY OFF el mismo barrido desplaza la fundamental proporcionalmente a
   `rate` (varispeed), sin alteración.
3. El barrido no produce saltos de fase ni "flanger" audible a `rate≈1`.
4. Sync y pitch bend (±5%) pasan por el mismo camino: el bend no desactiva ni
   "burla" el key lock.

### US2 — Bypass exacto y transición sin clicks (P1)

A `rate == 1.0` KEY ON es indistinguible de KEY OFF (bit a bit). Activar/desactivar
KEY en marcha no produce click, salto ni artefacto de crossfade evidente.

**Aceptación**:
1. Con `rate==1.0`, la salida con KEY ON es **bit-exacta** a la del path actual
   (remuestreo lineal) para el mismo bloque de entrada.
2. Toggle ON→OFF→ON durante reproducción produce una transición acotada
   (crossfade ≤ ~10 ms) sin discontinuidad de amplitud > umbral y sin fase
   "flangerizada" audible.
3. El crossfade de toggle no cambia la posición del playhead ni dispara seek.

### US3 — KEY convive con sync, bend, scratch y loop (P1)

KEY es ortogonal al transporte: no pelea con sync, no interfiere con el scratch
(que usa su propio resampler) y no rompe los loops.

**Aceptación**:
1. Con KEY ON, el sync sigue corrigiendo `m_rate` y el deck sigue la fase; el
   key lock solo cambia el tono percibido, no la lógica de sync.
2. Durante scratch activo, el resampler de scratch (Hermite/sinc) es el que
   manda; al soltar, el path normal retoma el modo KEY que corresponda sin salto.
3. KEY ON durante un loop activo: en v1 el loop sigue con su render actual
   (remuestreo lineal + anti-click); documentar que key lock dentro del loop es
   una fase posterior (brecha explícita, no un fallo silencioso).

### US4 — Detección y display de key (P1)

Al terminar el análisis de una pista, el deck y la biblioteca muestran la
tonalidad en Camelot (`1A`–`12B`) junto al BPM, usando el tag si existe y la
detección si no.

**Aceptación**:
1. Un fixture de acordes con fundamental conocida (p. ej. arpegio de Do mayor)
   se clasifica como `8B` (Do mayor); un arpegio de La menor como `8A`.
2. Si el tag trae key (`INITIALKEY`/`KEY`), esa gana; si no, manda la detección;
   si ninguno, se muestra `—`.
3. El resultado se cachea (sidecar `.wfcache`): recargar la pista no reanaliza
   la key y la muestra de inmediato.
4. La key se muestra en el badge del deck (ya existente) y en la columna `key`
   de la biblioteca.

### US5 — Estado y acciones visibles (P2)

El botón KEY refleja el estado real confirmado por el motor, y las acciones
(click, atajo, MIDI) usan el mismo contrato.

**Aceptación**: el LED del botón KEY solo se enciende tras confirmación del
motor; note-off no re-alterna el toggle; una respuesta tardía de otro archivo no
ilumina el deck actual.

## Functional Requirements

- **FR-001**: Propiedad por deck `keyLock` (bool) con toggle ON/OFF; OFF es el
  comportamiento actual (varispeed/remuestreo lineal); ON activa time-stretch
  con pitch fijo.
- **FR-002**: El estado `keyLock` vive como flag atómico UI→audio y se confirma
  audio→UI (snapshot), sin alloc/locks en el callback.
- **FR-003**: Time-stretch **WSOLA** (correlación cruzada + crossfade
  equal-power) en el path normal no-scratch de `Deck::render`. Buffers de
  análisis/grano/correlación **preasignados**; cero malloc/I-O/locks en el
  callback.
- **FR-004**: Latencia del stage de stretch acotada: `latencia ≤ 40 ms` a 48 kHz
  (hop de análisis y ventana de búsqueda configurables; propuesta `Ha≈10 ms`,
  `Δ≈10 ms`).
- **FR-005**: Bypass exacto: si `rate == 1.0`, la salida es bit-exacta a la del
  path actual (remuestreo lineal), independientemente de `keyLock`.
- **FR-006**: Banda de transparencia a `|rate−1| < ε`: solape mínimo y alineación
  por correlación (o conmutación a interpolación lineal) de modo que no haya
  flanger audible cerca de rate 1.
- **FR-007**: Toggle KEY en marcha aplica crossfade de rampa corta (≤ ~10 ms)
  entre bypass y stretch; no cambia `m_playedFrames` ni dispara seek; no rompe
  EQ/filtro/gain posteriores.
- **FR-008**: `m_rate` sigue siendo la única fuente de verdad del tempo (pitch
  slider, `setAudioRate` de sync y pitch bend multiplican sobre él); el key lock
  solo cambia la *interpretación* del resample, no el cursor ni la fase.
- **FR-009**: Scratch mantiene su resampler (Hermite/sinc) y queda fuera del key
  lock; al soltar, el path normal retoma el modo KEY vigente con continuidad.
- **FR-010**: Key lock dentro de un loop activo queda **fuera de v1**; el loop
  sigue con su render actual. Se registra como brecha explícita, no como fallo.
- **FR-011**: Key analysis corre en `WaveformAnalyzer` (hilo aparte), reutilizando
  el `monoBuf` ya acumulado, sin segundo decode.
- **FR-012**: Detección con `qm-dsp GetKeyMode` (Chromagram + Krumhansl-Schmuckler),
  afinación A=440 Hz; se rechaza el resultado si la confianza máxima queda bajo
  umbral (→ "sin key").
- **FR-013**: Mapeo determinista `GetKeyMode` (índice 0–24) → notación Camelot
  `1A`–`12B`, con tabla propia de teoría musical, verificada por fixture.
- **FR-014**: Precedencia de display: tag (`INITIALKEY`/`KEY`) > análisis >
  vacío (`—`). Se publica `keySource` (Tag/Analysis/None) para auditar.
- **FR-015**: El key detectado se persiste en `WaveformCache` (sidecar) junto a
  grid/meta, con revisión de meta versionada; recarga sin reanálisis.
- **FR-016**: Un resultado de análisis obsoleto (generación vieja) no pisa el
  estado de la pista actual.
- **FR-017**: El display de key en deck/biblioteca usa el contrato existente
  (`Deck::key`, badge Camelot con color de rueda); no se introducen unidades ni
  notaciones ambiguas.

## Success Criteria

- **SC-001** (continuidad de pitch): seno de 440 Hz, barrido de `rate`
  0.5→1.5 con KEY ON → fundamental de salida dentro de ±5 cents de 440 Hz en
  estado estable, medida por estimación espectral (o cruce por cero sobre tramos
  sin transitorio), mientras un patrón rítmico de referencia escala su tempo con
  `rate`. KEY OFF → fundamental escala con `rate`.
- **SC-002** (bypass bit-exacto): con `rate==1.0`, KEY ON produce salida idéntica
  bit a bit a la del path lineal actual para bloques de 1/64/127/256/1024 frames.
- **SC-003** (transición sin artefactos): toggle ON→OFF→ON durante reproducción
  con rampa ≤ 10 ms; discontinuidad de amplitud < umbral y sin "flanger" medible
  (correlación entre tramo bypass y tramo stretch ≥ umbral en la banda de unión).
- **SC-004** (key de fixtures): arpegios/acordes sintéticos con fundamental
  conocida se clasifican en el Camelot esperado (Do mayor→`8B`, La menor→`8A`,
  más una muestra por cada modo si el fixture lo permite); fixture "sin tonalidad
  clara" (ruido/noise) → "sin key" o `—`.
- **SC-005** (mapeo Camelot): la tabla índice→Camelot es biyectiva y verificada
  por fixture; no hay índices huérfanos ni colisiones.
- **SC-006** (caché): análisis + key se guardan en sidecar; recargar la pista
  lee la key sin re-decodificar (verificado por conteo de llamadas o timestamp
  de sidecar).
- **SC-007** (latencia acotada): latencia de grupo del stage de stretch
  ≤ 40 ms (medida con impulso/métrica de retardo, no por inferencia).
- **SC-008** (RT sin alloc): cero malloc/locks/I-O en el intervalo instrumentado
  del callback con KEY ON (barrido + toggle), análogo a `loop_rt_test`.
- **SC-009** (regresión): suites existentes (sync, scratch, loop, eq/filter)
  verdes; capturas del deck con KEY ON/OFF y key visible en deck/biblioteca.

## Entidades y decisiones

`KeylockStage` (DSP WSOLA preasignado), `KeylockSnapshot` (estado confirmado
audio→UI), `KeyAnalysis` (índice GetKeyMode + Camelot + confianza),
`TrackMeta.analyzedKey/keySource` (extensión cacheable). [Contrato](contracts/keylock.md),
[plan](plan.md), [tareas](tasks.md), [research](research.md).

Decisiones propias: WSOLA sobre phase vocoder (RT+latencia), bypass exacto a
rate 1, crossfade de toggle, detección con GetKeyMode sobre `monoBuf`, precedencia
tag>análisis, key lock fuera de scratch y de loop en v1. No se atribuyen estas
políticas exactas a Serato sin evidencia adicional.

## Decisión de UI (2026-10-19)

- El botón KEY va en el DeckPanel **arriba del botón SYNC** (estilo Traktor):
  botón pequeño con acento del deck, toggle con estado iluminado cuando el
  key lock está activo, ToolTip "Key Lock".
- Al lado del BPM (misma fila o la del pitch) se muestra la tonalidad Camelot
  cuando el análisis la conoce (F3).

