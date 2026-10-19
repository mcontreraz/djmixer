# Quickstart: Real-time Beat Detector + Zapateo

## 1. Build + regresión

```bash
cmake --build build -j
DJMIXER_AUTOTEST="<HOME>/Downloads/Deep Garage Groove (Breakdown & Drop) (Extendido).wav" \
  ./build/djmixer.app/Contents/MacOS/djmixer
```

Esperado: exit 0 (el detector no rompe `render()`).

## 2. Detector con fixture de clicks (intervalo)

Fixture sintético: WAV con clicks a 120 BPM (cada 0.5 s). Reproducir y verificar
que `lastBeatPosition` avanza en saltos ≈ 0.5 s (SC-001).

## 3. Zapateo entre 2 decks

Cargar el mismo track en A y B, adelantar B (seek +N ms), reproducir ambos y
leer el medidor: `offsetMs` ≈ N ms, estado `zapateo`. Activar sync → el offset
cae a ~0 (estado `in-sync`).

## 4. Visual

```bash
DJMIXER_SYNCLAB=1 DJMIXER_SCREENSHOT=/tmp/009.png ./build/djmixer.app/Contents/MacOS/djmixer
```

Verificar que el medidor de zapateo aparece en el SyncLab.
