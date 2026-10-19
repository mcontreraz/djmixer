# Research: Real-time Beat Detector + Zapateo

## Decisión 1: Envolvente de onsets (qué señal marca un beat)

- **Decision**: energía de graves por hop (lowpass ~250 Hz, hop 512 muestras) y
  **flujo positivo** (`max(0, e[t] − e[t−1])`), igual que `detectTempo`.
- **Rationale**: ya probado en el detector offline; el kick vive en graves; el
  flujo positivo aísla los ataques.
- **Alternatives**: flux espectral (FFT) — rechazado (más CPU, viola IV);
  energía full-band — rechazado (voces/agudos meten ruido).

## Decisión 2: Detección de picos con umbral adaptativo

- **Decision**: un onset es "beat" si `flux > k * media_reciente` (k≈1.5) y
  pasó el **refractory** (≥ 200 ms desde el último beat). La media se mantiene
  con un buffer circular fijo.
- **Rationale**: adaptativo evita falsos positivos con tracks suaves; refractory
  evita dobles detecciones del mismo golpe.
- **Alternatives**: umbral fijo (rechazado: no escala entre tracks); onset
  onset-strength de librosa (rechazado: dependencia).

## Decisión 3: Dónde corre

- **Decision**: en `Deck::render()`, alimentado con el buffer mezclado del deck
  (o la suma mono). Expone `lastBeatPosition` por `std::atomic<double>`.
- **Rationale**: es el único lugar con el audio en tiempo real; O(1) por frame.
- **Alternatives**: hilo aparte leyendo el buffer (rechazado: copia + sync);
  solo en el SyncLab (rechazado: el SyncLab simula, no tiene audio).

## Decisión 4: Medición del zapateo (desfase)

- **Decision**: `offsetMs = wrap(beatB − beatA, período)` con período del deck
  de referencia (A). `state`: `in-sync` si `|offsetMs| < umbral`, `zapateo` si
  no, `no-beat` si falta un lado.
- **Rationale**: envuelto a medio período para no confundir "un beat adelante"
  con "un beat atrás"; es exactamente el golpe doble audible.
- **Alternatives**: diferencia sin envolver (rechazado: ambiguo en octavas).

## Decisión 5: Sin dependencias nuevas

- **Decision**: reutilizar `Biquad::lowpass` (ya en `waveformanalyzer.h`) o un
  filtro de primer orden aún más simple.
- **Rationale**: Constitución IV; aubio/SoundTouch no entran.
