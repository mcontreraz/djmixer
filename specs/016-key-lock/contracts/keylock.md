# Contrato de Deck: key lock + key analysis

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

Estado: **implementado** (motor Rubber Band). El botón KEY y el badge de key
existen en `DeckPanel.qml`; el motor es `RubberBand::RubberBandStretcher` por
deck (`deck.cpp` (no publicado)). Reconciliado con el código el 2026-10-19.

## Key lock (propiedades y acciones)

| Nombre | Tipo/unidad | Significado |
|---|---|---|
| `keyLock` | bool | ON/OFF por deck. OFF = varispeed actual (path directo) |
| `setKeyLock(bool)` | slot | Conmuta el modo |

- `setKeyLock(bool)`: conmuta el modo. El flag atómico lo lee el hilo de audio
  al inicio de cada bloque. El cambio de path lleva un crossfade de 1024 frames
  (≈ 21.3 ms a 48 kHz), de rampa propia, en entrada y en salida. No cambia
  `m_playedFrames`, no dispara seek, no resetea EQ/filtro/gain.
- `keyLockChanged` se notifica en el hilo UI en el momento del toggle. El LED
  refleja el estado **solicitado**: no hay un estado `pending` ni una
  confirmación separada desde el hilo de audio (el motor no puede fallar en un
  toggle; el camino de audio toma el flag en el bloque siguiente).

## Key analysis (resultado y precedencia)

| Nombre | Tipo/unidad | Significado |
|---|---|---|
| `key` (existente) | QString | Display Camelot `1A`–`12B`, o vacío |
| `keySource` | enum Tag/Analysis/None | Procedencia del valor mostrado |
| `analyzedKey` | QString | Resultado crudo de la detección (independiente del tag) |

Precedencia (FR-014): `key = tag ? tag : analyzedKey`. El `analyzedKey` se
calcula al terminar el análisis y se persiste en `WaveformCache` (sidecar); un
resultado de generación vieja se descarta.

## Invariantes RT

- El camino de key lock no asigna memoria, no bloquea y no hace I/O en el
  callback: los buffers (`m_klInL/R`, `m_klOutL/R`, `m_klFadeBuf`, `m_klLoopIn`)
  son arrays miembro preasignados de `Deck`, y el motor se construye una vez,
  en el constructor.
- `m_rate` sigue siendo la única fuente de verdad del tempo; el key lock solo
  cambia la interpretación del resample, no el cursor ni la fase musical.
- Con KEY OFF la salida es bit-exacta al path directo. Con KEY ON el motor queda
  siempre en el camino (incluso a `rate == 1.0`): no hay conmutación de camino
  ni banda de transparencia alrededor de rate 1.

## Alcance y exclusiones v1

- Scratch usa su propio resampler (Hermite/sinc) y no pasa por el key lock.
- El key lock **sí** aplica dentro de un loop activo: la ventana del loop se
  lee a `rate=1.0` (raw) y se alimenta al motor.
- Key shift/transposición (±12 semitonos) no es parte de este contrato.

## MIDI

Acción lógica propuesta: `key_lock` (toggle por deck). Note-on/press ejecuta
una vez; note-off/release no alterna. Feedback nunca llama a `setKeyLock`.
Los alias ACI de Serato (`SetDeckKeyLock`, `set_deck_keylock`) son evidencia de
interfaz, no bytes MIDI para Vestax. **Pendiente**: hoy `keylock` figura entre
las acciones reservadas de `midicontroller.cpp` (no publicado); el mapeo MIDI del key lock
no está implementado (tarea T014 de [tasks.md](../tasks.md)).

## Compatibilidad

El key lock no reescribe tags musicales, grid, cues ni sidecars (salvo el key
analizado en su propio campo). La posición visible y `effectiveBpm` siguen
derivándose del tempo; el key lock solo fija el tono, no el BPM mostrado. La
fase que se publica para sync es la **audible** (cursor − rate × latencia del
motor), para que un deck con KEY y otro sin KEY se comparen en la misma moneda.
