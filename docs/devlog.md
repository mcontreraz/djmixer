# Notas de desarrollo — DJMixer

Fecha: 2026-10-19 · Documento de avance para visitantes, donantes y betatesters.
No es un plan: es lo que existe, lo que se ha medido y lo que falta.

---

## Qué es

DJMixer es un software de DJ **nativo** (C++17 + Qt 6 / QML) construido desde
cero, en la liga de Serato y Traktor. La razón de existir: que cualquier DJ que
quiera ser DJ pueda empezar **sin pagar mensualidades ni comprar software caro**.

- **Lite: gratis para todo el mundo, para siempre.** Sin precio, sin cuota, sin
  trial que expire. El compromiso completo está en [`promise.md`](promise.md).
- **Existirá un Pro de pago**, para lo que un DJ necesita cuando crece (stems,
  grabación, DVS), nunca para lo esencial de mezclar.
- Licencia **GPL-2.0-or-later**: el código fuente completo se entrega con cada
  binario. Por eso el "gratis para siempre" es creíble y no una promesa de
  marketing.
- El equipo de ingeniería es un **equipo de agentes de IA** (CTO, Coder, QA,
  Growth) orquestados con Paperclip, con una persona humana como dueño y
  decisor.

![Vista principal: dos decks, EQ de 3 bandas, mixer strip y waveform RGB con marcadores de beat](media/03-decks.png)

*Dos decks con la misma pista cargada: 129.26 BPM detectados, tonalidad 5B en
Camelot, 8 hot cues por deck, grilla de auto-loops, EQ de 3 bandas + filtro +
FX por canal, y el waveform con los marcadores de beat del grid.*

## Qué funciona hoy

| Área | Estado |
|---|---|
| Decks | 2 decks + crossfader, cue, seek, PFL por deck, 8 hot cues con persistencia en sidecar |
| Tempo | Pitch / tempo (±8/16/32 %), pitch-bend continuo, key lock (tempo sin cambiar tono) |
| Tonalidad | Análisis de tonalidad con nomenclatura Camelot, cacheado por pista |
| Beats | Detección de BPM y downbeat, beatgrid, y lectura del blob BeatGrid de Serato que un tema ya trae en su propio tag (MP3 GEOB / M4A) |
| Loops | Auto-loops sobre el beatgrid (1/8 … 16 beats), redimensionado diferido sin glitch |
| Sincronía | Motor de sync con correccion de fase; SyncLab para inspeccionar la alineacion del downbeat |
| Mezcla | EQ de 3 bandas, filtro y VU master (el botón FX está en la interfaz, sin efecto todavía) |
| Waveform | RGB con detalle a 200 buckets/s, overview en color, zoom 2–64 s |
| Scratch | Continuo, sin granulacion audible |
| MIDI | Mapeo completo, sensibilidad de jog, pitch-bend |
| Decodificacion | MP3, FLAC, AAC, MP4/M4A, Opus (el Opus dentro de un video se muda de contenedor por stream-copy, sin recodificar) |

![Biblioteca con 6 pistas, columna de BPM y de tonalidad](media/01-biblioteca.png)

*La biblioteca analiza sola: BPM y tonalidad de cada pista, con el cache en
disco. Las pistas de esta captura son audio sintetico de prueba, no musica
real.*

![SyncLab con el demo sintetico: DOWNBEAT ALINEADO](media/02-synclab.png)

*SyncLab: el motor de sincronizacion con un downbeat de A y otro de B, la fase
del compas y el desplazamiento medido en milisegundos. En el demo sintetico
queda en +0.0 ms.*

## Notas de desarrollo (lo que de verdad costó)

**1. El camino de loop del hilo de audio no asigna memoria.** Ni `malloc`,
ni locks, ni dependencia del hilo de UI. El camino es cache de PCM (la llena
un worker) + seqlock + colas SPSC de capacidad fija. Ojo con la frase: es el
camino de loop el que no asigna; el path general de playback reasigna buffer
cuando cambia el número de muestras, y eso esta anotado como limitacion
conocida, no como garantia. El test `no_absolute_paths` y el resto de la
suite de audio existen justo para que esto no se degrade en silencio.

**2. El key lock usa un motor de Rubber Band (GPL), no un time-stretch
generico.** Primero se prototipo WSOLA propio y se descarto: se ahogaba. El
motor final es Rubber Band en modo realtime con transients mixtos, con un
crossfade de 1024 frames de entrada y salida (implementado y ejercitado de
rebote por los tests de key lock; no hay test dedicado que afirme que no hace
clic, y eso queda anotado como laguna, no como garantia).
Se estudio el comportamiento observable de Serato y Traktor (clean-room: solo
comportamiento, nunca codigo copiado). Al repo sale el **analisis de
comportamiento**; la evidencia cruda de ingenieria inversa se queda en la
maquina de desarrollo, y el `.gitignore` del repo lo dice.

**3. El scratch no usa granulacion.** Es la diferencia entre un scratch que
suena a instrumento y uno que suena a efecto. Salio de mantener continuidad
entre callbacks de audio con sinc por tasa de sampleo.

**4. Los loops caen exactos sobre el beatgrid.** El resize es diferido: se
redimensiona cuando el loop llega al final del ciclo, no en caliente, y por
eso no hay click ni hueco. El mecanismo esta en `src/looptransport.cpp` con
la geometria musical en unidades explicitas (beats, frames, segundos).

**5. El sync se valida contra un oracle, no contra la propia salida.** El
SyncLab existe para eso: una pista se mueve, otra se comprueba, y el
desfase se lee en milisegundos.

**6. La deteccion de beats automatico todavia se esta validando contra pistas
reales.** El motor y la integracion estan, y el repo lo dice con todas sus
letras: cuando falla, el grid lo lleva la app y el fallo esta a la vista. No
se marca como verificado lo que no se ha verificado.

## Numeros

| | |
|---|---|
| Lineas de codigo propio (src + tests) | ~17.700 |
| Tests registrados en CTest | la lista viva: `ctest --test-dir build -N` (el numero cambia con cada commit) |
| Specs | la lista viva: `ls specs/` (spec → plan → tasks → contratos) |
| Commits | el historial completo: `git log --oneline` |
| Equipo | 4 agentes de IA + 1 humano |
| Stack | C++17, Qt 6 (QML), miniaudio, qm-dsp (GPL), BeatThis (MIT), ONNX Runtime, Rubber Band |

## Estado de la release

La Lite se publica **sin firmar** primero: el binario funciona, pero macOS
muestra el aviso de Gatekeeper porque no hay certificado de Apple Developer.
Firmarlo cuesta 99 USD/ano y **esa es exactamente la partida que se pide con
las donaciones** — no se puede firmar sin la cuenta, y no se compra la cuenta
con el tiempo del equipo.

Orden real: **donaciones → release sin firmar → firma cuando haya propina.**

## Que se pide

- **Capacidad de modelos (tokens).** Es el cuello de botella real: cada
  decision de motor, cada estudio de referencia y cada iteracion de tests
  consume tokens del equipo de agentes.
- **Un MIDI controller** para validar con hardware real (jog, PFL bajo
  presion, hot cues en vivo): el Latte y la presion no se automatizan.
- **La cuenta de Apple Developer** (99 USD/ano) en cuanto entre la primera
  propina, para que la descarga no salga con el aviso de Gatekeeper.

Detalles, redes y direccion de donacion: [`FUNDING.md`](../FUNDING.md).

El codigo fuente completo se publica junto con el primer binario (obligacion
de GPL-2.0-or-later). Hasta entonces el repositorio del código fuente es
privado: este devlog, las capturas y las especificaciones son lo que se puede
leer hoy.
