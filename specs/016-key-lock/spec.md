# Feature Specification: Key Lock + Key Analysis

**Feature**: `016-key-lock` · **Creada**: 2026-10-19
**Estado**: Implementada (motor Rubber Band); gates F4 pendientes
**Base revisada**: `04e8de0` (motor) · **Rama**: `main`
**Solicitud**: «Key Lock (pitch fijo al cambiar tempo) + análisis de tonalidad
(Camelot), revisando cómo lo hace Serato en la referencia ya guardada».

> **Reconciliada con el código (2026-10-19).** El motor que se despacha es
> **Rubber Band** (GPL-2.0-or-later), no el WSOLA propio que era el plan
> original. Este documento describe lo que el repo hace hoy; el motor
> descartado y su sustituto están en [research.md](research.md).

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

Se revisaron las cadenas de Serato DJ Pro 4.0.10.213 (material de
referencia local, no publicado — ver
referencia local (../../docs/referencia-local.md, no publicado)).
[Research](research.md) separa observaciones, inferencias y decisiones propias.
No se afirma haber recuperado ni medido el algoritmo propietario de time-stretch
ni el de detección de key.

V1 incluye: toggle KEY por deck con crossfade de entrada/salida, time-stretch
con **Rubber Band** en modo real-time (transientes mixtos) en el path normal
(no-scratch) y también dentro del loop activo, detección de key al finalizar el
análisis, mapeo Camelot y persistencia en caché. **No incluye**: key
shift/transposición (±12 semitonos), Pitch-Shift independiente, ni edición
manual de la key.

## User Scenarios & Testing

### US1 — Key Lock conserva el pitch al variar el tempo (P1)

Con una pista sonando y KEY activo, muevo el pitch slider, el sync ajusta el
rate o aplico pitch bend: el tempo cambia pero la nota/frecuencia percibida se
mantiene. Apago KEY y vuelve el comportamiento vinílico.

**Aceptación**:
1. Sobre un seno puro (el fixture del repo es de 480 Hz), con KEY ON la
   fundamental de salida se mantiene en el valor de la fuente (desviación
   < ±15 Hz ≈ 50 cents, que es la tolerancia real del oráculo) mientras el
   tempo escala con `rate`; con KEY OFF la fundamental desplaza
   proporcionalmente a `rate` (varispeed), sin alteración.
2. El barrido no produce saltos de fase ni "flanger" audible a `rate≈1`.
3. Sync y pitch bend (±5%) pasan por el mismo camino: el bend no desactiva ni
   "burla" el key lock.

### US2 — Bypass exacto y transición sin clicks (P1)

Con KEY OFF la salida es bit-exacta al path directo; con KEY ON el motor de
stretch está siempre en el camino. Activar/desactivar KEY en marcha no produce
click, salto ni artefacto de crossfade evidente.

**Aceptación**:
1. Con KEY OFF la salida es **bit-exacta** a la del path actual (remuestreo
   lineal) para el mismo bloque de entrada.
2. Toggle ON→OFF→ON durante reproducción produce una transición acotada
   (crossfade de 1024 frames ≈ 21.3 ms a 48 kHz) sin discontinuidad de
   amplitud > umbral y sin fase "flangerizada" audible.
   **Estado 2026-10-19 ([DJM-36](/DJM/issues/DJM-36))**: la primera mitad se
   cumple (sin salto de amplitud, con su prueba de la prueba); la segunda **no**:
   el crossfade suma dos afinaciones y late a 96 Hz medido. El arreglo de la
   alineación temporal (FR-018/FR-019) es lo que entra en la v1; la
   eliminación del batido va en su propio ticket (FR-020).
3. El crossfade de toggle no cambia la posición del playhead ni dispara seek.

### US3 — KEY convive con sync, bend, scratch y loop (P1)

KEY es ortogonal al transporte: no pelea con sync, no interfiere con el scratch
(que usa su propio resampler) y no rompe los loops.

**Aceptación**:
1. Con KEY ON, el sync sigue corrigiendo `m_rate` y el deck sigue la fase; el
   key lock solo cambia el tono percibido, no la lógica de sync. La fase
   publicada es la **audible** (cursor − rate × latencia del motor), para que un
   deck con KEY y otro sin KEY se comparen en la misma moneda.
2. Durante scratch activo, el resampler de scratch (Hermite/sinc) es el que
   manda; al soltar, el path normal retoma el modo KEY que corresponda sin salto.
3. KEY ON durante un loop activo: el key lock **sí** aplica dentro del loop (el
   motor recibe la ventana del loop leída a `rate=1.0`); entrar y salir del loop
   usa el mismo crossfade simétrico de 1024 frames.

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

El botón KEY refleja el estado real del key lock, y las acciones (click, atajo,
MIDI) usan el mismo contrato.

**Aceptación**: el LED del botón KEY refleja el estado solicitado por el
usuario (se enciende al conmutar, sin esperar confirmación separada del hilo de
audio); note-off no re-alterna el toggle; una respuesta tardía de otro archivo no
ilumina el deck actual.

## Functional Requirements

- **FR-001**: Propiedad por deck `keyLock` (bool) con toggle ON/OFF; OFF es el
  comportamiento actual (varispeed/remuestreo lineal); ON activa time-stretch
  con pitch fijo.
- **FR-002**: El estado `keyLock` vive como flag atómico UI→audio
  (`std::atomic<bool> m_keyLock`), leído por el hilo de audio al inicio de cada
  bloque; sin alloc/locks en el callback. El LED de la UI refleja el estado
  **solicitado** (la señal `keyLockChanged` se emite en el hilo de UI al
  conmutar): no hay una confirmación separada desde el hilo de audio.
- **FR-003**: Time-stretch con **Rubber Band** (GPL-2.0-or-later) en el path
  normal no-scratch de `Deck::render` y también en el path de loop. Un
  `RubberBandStretcher` por deck, en modo real-time con transientes mixtos
  (`OptionProcessRealTime | OptionTransientsMixed`) y `setMaxProcessSize(512)`.
  El motor se construye una sola vez, en el constructor de `Deck`; los buffers
  de entrada/salida/crossfade son **arrays miembro preasignados** de `Deck`
  (`m_klInL/R`, `m_klOutL/R`, `m_klFadeBuf`, `m_klLoopIn`): el código de la
  app no asigna memoria, no hace I/O y no toma locks en el callback al
  alimentar o extraer del motor.
- **FR-004**: Latencia del motor de stretch acotada y **medida, no estimada**.
  `getLatency()` del `RubberBandStretcher` (con `setMaxProcessSize(512)`) da
  **1024 muestras ≈ 21.3 ms a 48 kHz**, pero ese es el **retardo de salida
  inicial**, no la latencia efectiva en streaming: medido sobre el audio
  renderizado, el contenido del motor llega **27–37 ms** tarde respecto del
  path directo (ver `research.md`, sección "Desfase del motor y crossfade del
  toggle de KEY"). El retardo efectivo se **calibra** (en el hilo de UI, al
  construir el deck) y ese valor —no `getLatency()`— es el que se usa para
  compensar la fase audible en sync y para alimentar el motor por delante del
  cursor (FR-007).
- **FR-005**: Bypass por conmutación de camino **descontado**: con KEY **ON** el
  motor de stretch queda **siempre** en el camino, incluso a `rate == 1.0`
  (cruzar el 0 del pitch es solo el ratio pasando por 1.0 dentro del motor);
  no hay banda de conmutación alrededor de rate 1. Con KEY **OFF** la salida
  es bit-exacta al path directo (remuestreo lineal).
- **FR-006**: Sin flanger audible cerca de `rate ≈ 1`: al no conmutar de camino
  (FR-005) no hay doble cambio de camino con sus artefactos de latencia; la
  continuidad la aporta el propio motor.
- **FR-007**: Toggle KEY en marcha aplica un crossfade de **1024 frames**
  (≈ 21.3 ms a 48 kHz) de rampa propia, **simétrico** (entrada y salida),
  entre path directo y stretch; no cambia `m_playedFrames` ni dispara seek; no
  rompe EQ/filtro/gain posteriores.
- **FR-018**: El crossfade mezcla **el mismo instante de material** en las dos
  rutas: el motor se alimenta `Δ` muestras de fuente **por delante** del cursor
  (`Δ` = retardo efectivo calibrado, FR-004), de modo que su salida y el path
  directo hablan del mismo punto de la fuente. Sin esto, el contenido se
  desliza ~30 ms hacia delante durante la transición (un "tropiezo" audible).
  La calibración se hace **en el hilo de UI, al construir el deck**: el hilo de
  audio no mide, no asigna, no bloquea ni hace I/O (SC-008).
- **FR-019**: La compensación de fase audible que publica el sync usa el
  retardo **calibrado** (FR-004), no `getLatency()`: con `getLatency()` el
  error de fase entre un deck con KEY y otro sin KEY es de ~7 ms a `rate=1.2`.
- **FR-020** (transición sin batido): el crossfade **no puede** sumar dos
  afinaciones distintas —con KEY OFF la salida es varispeed (`f0 × rate`) y con
  KEY ON es `f0`—, así que la transición actual late a `|rate−1| × f0`
  (96 Hz a `rate=1.2` con un fixture de 480 Hz). La transición de la v1 lo
  **mide y publica** (SC-003); la eliminación del batido exige un camino único
  con un *glide* de los parámetros del motor y se sigue en su propio ticket.
- **FR-008**: `m_rate` sigue siendo la única fuente de verdad del tempo (pitch
  slider, `setAudioRate` de sync y pitch bend multiplican sobre él); el key lock
  solo cambia la *interpretación* del resample, no el cursor ni la fase.
- **FR-009**: Scratch mantiene su resampler (Hermite/sinc) y queda fuera del key
  lock; al soltar, el path normal retoma el modo KEY vigente con continuidad.
- **FR-010**: El key lock **sí** aplica dentro de un loop activo: la ventana
  del loop se lee a `rate=1.0` (raw) y se alimenta al motor, que produce el
  bloque audible; las transiciones entrar/salir del loop usan el mismo
  crossfade simétrico.
- **FR-011**: Key analysis corre en el hilo del `WaveformAnalyzer` (hilo
  aparte), reutilizando el `monoBuf` ya acumulado, sin segundo decode. El
  detector vive en `keyanalyzer.cpp` (no publicado) (envuelve `qm-dsp GetKeyMode`).
- **FR-012**: Detección con `qm-dsp GetKeyMode` (Chromagram + Krumhansl-Schmuckler),
  afinación A=440 Hz; se rechaza el resultado si la confianza máxima queda bajo
  umbral (0.5) → "sin key" (Camelot vacío).
- **FR-013**: Mapeo determinista `GetKeyMode` (índice 0–24) → notación Camelot
  `1A`–`12B`, con tabla propia de teoría musical en `keynotation.h` (no publicado),
  verificada por fixture.
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

Estado de cada criterio: **verificado** (hay un test en el repo que lo
comprueba y pasa) o **abierto** (no hay oráculo automatizado que lo cubra).

- **SC-001** (continuidad de pitch): con KEY ON el pitch no sigue a la tasa
  (440/480 Hz conservados) mientras el tempo sí escala. **Verificado** con
  fixture de seno de 480 Hz en `keylock_loop_test.cpp` (no publicado) (rate 1.2 dentro
  de loop: 480 Hz con KEY, 576 Hz sin KEY). **Abierto**: el barrido continuo
  0.5→1.5 con tolerancia de cents (SC del enunciado original) no tiene oráculo
  automatizado.
- **SC-002** (bypass bit-exacto): con KEY **OFF** la salida es idéntica bit a
  bit a la del path lineal actual. **Parcialmente verificado**: el path KEY OFF
  es el remuestreo lineal sin tocar (`keylock_audio_test.cpp` (no publicado) comprueba
  el tono, no la identidad bit a bit bloque a bloque). Con KEY ON ya no aplica:
  el motor está siempre en el camino (FR-005).
- **SC-003** (transición sin artefactos): toggle ON→OFF→ON sin clic medible en
  el borde del crossfade. **Parcialmente verificado**: `keylock_click_test.cpp` (no publicado)
  mide el salto máximo muestra a muestra (`maxStep`) en el borde del crossfade, en el
  path normal y en el de loop, y lo compara contra la referencia en régimen con
  un umbral (`kFadeRatio`); incluye además la **prueba de la prueba**: se
  reejecuta con el crossfade a 0 frames y el test **debe fallar** (si no, el
  sensor está muerto). Cerrado en `a0a837e` ([DJM-28](/DJM/issues/DJM-28)).
  **No verificado**: el criterio "sin fase *flangerizada* audible" de US2 no se
  cumple: el crossfade suma dos afinaciones (FR-020) y late a 96 Hz medido
  ([DJM-41](/DJM/issues/DJM-41)). Además, hasta que FR-018 llegue, el
  contenido se desliza ~30 ms durante la transición (tropiezo). Los oráculos
  C1 (sin deslizamiento) y C4 (fase de sync) están definidos en
  `research.md` y ambos **fallan hoy**.
  **Fila de evidencia**: lo medido, lo no escuchado y la fecha de este
  criterio viven en `evidence/keylock-toggle-crossfade.evidence` (no publicado), citada
  aquí como evidencia:keylock-toggle-crossfade. La regla de esa fila (quien
  escribe, los plazos y qué pasa cuando caduca) está en
  la evidencia de QA (../../docs/qa-evidencia.md, no publicado).
- **SC-004** (key de fixtures): arpegios/acordes sintéticos con fundamental
  conocida se clasifican en el Camelot esperado (Do mayor→`8B`, La menor→`8A`,
  más una muestra por cada modo si el fixture lo permite); fixture "sin tonalidad
  clara" (ruido/noise) → "sin key" o `—`. **Verificado** en
  `keyanalysis_test.cpp` (no publicado).
- **SC-005** (mapeo Camelot): la tabla índice→Camelot es biyectiva y verificada
  por fixture; no hay índices huérfanos ni colisiones. **Verificado**
  (`keyanalysis_test.cpp` (no publicado) comprueba 24 códigos distintos y valores de
  referencia).
- **SC-006** (caché): análisis + key se guardan en sidecar; recargar la pista
  lee la key sin re-decodificar (verificado por conteo de llamadas o timestamp
  de sidecar). **Verificado** en `grid_cache_test.cpp` (no publicado).
- **SC-007** (latencia acotada): latencia del motor de stretch ≤ 40 ms.
  **Verificado por medición directa**: `getLatency()` = 1024 muestras
  (≈ 21.3 ms a 48 kHz) con la configuración real del deck. **Matizado**
  ([DJM-36](/DJM/issues/DJM-36)): el retardo efectivo en streaming medido sobre
  el audio renderizado es de **27–37 ms** (sigue bajo el techo de 40 ms), y ese
  —no `getLatency()`— es el que hay que compensar (FR-004, FR-018). Pendiente
  la métrica de retardo por impulso sobre el audio renderizado (no solo la cifra
  que reporta el motor).
- **SC-008** (RT sin alloc): cero malloc/locks/I-O en el callback con KEY ON
  (barrido + toggle). **Abierto**: el arnés de instrumentación RT existe
  (`loop_rt_test.cpp` (no publicado)) pero cubre el camino de loop/PCM cache, no el
  camino de key lock. En el camino de key lock los buffers son miembros
  preasignados de `Deck` y el motor se construye en el constructor, pero falta
  el oráculo que lo afirme. Ojo: el path general de reproducción sí reasigna
  `m_mixBuffer` (`deck.cpp` (no publicado)) — es deuda RT heredada, ya auditada en
  `docs/loop-validation.md`, y no la introduce esta feature.
- **SC-009** (regresión): suites existentes (sync, scratch, loop, eq/filter)
  verdes. **Verificado** por `ctest`; las capturas del deck con KEY ON/OFF y key
  visible en deck/biblioteca quedan en el cierre de F4.

## Entidades y decisiones

Entidades que existen hoy en el repo:

- `Deck::m_keylock` — `RubberBand::RubberBandStretcher` por deck, creado en
  el constructor de `Deck` (`deck.cpp` (no publicado)), alimentado desde el hilo de audio
  con un acumulador de entrada de promedio exacto (sin drift) y consultado con
  `available()` antes de `retrieve` (sin dropouts).
- `Deck::m_kl*` — estado del camino de key lock: acumuladores de entrada,
  contador de crossfade, buffers preasignados (`m_klInL/R`, `m_klOutL/R`,
  `m_klFadeBuf`, `m_klLoopIn`) y `m_klLatencyOut` (latencia medida del motor).
- `KeyAnalyzer` / `KeyAnalysis` — detector de tonalidad (`keyanalyzer.cpp` (no publicado),
  `keynotation.h` (no publicado)): índice `GetKeyMode` + Camelot + confianza.
- `TrackMeta.analyzedKey/keySource` — extensión cacheable
  (`waveformcache.h` (no publicado)).

[Contrato](contracts/keylock.md), [plan](plan.md), [tareas](tasks.md),
[research](research.md).

Decisiones propias: **Rubber Band** (GPL-2.0-or-later) como motor de
time-stretch, en modo real-time con transientes mixtos; motor siempre en el
camino con KEY ON (sin banda de conmutación); crossfade propio de 1024 frames
simétrico; key lock también dentro del loop activo; detección con `GetKeyMode`
sobre `monoBuf`; precedencia tag>análisis; key lock fuera del scratch. No se
atribuyen estas políticas exactas a Serato sin evidencia adicional.

Nota de licencia: el motor es GPL, igual que `qm-dsp`. Mientras siga en el
árbol, todo binario distribuido debe traer el código fuente completo
(`docs/promise.md`, `docs/business-model.md`); la ruta del Pro sustituye el
motor, no lo licencia.

## Decisión de UI (2026-10-19)

- El botón KEY va en el DeckPanel **arriba del botón SYNC** (estilo Traktor):
  botón pequeño con acento del deck, toggle con estado iluminado cuando el
  key lock está activo, ToolTip "Key Lock".
- Al lado del BPM (misma fila o la del pitch) se muestra la tonalidad Camelot
  cuando el análisis la conoce (F3).

