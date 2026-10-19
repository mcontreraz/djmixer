# Quickstart: Cue Points (CDJ)

## 1. Return (SC-001)

WAV sonando en deck 1, pulsar CUE → pausa en 00:00 (cue inicial) con error
<100 ms de audio. Mover a 30 s (needle), pulsar CUE → vuelve a 00:00.

## 2. Set + preview (SC-004)

Pausado a los 30 s, mantener CUE 2 s → suena 2 s (±200 ms); soltar → pausa
en 30 s. Pulsar CUE (tap) en pausa a los 45 s → cue queda en 45 s.

## 3. Persistencia (SC-002)

Con cue en 30 s, cargar otro tema y recargar el primero → CUE devuelve a
30 s (±100 ms).

## 4. Marca visual (SC-003)

Captura con cue en 30 s: marca visible en overview y en la grande a esa
posición; sin cue no hay marca.

## 5. Autotest

`DJMIXER_AUTOTEST=<wav>`: return-to-cue, set+preview temporizado,
persistencia por recarga, hot set/jump/clear y marca renderizada.

## 6. Hot cues en pads

Pausado a los 20 s, click en pad 3 → muestra "3"; click de nuevo → salta
a 20 s y suena; click derecho → vuelve a "+". Recargar el tema recupera
los números.
