# Contrato propuesto de Deck: key lock + key analysis

Estado: diseño, no API existente (el botón KEY y el badge de key ya existen en
`DeckPanel.qml` como visual; falta el motor). UI/teclado/MIDI deben converger aquí.

## Key lock (propiedades y acciones)

| Nombre | Tipo/unidad | Significado |
|---|---|---|
| `keyLock` | bool | ON/OFF por deck, confirmado por el motor (snapshot). OFF = varispeed actual |
| `keyLockPending` | bool | Toggle solicitado aún no confirmado (crossfade en curso) |
| `keyLockError` | enum | None/NoTrack (sin pista no hay key lock) |

- `setKeyLock(bool)`: conmuta el modo. Se aplica en el hilo de audio con
  crossfade de rampa corta (≤ ~10 ms). No cambia `m_playedFrames`, no dispara
  seek, no resetea EQ/filtro/gain.
- `keyLockChanged` se notifica en el hilo UI desde snapshot. El LED solo se
  enciende con confirmación del motor, no con el click.

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

- `KeylockStage` no asigna memoria, no bloquea y no hace I/O en el callback;
  buffers preasignados al cargar la pista.
- `m_rate` sigue siendo la única fuente de verdad del tempo; el key lock solo
  cambia la interpretación del resample, no el cursor ni la fase musical.
- Bypass bit-exacto a `rate==1.0`; banda `|rate−1|<ε` sin flanger.

## Alcance y exclusiones v1

- Scratch usa su propio resampler (Hermite/sinc) y no pasa por el key lock.
- Key lock dentro de un loop activo queda fuera de v1 (el loop usa su render
  actual). Se registra como brecha, no como fallo.
- Key shift/transposición (±12 semitonos) no es parte de este contrato.

## MIDI

Acción lógica propuesta: `key_lock` (toggle por deck). Note-on/press ejecuta una
vez; note-off/release no alterna. Feedback nunca llama a `setKeyLock`.
Los alias ACI de Serato (`SetDeckKeyLock`, `set_deck_keylock`) son evidencia de
interfaz, no bytes MIDI para Vestax.

## Compatibilidad

El key lock no reescribe tags musicales, grid, cues ni sidecars (salvo el key
analizado en su propio campo). La posición visible y `effectiveBpm` siguen
derivándose del tempo; el key lock solo fija el tono, no el BPM mostrado.
