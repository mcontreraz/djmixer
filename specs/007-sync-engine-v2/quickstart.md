# Quickstart: Sync Engine v2

## 1. Convergencia (SC)

Dos decks (124 vs 126 BPM, desfase medio beat), SYNC en el segundo.
Esperado: lock <4 s, phaseErr <0.02, sin bombeo audible.

## 2. Gate quantize

SYNC sin Q → tempos iguales, fases libres. Encender Q → alinea.
Esperado: comportamiento distinto y estable en ambos.

## 3. Enganche

Desfase cualquiera + SYNC → salto inmediato a fase (no rampa larga);
tarde → beat más cercano (1/8).

## 4. Autotest

`DJMIXER_AUTOTEST` extiende fases: escenario de convergencia con
`lockMs`/`phaseErr` impresos y umbrales; grep `umbral-sin-fuente` en repo debe dar vacío.
