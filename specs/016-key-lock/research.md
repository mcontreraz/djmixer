# Research: referencia de Serato para Key Lock + Key Analysis

> **Material de referencia local, no publicado.** La evidencia sobre la que
> se apoya este documento (volcado de cadenas, grafo de dylibs, índice de la
> previa) vive **solo en la máquina de desarrollo**: no está en el repo
> público. Aquí se publica el **método y la conclusión**, no el inventario de
> la evidencia. Ver referencia local (../../docs/referencia-local.md, no publicado).

**Fecha**: 2026-10-19 · **Base local**: `23bfe59`.
Se revisó la evidencia ya persistida en la maquina de desarrollo y se
volvio a interrogar las cadenas publicas del fabricante. No se hizo analisis
nuevo de binario ni se observaron ejecuciones en runtime.

## Limitación de método (honestidad de evidencia)

El entorno de este worker **no expone shell** (`Bash`/`terminal`/`Run`/`task_shell`
están bloqueados por el write-scope, y los sub-agentes `scout`/`worker` no traen
herramientas de ejecución). Por eso `nm -C` / `otool -L/-l` sobre el binario
instalado `/Applications/Serato DJ Pro.app/Contents/MacOS/Serato DJ Pro`
(Serato DJ Pro 4.0.10.213, `com.serato.seratodj`, universal arm64+x86_64) **no
pudieron ejecutarse**. En su lugar:

1. Se verificó la identidad y arquitectura del binario en el grafo de dylibs ya
   guardado en local (no publicado): `evidence_id ev_c485bc207da7fd2e0b685398d74acf71513aba3f62592e5c842376613ddd3c88`,
   `subject.sha256 = 1df36a8907bf3034b174aeab7c6ceb46a87493f78704c14934eb7210e3fdd2f5`,
   `format = mach-o`, `architecture = arm64` (y `x86_64` en el slice universal).
2. Se interrogó el volcado de cadenas del binario (`strings`, persistido en
   local y **no publicado**) con patrones dirigidos. **Esta es la misma fuente
   que produciría `nm -C`/`strings`**, y de ella salen los nombres de
   clases/símbolos demangleados (`serato::audio::KeylockAudioSource`, etc.) que
   se citan abajo.

Los IDs `KL-*` / `KA-*` de esta tabla identifican esta revisión local; no son
nuevos identificadores de evidencia. Las direcciones de línea (`L###`) son offsets
dentro del volcado local: sirven de trazabilidad interna en la máquina de
desarrollo y **no son verificables desde el repo público**, porque el volcado
no se distribuye.

## Evidencia: Key Lock (time-stretch con pitch fijo)

| ID | Observación verificable (cadena + offset local `L###`) | Conclusión permitida y límite |
|---|---|---|
| KL-S01 | `transport_pitch_keylock` (L3076) | Existe un control de transporte lógico `pitch_keylock`, distinto del fader de pitch |
| KL-S02 | `Keylock On` / `Keylock Off` (L2981–2982) | Dos estados con nombre de usuario; UI/estado distinto de "activado por rate" |
| KL-S03 | `keylock` (L24542) | Identificador corto del feature |
| KL-S04 | `KeylockCrossfadeTrigger` + `Whether the keylock crossfade should be triggered` (L22646–22647) | El algoritmo tiene un crossfade de transición (consistente con un overlap-add), y es configurable |
| KL-S05 | `KeylockAudioSource does not support looping` (L24142) | El nodo de key lock es un *AudioSource* separado con una restricción explícita de loop |
| KL-S06 | `serato::audio::KeylockAudioSource` (L84215) y `serato::audio::KeylockAudioSourceDelegate` (L82536) | Clase de audio dedicada (nodo del grafo), con delegate — el time-stretch vive en un nodo propio, no inline en el deck |
| KL-S07 | `SetDeckKeyLock` / `set_deck_keylock` / `remotehostscreen.v1.SetDeckKeyLock` / campo `keyLock` (L25184, L84924, L84925, L85147, L85149, L85428) | API de control remoto y por-deck del key lock: granularidad **por deck**, no global |
| KL-S08 | `Speed/Pitch macro, mode dependent control of Varispeed/Pitch-Shift/Time-Stretch playback.` (L2266) | Existen al menos tres modos de cambio de velocidad/tono: Varispeed (pitch+tempo juntos, = vinilo), Pitch-Shift (tono sin tempo) y Time-Stretch (tempo sin tono). Key lock corresponde a Time-Stretch |

**Qué NO prueba KL-S01..S08**: no identifica el algoritmo (WSOLA/SOLA/phase
vocoder), ni sus parámetros (hop, ventana, latencia), ni si usa librería de
terceros. El crossfade de KL-S04 es consistente con overlap-add pero no lo
demuestra. La ausencia de librerías `Elastique`/`ZPlane`/`PitchNTempo` en
`Contents/Frameworks` (vista en el listado del bundle) **no** descarta DSP
enlazado estáticamente dentro del Mach-O o dentro de `qt/` o los `.bin`.

## Evidencia: Key Analysis (análisis armónico)

| ID | Observación verificable (cadena + offset local `L###`) | Conclusión permitida y límite |
|---|---|---|
| KA-S01 | `analysis_set_key_detection` (L8137) | La detección de key es un ajuste del pipeline de *análisis* de pista (no del playback) |
| KA-S02 | `keyAnalysisEnabled` / `keyAnalysisEnabledChanged` (L69350, L69344) | Estado on/off observable con NOTIFY |
| KA-S03 | `musicalKey` / `musicalKeyChanged` (L67224, L67212) | Propiedad de modelo `musicalKey` con cambio notificable |
| KA-S04 | `serato::ui::qt::MusicalKey` (L71323) y `serato::ui::qt::MusicalTheory` (L71334) | Tipos UI dedicados para la tonalidad y la teoría musical |
| KA-S05 | `musical_theory::KeyNotation` (L71328, L71644) | La notación de key es un concepto separado del valor (distintas notaciones posibles) |
| KA-S06 | `CAMELOT`, `CLASSICAL`, `CLASSICAL_FLATS`, `CLASSICAL_SHARPS`, `OPEN` (L32694–32698) | Notaciones soportadas: Camelot es una de varias |
| KA-S07 | `Analysed key for: ` (L32738) | El análisis persiste un resultado de key por pista |
| KA-S08 | `The spectrum provided in Chromagram::AddEnergy isn't long enough.` (L32773) | La detección usa un **Chromagram** (igual familia que qm-dsp `GetKeyMode`), no un clasificador ML externo por sí solo |
| KA-S09 | `Skipping key analysis as the sample rate is too low (` (L32774) | Guarda de sample-rate mínima antes de analizar key |
| KA-S10 | `regex_search threw unknown exception during musical key conversion` / `regex_search failed during musical key conversion` (L32688–32689) + regexes de parsing (L32680–32686) | Hay un paso de *conversión* de cadenas de key (texto → valor), con parsing por regex |
| KA-S11 | `Cannot transpose an invalid key.` / `ToColor: Cannot translate an invalid key` / `ToString: Cannot translate an invalid key` (L32690–32692) | Existen operaciones de transposición y mapeo key→color/key→texto (consistentes con la rueda Camelot coloreada) |
| KA-S12 | `serato::musical_theory::TempoMap` (L71753+) | La teoría musical es un módulo compartido con el tempo (mismo dominio que beatgrid) |

**Qué NO prueba KA-S01..S12**: no identifica el perfil de correlación
(Krumhansl-Schmuckler vs otro), ni la frecuencia de afinación de referencia
(A=440 vs otra), ni el umbral de confianza para declarar "sin key". El hallazgo
KA-S08 (Chromagram) es la señal más fuerte de la técnica, y **coincide** con lo
que `qm-dsp` (no publicado) ya trae (`dsp/keydetection/GetKeyMode`: Chromagram +
correlación de Krumhansl-Schmuckler). No se afirma que Serato use exactamente
`GetKeyMode`.

## Fuentes

Material de referencia **local, no publicado** (ver
referencia local (../../docs/referencia-local.md, no publicado)):

- Volcado de cadenas del binario (`strings`): base de las tablas KL-*/KA-*.
- Grafo de resolución de dylibs: identidad y arquitectura del binario.
- Indice de la evidencia previa.
- Intentos de analisis del binario: fallaron por timeout; no aportan informacion sobre la key.

Material del repo (público y verificable):

- `waveformanalyzer.cpp` (no publicado), `deck.cpp` (no publicado), `deck.h` (no publicado), `waveformcache.h` (no publicado),
  `DeckPanel.qml` (no publicado), `qm-dsp/dsp/keydetection/GetKeyMode.h` (no publicado).

## Comparación útil

| Pregunta | Serato (evidencia guardada) | Decisión de esta app |
|---|---|---|
| Granularidad del key lock | `SetDeckKeyLock`, campo `keyLock` por deck (KL-S07) | ON/OFF por deck (botón KEY) |
| Modo del pitch | Varispeed / Pitch-Shift / Time-Stretch como modos (KL-S08) | Solo dos: OFF = Varispeed (actual, remuestreo) y ON = Time-Stretch. No Pitch-Shift independiente en v1 |
| Dónde vive el stretch | Nodo `KeylockAudioSource` con delegate (KL-S06) | Objeto DSP dedicado en el path no-scratch de `Deck::render` (preasignado, sin alloc) |
| Transición al activar | `KeylockCrossfadeTrigger` (KL-S04) | Crossfade acotado entre bypass y stretch para evitar click/flanger al togglear |
| Detección de key | `analysis_set_key_detection`, `keyAnalysisEnabled` (KA-S01/S02) | Se ejecuta al terminar `WaveformAnalyzer`, siempre (v1 sin toggle de UI; el toggle queda como extensión) |
| Representación | `musicalKey`, `KeyNotation`, `CAMELOT` (KA-S03/S05/S06) | `key` Camelot (1A–12B) como display primario; fuente tag vs análisis separada |
| Técnica de detección | Chromagram (KA-S08) | `qm-dsp GetKeyMode` (Chromagram + Krumhansl-Schmuckler), ya vendido en el repo |
| Persistencia | `Analysed key for:` (KA-S07) | Campo en `TrackMeta`, cacheado en `WaveformCache` (sidecar `.wfcache`) |

**Inferencia**, no hallazgo: que Serato tenga un `KeylockAudioSource`, un
crossfade de keylock y una notación `CAMELOT` no demuestra que use nuestro
motor de stretch, nuestro crossfade ni nuestro mapeo. El diseño de
esta feature es propio; la referencia solo informa la forma de la API (por deck, modo,
nodo separado, notación) y valida la elección de Chromagram para la detección.

## Comparación de técnicas de time-stretch (decisión propia, SUPERADA)

> Esta comparación llevó al prototipo de WSOLA propio. **No es la decisión
> vigente**: el motor que se despacha es Rubber Band (ver «Decisiones finales
> del motor», más abajo). Se conserva como registro del razonamiento y del
> por qué del cambio.

Restricciones impuestas por el repo: C++17/Qt6, PCM interno float estéreo 48 kHz,
callback de audio RT (cero malloc/locks/I-O), latencia ≤ ~40 ms, bypass
bit-exacto a `rate==1.0`, sin flanger a `rate≈1`, transparencia en música de
mezcla (material percusivo + armónico), rango de rate 0.4–1.6.

| Técnica | Coste CPU | Latencia | Calidad en música | Artefactos típicos | ¿RT sin alloc? |
|---|---|---|---|---|---|
| **WSOLA** (Waveform Similarity Overlap-Add) | Bajo–medio, O(N), sin FFT | Baja (hop + ventana de búsqueda, ~10–30 ms) | Buena en material mixto; transientes razonables | Doble-transiente y ligero "granular" a ratios extremos | Sí, con buffers preasignados |
| **SOLA** (Synchronous OLA) | Bajo | Baja | Menor que WSOLA | Más artefactos, menos robusto a transientes | Sí |
| **Phase vocoder (FFT)** | Alto (FFT por frame + IFFT) | Media–alta (ventana de análisis grande) | Mejor en armónicos sostenidos | "Smearing"/phasiness en transientes sin phase-locking; flanger si el bin se reutiliza | Sí pero exigente; FFT en el callback es pesado |
| **Granular simple (grain + envelope)** | Muy bajo | Baja | Pobre para música | Flanger/comb evidente | Sí |

**Elección en ese momento: WSOLA** con alineación por correlación cruzada y
crossfade equal-power, con las siguientes justificaciones RT y de calidad
— que el prototipo **no llegó a cumplir** (fallaba en transientes):

1. **Latencia acotada**: hop de análisis `Ha` y ventana de búsqueda `±Δ` fijan
   una latencia predecible `≈ Ha + Δ + (solape de crossfade)`, configurable para
   quedar ≤ 40 ms a 48 kHz (p. ej. `Ha≈10 ms`, `Δ≈10 ms`).
2. **Cero malloc**: el motor mantiene un anillo de entrada (historial fuente) y
   buffers de grano/correlación/crossfade **preasignados** una vez; el callback
   solo lee/escribe índices.
3. **Bypass exacto**: a `rate==1.0` el path no pasa por WSOLA; usa el remuestreo
   lineal actual (identidad del comportamiento existente, bit a bit).
4. **Sin flanger a rate≈1**: en una banda `|rate−1| < ε` se usa solape mínimo y
   alineación por correlación, de modo que los granos se superponen en fase; el
   crossfade equal-power evita el comb. Alternativa aceptada: conmutar a
   interpolación lineal dentro de la banda ε (continuidad asegurada por un
   crossfade de rampa corta entre modos).
5. **Calidad**: se estimaba que WSOLA preservaría transientes mejor que
   un phase vocoder básico; **el prototipo demostró lo contrario** en el
   material percusivo, que es el caso que decidía.

El diseño se describe en términos propios (hop, ventana de búsqueda, correlación
cruzada normalizada, crossfade equal-power); **no** se reproduce pseudocódigo de
terceros ni se atribuye este algoritmo a Serato.

## Brechas del proyecto antes de implementar

> Instantánea del estado del repo **antes** de implementar la feature. Las
> referencias de línea apuntan a ese commit (`23bfe59`), que ya no es
> alcanzable en el historial actual (el historial se reescribió al publicar el
> repo). Se conserva como registro de qué se encontró y qué se decidió hacer.

| Fuente | Hallazgo | Consecuencia para key lock/key analysis |
|---|---|---|
| `deck.h` (no publicado) | `m_rate` atómico float, rango motor 0.4–1.6 (`setAudioRate`) | El rate es la única fuente de verdad del tempo; key lock actúa sobre él sin tocar el cursor |
| `deck.cpp` (no publicado) | Path normal usa **remuestreo lineal** frame a frame; `played += rate` | Sustituir el interpolador lineal por el motor de stretch cuando `keyLock` está ON |
| `deck.cpp` (no publicado) | Scratch usa Hermite + sinc AA propios (`renderScratchRange`) | Scratch queda **fuera** del key lock (gesto vinílico); documentar política de salida |
| `deck.cpp` (no publicado) | Loop renderiza con `loopTransport.render(..., rate, ...)` | Interacción aparte; **resuelto en v1**: el motor también entra en el path del loop |
| `deck.cpp` (no publicado) | Pitch bend ±5% rampeado 2 s sobre `m_rate` | El bend debe cruzar el mismo motor de stretch; continuidad de pitch durante el barrido es SC |
| `waveformanalyzer.cpp` (no publicado) | Acumula `monoBuf` (mono f32, cap 2^26) durante el decode | Reutilizar `monoBuf` como entrada de `GetKeyMode` (sin segundo decode) |
| `waveformanalyzer.cpp` (no publicado) | `readMeta` ya lee `INITIALKEY`/`KEY` de tags → `meta.key` | La detección debe convivir con el tag: precedencia + `keySource` explícito |
| `waveformcache.h` (no publicado) | `TrackMeta` ya tiene `key`; `save/load` ya persisten `meta` | Extender `TrackMeta` con `analyzedKey`/`keySource` y versionar el sidecar de meta |
| `deck.h` (no publicado), `deck.cpp` (no publicado) | `Deck::key()` devuelve `meta.key` (tag) | Display Camelot ya existe; falta la fuente "análisis" |
| `DeckPanel.qml` (no publicado) | `property bool keyLock: false` (solo visual) | El botón KEY está cableado al slot; el LED refleja el estado solicitado |
| `DeckPanel.qml` (no publicado) | `keyColorFor()` (paleta Camelot 12) y badge de key | Display listo; alimentado con el key analizado |
| `MixerStrip.qml` (no publicado) | Knob `KEY` (−12..+12) deshabilitado | Es **key shift** (transposición), no key lock; fuera de v1 |
| `qm-dsp/dsp/keydetection/GetKeyMode.h` (no publicado) | `GetKeyMode::Config(sampleRate, tuningFrequency)`, `process(double*)` → índice 0–24, `getKeyStrengths()` | API disponible y ya compilada en `qmdsp` (CMake glob `dsp/*/*.cpp`) |

## Decisiones de diseño

1. **Key lock por deck, dos modos**: OFF = Varispeed (comportamiento actual,
   pitch baja/sube con tempo); ON = time-stretch (pitch constante). No hay
   Pitch-Shift independiente en v1.
2. **Técnica**: **sustituida**. Se empezó por WSOLA con correlación cruzada +
   crossfade equal-power, buffers preasignados y bypass exacto a `rate==1`;
   el motor que se despacha es Rubber Band (`04e8de0`), con el motor siempre en
   el camino con KEY ON.
3. **Alcance del path**: **ampliado**. Se declaraba fuera de v1 la combinación
   key lock + loop; quedó implementada (`1a99941`): la ventana del loop se lee
   a `rate=1.0` y se alimenta al motor. El scratch sigue fuera (usa su propio
   resampler).
4. **Detección**: `qm-dsp GetKeyMode` (Chromagram + Krumhansl-Schmuckler) sobre
   `monoBuf`, con afinación A=440 Hz y umbral de confianza (0.5) para rechazar
   "sin key".
5. **Mapeo Camelot**: tabla determinista propia (teoría musical) `GetKeyMode` →
   notación `1A–12B`; display primario en Camelot.
6. **Precedencia de key**: tag si existe; si no, análisis; si ninguno, "—".
   Se guarda `keySource` (Tag/Analysis/None) para auditar la procedencia.
7. **Caché**: el key analizado se persiste en `WaveformCache` (sidecar) junto a
   BPM/grid, con revisión de meta versionada.

## Registro de preguntas (cerradas en la implementación)

| Pregunta | Estado | Criterio |
|---|---|---|
| Latencia máxima aceptable | **Cerrada** | ≤ 40 ms (brief); medido 1024 muestras ≈ 21.3 ms a 48 kHz con la configuración real del deck |
| Calidad objetivo | **Cerrada** | "Transparente a rate≈1; artefactos tolerables a 0.5–1.5 en música de mezcla". Rubber Band en modo real-time con transientes mixtos es el motor probado en mezcla real |
| Rango de rate cubierto | **Cerrada** | 0.4–1.6 (clamp del motor); el spin extremo (scratch) queda fuera |
| Comportamiento al togglear | **Cerrada** | Crossfade de 1024 frames (≈21.3 ms a 48 kHz), simétrico, de rampa propia. La prueba de "no hace clic" está cerrada (`a0a837e`, con umbral y prueba de la prueba) |
| Interacción key lock × loop | **Cerrada** | El motor aplica dentro del loop activo (`1a99941`) |
| Key shift (±12 semitonos) | Abierta (v1 fuera) | El knob KEY de `MixerStrip` sugiere transposición; ¿es parte de esta feature o de otra? |
| Toggle de key analysis en UI | Abierta | v1: siempre activo en análisis; el toggle `keyAnalysisEnabled` (KA-S02) queda como extensión |
| Precedencia tag vs análisis | **Cerrada** | Tag gana; `keySource` queda publicado para auditar la procedencia |

No se bloquea una implementación original por no conocer el DSP propietario de
Serato; se impide etiquetarla como réplica exacta.


## Verificación contra el binario vivo (2026-10-19)

`strings "/Applications/Serato DJ Pro.app/Contents/MacOS/Serato DJ Pro"` (167.6 MB)
confirma los hallazgos del volcado persistido: 12 coincidencias de
`KeylockAudioSource` / `SetDeckKeyLock` / `keyAnalysis` / `Chromagram`
(clase `serato::audio::KeylockAudioSource`, su delegate, y el comando
`SetDeckKeyLock`). `nm` expone solo 4063 símbolos (binario strippead0): la
tabla C++ no está — la evidencia de diseño queda a nivel de cadenas/nombres,
no de direcciones de función.


## Referencia: Traktor Pro 3 (comparativa)

Evidencia del binario instalado (símbolos C++ completos, `nm`/`strings`):

**Key lock — engine Elastique Pro V3 (zplane):**
- `CElastiqueProV3Direct` / `CElastiqueProCore` / `ElastiqueProxyImpl<CElastiqueProV3DirectIf>` (294 símbolos Elastique): el key lock de Traktor corre sobre el engine comercial **Elastique Pro V3**.
- `PSOLASynthForElastiqueProV3::CPSOLASynthesis` — síntesis **PSOLA** (pitch-synchronous overlap-add, dominio temporal). Es la versión profesional de una familia de overlap-add; el motor que usa esta app es **Rubber Band** (phase vocoder con reset de fase en transientes), de otra familia, pero el patrón general —stretch temporal por deck con toggle— queda validado por la referencia, sin copiar nada.
- `TrackPlayer::onTimeStretchOn` / `RemixPlayer::onTimeStretchOn` + `TimeStretchingModule`: el toggle es **por player/deck** y activa el modo time-stretch (key lock) vs varispeed — igual semántica que `SetDeckKeyLock` de Serato.
- `PreferenceDialogPage::KeyLockRange` + `KeyLockWidget`: Traktor expone un **rango de key lock** configurable en preferencias (referencia para una futura preferencia de rango, fuera del alcance v1 de esta spec).

**Key analysis:**
- `PreferenceDialogPage::KeyDetection`: detección de tonalidad **integrada** con página de preferencias propia (el análisis de key es una feature de primera clase en Traktor).
- `camelot_number` / `camelot_letter`: notación **Camelot** (igual que Serato).
- "Replace empty musical key by defined musical key": política de key vacía → sustitución definida (referencia para el umbral de confianza: no inventar key con evidencia baja).
- `BrowserForm::executeAnalyse` + `ContentCollectionMgr::setTrackAnalysisLock`: el análisis se dispara desde la librería, con lock por pista (mismo patrón que el análisis en lote de esta app).

**Comparativa Serato vs Traktor (convergencia de diseño):**

| Aspecto | Serato | Traktor | Decisión de esta app |
|---|---|---|---|
| Key lock | KeylockAudioSource, modo time-stretch por deck | Elastique Pro V3 (PSOLA), toggle por player | Rubber Band (GPL), toggle por deck, con crossfade propio de 1024 frames |
| Key analysis | Chromagram + musicalKey + Camelot | KeyDetection integrada + Camelot | qm-dsp KeyDetector (chroma) + Camelot |
| Preferencias | — | KeyLockRange | fuera del alcance v1 (documentado) |

Ambos productos convergen en el mismo patrón (stretch temporal por deck +
detección cromática + Camelot): la spec 016 queda confirmada en diseño.


## Comparativa de librerías open source (web research 2026-10-19)

Benchmarks independientes (syshlted/timepitch-bench, tonos Shepard, 48 kHz,
bloque 512; arxiv "Variable-Rate Harmonic-Percussive TSM" 2026) y
comparativas de la industria (Capo, PitchTech, Audacity):

| Librería | Licencia | Motor | Calidad (error centro, Shepard) | CPU (realtime) | Latencia |
|---|---|---|---|---|---|
| **Rubber Band Library** (breakfastquay) | GPL-2.0+ / comercial | Phase vocoder con reset de fase en transientes | **±23 cents** (el mejor) | ~10× | configurable (modo RT) |
| **SoundTouch** (surina) | LGPL-2.1 | WSOLA-like | +106 cents en stretch puro, +170 en pitch (coloración) | ~350× (el mejor) | baja |
| **Signalsmith Stretch** | MIT | Phase vocoder moderno | ±43 cents | ~60× | ~60 ms (alta para DJ) |

Hallazgos clave:
- En **time-stretch puro** (el caso key lock), SoundTouch desplaza la
  envolvente espectral +106 cents (aclara el timbre) — falla el invariante;
  Rubber Band y Signalsmith quedan en ±19 cents.
- Solo **SoundTouch y Rubber Band** son real-time capables entre los
  motores abiertos (arxiv 2026).
- **Mixxx usa Rubber Band para su key lock** — referencia open source de
  la industria DJ.
- Rubber Band R3 (2022) agregó el modo de mayor calidad; el modo
  real-time con ventanas cortas da latencias aptas para mezcla.

**Decisión de la spec (2026-10-19, tras definir el modelo de negocio) —
SUPERADA por la implementación:** se llegó a elegir **WSOLA propio como motor
primario** con el razonamiento de que el plan Pro cerrado
(`docs/business-model.md`) exige un árbol 100% libre de GPL y un motor propio
sería cero dependencias. Ese razonamiento no se sostuvo al prototipar: el
prototipo **fallaba en transientes** (interferencia tipo saturación en los
beats), que es el caso más difícil del stretch naive. El motor que se despacha
es hoy Rubber Band (GPL) y la ruta del Pro **sustituye** el motor, no lo
licencia (ver `docs/business-model.md`).


## Decisiones finales del motor (implementación F0-F2, 2026-10-19)

Estas son las decisiones **vigentes**; mandan sobre cualquier párrafo anterior
de este documento.

- Motor: **Rubber Band** (GPL-2.0-or-later), enlazado por pkg-config **sin
  versión fijada** (el repo no fija la versión de la librería), en modo
  `OptionProcessRealTime | OptionTransientsMixed` con
  `setMaxProcessSize(512)`. El engine FINER se probó y se descartó por latencia
  de toggle (`117c768` → `64cf46b`).
- Cambio de motor: commit `04e8de0` ("motor de key lock → Rubber Band"), que
  también **borró** el módulo propio de stretch (header-only) y el fichero de
  test de DSP que lo acompañaban. Ninguno de los dos existe hoy en el repo.
- Latencia medida del motor: `getLatency()` = **1024 muestras ≈ 21.3 ms a
  48 kHz** (independiente del ratio 0.5–1.5), por debajo del techo de 40 ms.
  Se guarda en `Deck::m_klLatencyOut` y se usa para compensar la fase audible
  en sync.
- Integración: `setTimeRatio(1.0 / rate)` (¡el ratio es duración salida /
  entrada — invertirlo aceleraba al bajar el pitch!); alimentación con
  acumulador output×tasa (drift cero); consulta de `available()` antes de
  `retrieve` (el motor devuelve 0 si se pide de más).
- **Con KEY activo el motor queda SIEMPRE en el camino**: cruzar el 0 del
  pitch es el ratio pasando por 1.0 sin switches (la banda ε producía dos
  cambios de camino y sus artefactos de latencia). KEY off = path directo
  bit a bit.
- Toggles de KEY: motor "siempre caliente" (se alimenta y se descarta su
  salida cuando está off) + crossfades de entrada/salida de 1024 muestras
  contra el path directo.
- El key lock **sí** aplica dentro del loop activo: la ventana del loop se lee
  a `rate=1.0` (raw) y se alimenta al motor (commit `1a99941`).


## Desfase del motor y crossfade del toggle de KEY — decisión del CTO (DJM-36, 2026-10-19)

Esta sección **manda** sobre el párrafo "Latencia medida del motor" de
"Decisiones finales del motor" (que queda matizado) y sobre FR-004/FR-007/SC-003
de `spec.md`.

### Qué se midió (no estimado)

Sonda independiente contra el **mismo** build de Rubber Band que usa el deck
(`OptionProcessRealTime | OptionTransientsMixed`, `setMaxProcessSize(512)`,
48 kHz, 2 canales), con dos experimentos:

1. **Mapeo de contenido**: una ráfaga de 480 Hz en la fuente (frame 24000)
   feeding el motor con `setTimeRatio(1/1.2)`. La ráfaga aparece en el
   **índice de salida 19987** ≈ 24000/1.2 = 20000 (error < 15 muestras).
   → El motor **sí** entrega el contenido en su sitio: el desfase no está en
   el mapeo, está en **cuándo** está disponible la salida.
2. **Disponibilidad**, simulando el path real del deck (alimentar
   `frameCount × rate` muestras por bloque y consumir exactamente `frameCount`
   por bloque, como hace `Deck::render`): la salida del motor llega tarde.

| rate | desfase medido (frames de dispositivo) | en ms |
|---|---|---|
| 1.0 | +1794 (estable) | 37.4 ms |
| 1.2 | +1301 … +1598 (jitter ~±150) | 27.1 … 33.3 ms |

La medición de QA en el binario vivo coincide: el tono se fija **~37 ms**
después del toggle en el loop y **~27 ms** en el path normal
([DJM-34](/DJM/issues/DJM-34), [DJM-41](/DJM/issues/DJM-41)).

La sonda que produce estos números está en el repo:
`keylock_latency_probe.cpp` (no publicado) (compilar con
`clang++ -O2 -std=c++17 -o /tmp/keylock_probe tools/keylock_latency_probe.cpp $(pkg-config --cflags --libs rubberband)`).
Reproduce el desfase, el `getLatency()` declarado y la afinación de cada ruta.

`getLatency()` (= `getStartDelay()` = 1024 ≈ 21.3 ms) describe el **retardo de
salida inicial** del motor, no su latencia efectiva en streaming: el motor
necesita su ventana de análisis (≈1800 muestras de entrada) antes de poder
entregar el bloque que le toca. Por eso:

- el desfase real es **27–37 ms**, no 21.3 ms;
- la compensación de sync (`cursor − rate × m_klLatencyOut`, `deck.cpp`) queda
  **corta en ~330 muestras de fuente (≈7 ms a rate 1.2)** → un deck con KEY y
  otro sin KEY se comparan con ~7 ms de error de fase audible en un mix
  sincronizado.

### El batido de 96 Hz NO es un problema de alineación

Medido con Goertzel sobre las dos rutas con el mismo material:

| ruta | 480 Hz | 576 Hz |
|---|---|---|
| path directo (resample lineal a `rate=1.2`) | 0.000 | **0.208** |
| motor (`setTimeRatio(1/1.2)`) | **0.250** | 0.000 |

`setTimeRatio` cambia la **duración**, no la afinación (el pitch scale es otro
parámetro). El key lock funciona *por eso*: con KEY ON el motor conserva el
tono (480 Hz) mientras el tempo escala; con KEY OFF el path directo es
varispeed (576 Hz).

Consecuencia: **el crossfade de FR-007 suma dos afinaciones** (480 Hz y
576 Hz) y por eso late a |576−480| = **96 Hz**. Alinear las dos rutas en el
tiempo **no removes el batido**: es consecuencia de la arquitectura del
crossfade, no del desfase. La correlación entre el tramo de bypass y el de
stretch que pedía DJM-36 **no puede ser el oráculo**: son señales de distinta
afinación (su correlación es ~0 aunque estén perfectamente alineadas).

### Decisión

**Opción B — alimentar el motor con `Δ` muestras de fuente por delante del
cursor**, con `Δ` **calibrado** (no `getLatency()`):

- La calibración se mide **una vez, en el hilo de UI, al construir el deck**
  (una ráfaga por el motor: el hilo de audio no calcula, no asigna, no bloquea
  ni hace I/O).
- El motor se alimenta desde `cursor + Δ`; su salida queda así en fase con el
  path directo y el crossfade mezcla **el mismo instante** de material.
- La compensación de sync pasa a usar el retardo **calibrado**, lo que
  corrige de paso el error de fase de ~7 ms.

**Por qué B y no A**: A (retrasar el path directo)-costaría el retardo del motor
(≈30 ms) en **la latencia de salida de todos los decks, siempre**, incluso con
KEY OFF: elfeeling del jog y la respuesta del sync de la Lite se degradan y el
techo de 40 ms de SC-007 queda consumido por el.path de KEY OFF.

**Por qué B y no C**: el "tropiezo" (el contenido se desliza ~30 ms hacia
adelante durante el crossfade) es audible y el key lock es **esencial**
(está en la Lite por `docs/promise.md`): no se puede aceptar y documentar como
defecto conocido en una función esencial.

**Lo que esta decisión NO arregla**: el batido de 96 Hz (mixar dos
afinaciones). Va a su propio ticket con un rediseño de la transición (camino
único con un *glide* de los parámetros del motor, sin sumar dos señales de
distinta afinación). Para la Lite v1 el artefacto se **documenta** y SC-003
pasa de "verificado" a "parcialmente verificado" (sin salto de amplitud; con
batido documentado).

### Criterio de verificación (el oráculo que sustituye a SC-003)

| id | criterio | hoy |
|---|---|---|
| **C1** (sin deslizamiento) | a `rate = 1.0` (donde ambas rutas tienen la misma afinación) la **correlación cruzada** de la salida antes y después del toggle debe tener su pico en **lag 0 ± 64 frames (1.33 ms)** | pico en ~1794 frames → **falla** |
| **C2** (sin salto de amplitud) | el `maxStep` actual del crossfade, con su "prueba de la prueba" a 0 frames | pasa |
| **C3** (batido medido, no escondido) | la profundidad de modulación de amplitud durante la transición a `rate=1.2` se **mide y se publica**; para la v1 el criterio es que no empeore (≤ +20 % del valor medido hoy) | sin publicar |
| **C4** (fase de sync) | la posición publicada por un deck con KEY y otro sin KEY sobre el mismo material coincide dentro de **2 ms** | ~7 ms a `rate=1.2` → **falla** |

C1 y C4 son los que fallan hoy y son los que exige el arreglo. C1 es, en
formaExecutable, la "correlación entre el tramo de bypass y el de stretch" que
pedía DJM-36 — sólo que **a `rate = 1.0`**, que es el único caso en que la
correlación significa algo.

