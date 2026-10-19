# Quickstart: Needle Search

## 1. Overview

Cargar el WAV (doble-click → deck 1), click a mitad del overview.
Esperado (SC-001): el tiempo del jog salta a ~01:57 (50% de 03:54) y el
playhead del overview se mueve ahí.

## 2. Waveform grande

Con el tema sonando, click en el borde derecho de la fila superior.
Esperado: salto al tiempo visible en ese punto.

## 3. Sin tema / fuera de rango

Click en overview vacío y en zona vacía de la grande.
Esperado (SC-003): no pasa nada, sin errores en log.

## 4. Autotest

`DJMIXER_AUTOTEST=<wav>` extiende la cadena: tras el [3] hace
`seek(50%)` y verifica posición en 48–52% → `exit 0`.
