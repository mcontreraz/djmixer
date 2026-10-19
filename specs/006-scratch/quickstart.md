# Quickstart: Scratch

## 1. Drag atrás en waveform (SC-001)

WAV sonando, arrastrar la grande a la izquierda 5 s de audio → posición
retrocede ~5 s y se escucha reversa; soltar quieto → retoma normal.

## 2. Spin en plato (SC-002)

Flick rápido atrás en el JogWheel y soltar → rebobinado audible ≥600 ms
decayendo; la línea roja gira atrás.

## 3. Sin regresión (SC-003)

Click simple sigue siendo needle; play/pause/cue intactos (autotest verde).

## 4. Autotest

`DJMIXER_AUTOTEST=<wav>`: scratchTo adelante/atrás programático (±5 s),
`scratchRelease` con spin y resume; asserts de posición por fase.
