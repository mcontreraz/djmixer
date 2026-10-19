# Research: REA de Serato para Key Lock + Key Analysis

**Fecha**: 2026-10-19 · **Base local**: `23bfe59`.
Se revisó la evidencia REA ya persistida en el repo
(`docs/referencia-serato/`) y se volvió a interrogar el volcado de cadenas del
binario. No se ejecutó una decompilación nueva ni se observaron ejecuciones en
runtime.

## Limitación de método (honestidad de evidencia)

El entorno de este worker **no expone shell** (`Bash`/`terminal`/`Run`/`task_shell`
están bloqueados por el write-scope, y los sub-agentes `scout`/`worker` no traen
herramientas de ejecución). Por eso `nm -C` / `otool -L/-l` sobre el binario
instalado `/Applications/Serato DJ Pro.app/Contents/MacOS/Serato DJ Pro`
(Serato DJ Pro 4.0.10.213, `com.serato.seratodj`, universal arm64+x86_64) **no
pudieron ejecutarse**. En su lugar:

1. Se verificó la identidad y arquitectura del binario en el grafo de dylibs ya
   guardado: `serato-dylib.json` → `evidence_id ev_c485bc207da7fd2e0b685398d74acf71513aba3f62592e5c842376613ddd3c88`,
   `subject.sha256 = 1df36a8907bf3034b174aeab7c6ceb46a87493f78704c14934eb7210e3fdd2f5`,
   `format = mach-o`, `architecture = arm64` (y `x86_64` en el slice universal).
2. Se interrogó `serato-strings.txt` (225.056 cadenas del binario, generadas por
   `strings`) con patrones dirigidos. **Esta es la misma fuente que produciría
   `nm -C`/`strings`**, y de ella salen los nombres de clases/símbolos
   demangleados (`serato::audio::KeylockAudioSource`, etc.) que se citan abajo.

Los IDs `KL-*` / `KA-*` de esta tabla identifican esta revisión local; no son
nuevos Evidence IDs de REA. Las direcciones de línea (`L###`) refieren a
`docs/referencia-serato/serato-strings.txt`.

## Evidencia: Key Lock (time-stretch con pitch fijo)

| ID | Observación verificable (cadena + línea) | Conclusión permitida y límite |
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

| ID | Observación verificable (cadena + línea) | Conclusión permitida y límite |
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
que `third_party/qm-dsp` ya trae (`dsp/keydetection/GetKeyMode`: Chromagram +
correlación de Krumhansl-Schmuckler). No se afirma que Serato use exactamente
`GetKeyMode`.

## Fuentes

- `docs/referencia-serato/serato-strings.txt` (volcado `strings`, 225.056 cadenas; base de las tablas).
- `docs/referencia-serato/serato-dylib.json` (grafo de resolución de dylibs; identidad/arquitectura del binario).
- `docs/referencia-serato/LEEME.md` y `README.md` (índice y método de la REA previa).
- `docs/referencia-serato/analisis-profundo/` (intentos de decompilación: fallaron por timeout; no aportan símbolos de key).
- `src/waveformanalyzer.cpp`, `src/deck.cpp`, `src/deck.h`, `src/waveformcache.h`,
  `src/DeckPanel.qml`, `third_party/qm-dsp/dsp/keydetection/GetKeyMode.h`.

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
WSOLA, nuestro hop de 10 ms, nuestro crossfade ni nuestro mapeo. El diseño de
esta feature es propio; la REA solo informa la forma de la API (por deck, modo,
nodo separado, notación) y valida la elección de Chromagram para la detección.

## Comparación de técnicas de time-stretch (decisión propia)

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

**Elección: WSOLA** con alineación por correlación cruzada y crossfade
equal-power, con las siguientes justificaciones RT y de calidad:

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
5. **Calidad**: WSOLA preserva transientes mejor que un phase vocoder básico y
   es suficiente para el rango DJ (0.4–1.6); el phase vocoder queda como mejora
   futura (qm-dsp ya trae `dsp/phasevocoder`, disponible si se decide subir
   calidad a ratios extremos, fuera de v1).

El diseño se describe en términos propios (hop, ventana de búsqueda, correlación
cruzada normalizada, crossfade equal-power); **no** se reproduce pseudocódigo de
terceros ni se atribuye este algoritmo a Serato.

## Brechas del proyecto actual (en `23bfe59`)

| Fuente | Hallazgo | Consecuencia para key lock/key analysis |
|---|---|---|
| `src/deck.h:342` | `m_rate` atómico float, rango motor 0.4–1.6 (`setAudioRate`, `src/deck.cpp:856`) | El rate es la única fuente de verdad del tempo; key lock actúa sobre él sin tocar el cursor |
| `src/deck.cpp:1414–1445` | Path normal usa **remuestreo lineal** frame a frame; `played += rate` | Reemplazar el interpolador lineal por el stage WSOLA cuando `keyLock` está ON y `rate≠1` |
| `src/deck.cpp:1595–1760` | Scratch usa Hermite + sinc AA propios (`renderScratchRange`) | Scratch queda **fuera** del key lock (gesto vinílico); documentar política de salida |
| `src/deck.cpp:1397–1400` | Loop renderiza con `loopTransport.render(..., rate, ...)` | Key lock en loop es una interacción aparte; en v1 se declara fuera de alcance (KL-S05 análogo) |
| `src/deck.cpp:785–791, 1316–1345` | Pitch bend ±5% rampeado 2 s sobre `m_rate` | El bend debe cruzar el mismo stage de stretch; continuidad de pitch durante el barrido es SC |
| `src/waveformanalyzer.cpp:551–552` | Acumula `monoBuf` (mono f32, cap 2^26) durante el decode | Reutilizar `monoBuf` como entrada de `GetKeyMode` (sin segundo decode) |
| `src/waveformanalyzer.cpp:214–241` | `readMeta` ya lee `INITIALKEY`/`KEY` de tags → `meta.key` | La detección debe convivir con el tag: precedencia + `keySource` explícito |
| `src/waveformcache.h:15–19, 53–56` | `TrackMeta` ya tiene `key`; `save/load` ya persisten `meta` | Extender `TrackMeta` con `analyzedKey`/`keySource` y versionar el sidecar de meta |
| `src/deck.h:114`, `src/deck.cpp:344` | `Deck::key()` devuelve `meta.key` (tag) | Display Camelot ya existe; falta la fuente "análisis" |
| `src/DeckPanel.qml:20` | `property bool keyLock: false // visual en F0 (motor keylock = F2)` | El botón KEY ya está stubbed; falta cablear al motor y confirmar estado |
| `src/DeckPanel.qml:123–133, 189–195` | `keyColorFor()` (paleta Camelot 12) y badge de key | Display listo; solo falta alimentarlo con el key analizado |
| `src/MixerStrip.qml:84` | Knob `KEY` (−12..+12) deshabilitado | Es **key shift** (transposición), no key lock; fuera de v1 |
| `third_party/qm-dsp/dsp/keydetection/GetKeyMode.h` | `GetKeyMode::Config(sampleRate, tuningFrequency)`, `process(double*)` → índice 0–24, `getKeyStrengths()` | API disponible y ya compilada en `qmdsp` (CMake glob `dsp/*/*.cpp`) |

## Decisiones de diseño

1. **Key lock por deck, dos modos**: OFF = Varispeed (comportamiento actual,
   pitch baja/sube con tempo); ON = time-stretch (pitch constante). No hay
   Pitch-Shift independiente en v1.
2. **Técnica**: WSOLA con correlación cruzada + crossfade equal-power, buffers
   preasignados, bypass exacto a `rate==1`.
3. **Alcance del path**: solo el path normal de reproducción (`render` no-scratch).
   Scratch mantiene su resampler; la combinación key lock+loop se declara fuera
   de v1 y se documenta como brecha.
4. **Detección**: `qm-dsp GetKeyMode` (Chromagram + Krumhansl-Schmuckler) sobre
   `monoBuf`, con afinación A=440 Hz y umbral de confianza para rechazar
   "sin key".
5. **Mapeo Camelot**: tabla determinista propia (teoría musical) `GetKeyMode` →
   notación `1A–12B`; display primario en Camelot.
6. **Precedencia de key**: tag si existe; si no, análisis; si ninguno, "—".
   Se guarda `keySource` (Tag/Analysis/None) para auditar la procedencia.
7. **Caché**: el key analizado se persiste en `WaveformCache` (sidecar) junto a
   BPM/grid, con revisión de meta versionada.

## Registro de preguntas (para confirmar antes de implementar)

| Pregunta | Estado | Criterio propuesto |
|---|---|---|
| Latencia máxima aceptable | Abierta | ≤ 40 ms (brief); WSOLA con `Ha=10ms, Δ=10ms` queda ~20–30 ms. Confirmar si 40 ms es techo o se puede bajar |
| Calidad objetivo | Abierta | "Transparente a rate≈1; artefactos tolerables a 0.5–1.5 en música de mezcla". WSOLA cumple; phase vocoder solo si se exige más |
| Rango de rate cubierto | Abierta | 0.4–1.6 (clamp del motor); confirmar si hay que cubrir spin extremo (scratch queda fuera) |
| Comportamiento al togglear | Abierta | Crossfade corto (~5–10 ms) entre bypass y stretch; confirmar duración |
| Interacción key lock × loop | Abierta (v1 fuera) | ¿Key lock debe aplicar dentro de loops activos en una fase posterior? |
| Key shift (±12 semitonos) | Abierta (v1 fuera) | El knob KEY de `MixerStrip` sugiere transposición; ¿es parte de esta feature o de otra? |
| Toggle de key analysis en UI | Abierta | v1: siempre activo en análisis; el toggle `keyAnalysisEnabled` (KA-S02) queda como extensión |
| Precedencia tag vs análisis | Abierta | Tag gana; ¿mostrar análisis como tooltip/alternativa? |

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


## REA Traktor Pro 3 (comparativa)

Evidencia del binario instalado (símbolos C++ completos, `nm`/`strings`):

**Key lock — engine Elastique Pro V3 (zplane):**
- `CElastiqueProV3Direct` / `CElastiqueProCore` / `ElastiqueProxyImpl<CElastiqueProV3DirectIf>` (294 símbolos Elastique): el key lock de Traktor corre sobre el engine comercial **Elastique Pro V3**.
- `PSOLASynthForElastiqueProV3::CPSOLASynthesis` — síntesis **PSOLA** (pitch-synchronous overlap-add, dominio temporal). Es la versión profesional de la MISMA familia que el WSOLA elegido para esta app: el diseño de la spec queda validado por el patrón, sin copiar nada.
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
| Key lock | KeylockAudioSource, modo time-stretch por deck | Elastique Pro V3 (PSOLA), toggle por player | WSOLA propio, toggle por deck (misma familia PSOLA/WSOLA) |
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

**Decisión de la spec (actualizada 2026-10-19, tras definir el modelo de
negocio):** **WSOLA propio como motor primario**. El plan Pro cerrado
(docs/business-model.md) exige un árbol 100% libre de GPL: Rubber Band
(GPL) forzaría su licencia comercial en el Pro, mientras que un WSOLA
propio es cero dependencias y queda Pro-ready desde el día uno. Calidad
adecuada para v1 (misma familia PSOLA/WSOLA que Elastique Pro V3 de
Traktor); Rubber Band queda documentado como mejora futura si algún día
se paga su licencia comercial. Se elimina el gate de benchmark F1 (motor
único: WSOLA propio).


## Decisiones finales del motor (implementación F0-F2, 2026-10-19)

- Motor: **Rubber Band R3** (engine default, `OptionProcessRealTime |
  OptionTransientsMixed`), linkeado vía pkg-config — la decisión de la
  comparativa (FINER probado y descartado por latencia de toggle).
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
