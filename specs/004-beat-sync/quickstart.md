# Quickstart: Beat Sync

Valida F4 de punta a punta.

## 1. Build + autotest

```bash
cmake --build build -j
DJMIXER_AUTOTEST="<HOME>/Downloads/Deep Garage Groove (Breakdown & Drop) (Extendido).wav" \
  ./build/djmixer.app/Contents/MacOS/djmixer
```

Esperado (SC-001/SC-002/SC-005): `exit 0`, con aserciones nuevas: convergencia de fase (< ±20 ms),
octava reconocida, restauración de rate al desactivar, deck sin grid → solo tempo.

## 2. Visual (SC-003)

```bash
DJMIXER_SCREENSHOT=/tmp/f4-sync.png ./build/djmixer.app/Contents/MacOS/djmixer
```

Con sync activo en ambos decks: play/pausa responde al instante (< 200 ms).

## 3. Convergencia manual

Carga el mismo WAV en A y B (misma BPM), fases distintas → activa sync en B → los beats caen
juntos y se mantienen (sin drift audible) 30 s.

## 4. Octava

Carga un tema a 70 y otro a 140 → sync → se alinean al mismo tempo (no quedan 70 vs 140).

## 5. Restauración

Desactiva sync en B → su rate vuelve al valor manual sin click.
