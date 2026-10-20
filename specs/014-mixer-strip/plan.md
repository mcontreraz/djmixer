# Plan de implementación: Franja MIXER completa (EQ + Filtro + Gain)

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

**Spec**: `specs/014-mixer-strip/spec.md` · **Rama**: `014-mixer-strip`

## Contexto (estado actual)

- **EQ**: existe una implementación previa (013, del otro agente) usada como
  REFERENCIA — no como base. La Fase 0 de este plan la reimplementa desde las
  fórmulas RBJ estándar con la misma calibración documentada (100 Hz / 1 kHz /
  8 kHz, ±12 dB, bypass en 0). Faltan además: `Knob.qml` funcional y la fila
  HI/MID/LOW en `MixerStrip.qml` (T006–T008 de 013, pendientes).
- **Filtro**: sin implementar. `Biquad::lowpass/highpass` ya existen en
  `audioformat.h` (RBJ). El diseño base ya está acordado en
  `referencia-traktor/EQ-FILTER.md` (no publicado) (referencia local, **no publicada**) §4: knob bipolar (centro off,
  izquierda LP, derecha HP, resonancia), modelos Z/Xone/Ladder fuera de
  alcance v1.
- **Gain**: `m_channelGain` fijo 0.8 en `Deck` (atomic, aplicado en
  `render()` junto al crossGain). Solo falta exponerlo.
- `MixerStrip.qml` actual: canal = número + fader + vúmetro (12 segmentos) +
  CUE; crossfader horizontal abajo. Alto ~144 px; el mockup exige más alto
  (2 filas de knobs extra ≈ +90 px).
- `components/Knob.qml` actual: visual estático (48×60), sin drag.

## Diseño DSP

### 1. Filtro de canal — `Deck` (`deck.h/.cpp` (no publicado))

- Estado UI→audio: `std::atomic<float> m_filterAmount{0.0f}` (−1..+1);
  Q_PROPERTY `filterAmount` + slot `setFilterAmount(double)` + notify.
- Solo hilo de audio: 4 `Biquad` (`m_filterLp[2]`, `m_filterHp[2]`),
  cutoff actual `m_filterCutoff`, flag `m_filterEngaged`.
- Mapeo del knob (constantes en `deck.cpp`):

  ```cpp
  // amount ∈ [-1, 0): LP, cutoff log 20 kHz → 40 Hz
  // amount ∈ (0, +1]: HP, cutoff log 20 Hz → 18 kHz
  // |amount| < 0.005 → bypass (y cutoff en extremo transparente)
  constexpr float kFilterLpMinHz = 40.0f, kFilterLpMaxHz = 20000.0f;
  constexpr float kFilterHpMinHz = 20.0f, kFilterHpMaxHz = 18000.0f;
  constexpr float kFilterQ = 1.0f;  // resonancia fija v1
  ```

- Suavizado: one-pole del cutoff por bloque (τ = 4 ms, snap 1 Hz, igual
  criterio que el EQ) + interpolación de coeficientes por muestra con
  `eqRampBlock` generalizado a `coeffRampBlock(to, buf, n, stride)` (el EQ y
  el filtro comparten la rutina; extraerla en `deck.cpp` sin cambiar la
  semántica del EQ).
- Inserción en `render()`: justo después de `applyEq(frameCount)` y antes del
  pico/vúmetro → cadena EQ → filtro → meter → gain → fader/cross.
- Bypass bit-exacto cuando `|amount| < 0.005` y asentado (mismo patrón
  `m_eqEngaged`).

### 2. Gain de canal — `Deck`

- Q_PROPERTY `channelGain` (0..2, default 0.8) + `setChannelGain(double)` →
  `m_channelGain` (ya existe el atomic). Sin suavizado por muestra (ganancia
  pura multiplicativa; un salto de 6 dB no clica con audio típico), pero con
  ramp corto de ~10 ms por bloque para el caso 0↔2 (barato y sin clicks
  garantizados). El vúmetro queda pre-gain (comportamiento de mixer real).

### 3. UI — `Knob.qml` funcional + `MixerStrip.qml`

- **`Knob.qml`** (reemplaza el estático):
  - Props: `value`, `minimum`, `maximum`, `defaultValue`, `label`, `accent`,
    `decimals` (para el ToolTip), `unit` ("" | "dB" | "×").
  - `onValueEdited(real)` para escribir al deck; drag vertical con
    sensibilidad ~1.5%/px del rango; doble clic → `defaultValue` exacto;
    `ToolTip` con valor formateado durante el drag; flechas del teclado ±1
    paso; `Accessible.name`.
  - Pintado: reutiliza el Canvas actual (aro + indicador) redibujado con
    `value` (requestPaint al cambiar, throttled como el JogWheel).
- **`MixerStrip.qml`** — reorganización por canal (columna):
  1. Fila EQ: 3 `Knob` (HI/MID/LOW, ±12 dB, default 0, accent del deck) →
     `deck.eqLow/eqMid/eqHigh` + `setEq*`.
  2. Fila GAIN/FILTRO: `Knob` GAIN (0..2, default 0.8) → `channelGain`;
     `Knob` FILTRO (−1..+1, default 0, bipolar: indicador centrado) →
     `filterAmount`.
  3. Fader + vúmetro (conservados, más altos) + botón CUE.
  - Alto de la franja: de ~144 px a ~240 px (ajuste del RowLayout en
    `Main.qml` si hace falta); los decks absorben el resto.
  - El crossfader y la cabecera "MIXER" no cambian.
- Verificación visual con captura (`DJMIXER_SCREENSHOT` + `open`/launcher).

### 4. Tests

- **`filter_dsp_test.cpp` (no publicado)** (nuevo ctest `filter_dsp`):
  - Respuesta: seno 50 Hz + 10 kHz por el filtro con `amount = ±1` →
    atenuaciones (SC-001).
  - Bypass bit-exacto con `amount = 0` (SC-001).
  - Barrido de tope a tope con seno constante: salto máximo por muestra
    ≤ umbral (SC-002), midiendo la salida completa de `Deck::render`.
  - Gain: `setChannelGain(0/2)` sobre bloque con seno → amplitud 0/2×
    (SC-003).
- Suite completa `ctest` (SC-004) + captura manual (SC-005).

## Fases

### Fase 0 — EQ propio (el DSP del otro agente queda como referencia)

0.1 `Biquad::lowShelf/peakingEq/highShelf` (RBJ cookbook) en `audioformat.h`
    + `waveformanalyzer.cpp`; identidad exacta con 0 dB. Reimplementado desde
    las fórmulas estándar; el código equivalente del otro agente (013) y sus
    docs quedan como referencia de calibración (frecuencias, rangos, tests).
0.2 `Deck`: props `eqLow/eqMid/eqHigh` (±12 dB, atómicos) + `applyEq` en la
    cadena post-resample con suavizado por bloque y bypass bit-exacto.
0.3 `eq_dsp_test.cpp` (no publicado): respuesta de las 3 bandas + identidad + barrido
    sin clicks (reimplementado; las aserciones de la spec 013 como guía).

### Fase 1 — DSP (filtro + gain)

1. `Deck`: `filterAmount`/`channelGain` props + setters (atómicos).
2. `Deck::render`: `applyFilter` (LP+HP suavizado) post-EQ + ramp de gain.
3. `filter_dsp_test.cpp` (no publicado) + registro en `CMakeLists.txt`.
4. `ctest` verde antes de tocar UI.

### Fase 2 — UI (Knob + MixerStrip)

5. `Knob.qml` funcional (drag, doble clic, ToolTip, teclado, pintado).
6. `MixerStrip.qml`: filas EQ + GAIN/FILTRO por canal (bindings).
7. Ajuste de altura del RowLayout en `Main.qml`.
8. Captura de la franja + verificación manual (giro audible, reset, filtro
   barre, gain recorta).

### Fase 3 — Cierre

9. `ctest` completo + `waveform_scratch_test` sin empeorar.
10. Commit por fase con mensajes claros; merge a `main` cuando esté verde.

## Riesgos / notas

- La interpretación del mockup (orden de filas, centro) es un supuesto
  documentado en la spec; se ajusta en la Fase 2 sin tocar DSP.
- `filterAmount` bipolar en el knob exige indicador con centro visible (la
  muesca del knob apunta arriba en 0).
- El filtro + EQ encadenados pueden superponer cortes (es lo esperado de un
  mixer real; sin protección de clip en v1).
