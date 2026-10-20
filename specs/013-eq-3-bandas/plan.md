# Plan de implementación: EQ de 3 bandas (HI/MID/LOW)

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

**Spec**: `specs/013-eq-3-bandas/spec.md` · **Rama**: `013-eq-3-bandas`

## Contexto (estado actual)

- `Biquad` RBJ ya existe en `audioformat.h` (no publicado) (impl. en `waveformanalyzer.cpp` (no publicado)): lowpass/highpass, estado por instancia, `process()` por muestra. El EQ solo necesita 3 fábricas nuevas.
- `Deck::render(frameCount, crossGain)` (`deck.cpp:635` (no publicado)) deja el bloque en `m_mixBuffer`; luego mide pico pre-fader (`:749`) y aplica `gain = m_channelGain * crossGain` (`:760`). Punto de inserción del EQ: entre resample/scratch y el pico (línea ~746), así el vúmetro queda post-EQ pre-fader.
- El path scratch (`renderScratchRange`) también vuelca en `m_mixBuffer` → el EQ cubre ambos caminos con la misma inserción.
- `MixerStrip.qml` (144 px): columna por canal = número + [fader vertical 28 px + vúmetro 12 segmentos] fillHeight + botón CUE 25 px. Hay ~40 px verticales libres para la fila de knobs por encima del fader.
- `components/Knob.qml` existe pero es **visual y no funcional** (48×60, Canvas estático, sin drag). Se reemplaza por un knob funcional compacto.
- Tests: patrón `*.cpp` (no publicado) + target en CMakeLists; `waveform_scratch_test` tiene una falla preexistente de comparación de píxeles (no relacionada; verificar que no empeore).

## Diseño DSP

### 1. Fábricas Biquad (RBJ cookbook) — `audioformat.h` (no publicado) + `waveformanalyzer.cpp` (no publicado)

```cpp
static Biquad lowShelf (float f0, float gainDb, float sampleRateHz, float slopeS = 1.0f);
static Biquad peakingEq(float f0, float gainDb, float q, float sampleRateHz);
static Biquad highShelf(float f0, float gainDb, float sampleRateHz, float slopeS = 1.0f);
```

- `gainDb == 0` → identidad (`b0=1`, resto 0): garantiza FR-004 incluso si algo quedara activo.
- Frecuencias fijas del canal (constantes en `deck.cpp`): LOW 100 Hz shelf, MID 1 kHz peaking Q 0.8, HIGH 8 kHz shelf. Con S=1.0: +12 dB LOW mide +11.1 dB a 50 Hz y HIGH +11.8 dB a 16 kHz (el test usa esas frecuencias; ambas dentro de ±1 dB de 12).
- Kill (P3): si `gainDb <= -12` con modo kill activo → tratar como −60 dB (shelf con S grande) o bypass de banda con fade corto; decidir al implementar T007.

### 2. Estado y aplicación en `Deck`

Nuevas propiedades (patrón `volume`):

```cpp
Q_PROPERTY(double eqLow  READ eqLow  WRITE setEqLow  NOTIFY eqChanged)
Q_PROPERTY(double eqMid  READ eqMid  WRITE setEqMid  NOTIFY eqChanged)
Q_PROPERTY(double eqHigh READ eqHigh WRITE setEqHigh NOTIFY eqChanged)
```

- Setters (hilo UI): clamp −12..+12 → `std::atomic<float> m_eqTarget[3]`.
- En `render()` (hilo audio), antes del pico:
  1. Si `m_eqGain == m_eqTarget` para las 3 bandas y no hay bypass pendiente → saltar (bypass exacto; FR-004/SC-002).
  2. Si difieren: avanzar `m_eqGain` hacia el target con one-pole por bloque (τ = 4 ms → asentado ≈ 30 ms, snap 0.01 dB) y diseñar los coeficientes nuevos **1 vez por bloque** por banda (trivial).
  3. Procesar `m_mixBuffer` en serie LOW→MID→HIGH por canal; en el bloque que se mueve, interpolar los coeficientes **por muestra** entre los vigentes y los nuevos (`eqRampBlock`) → sin zipper incluso con bloques de 10 ms (FR-005/SC-003). El estado x1..y2 persiste siempre.
- Los filtros viven solo en el hilo de audio (como `m_scratchVel`); los atomics son el único puente.

### 3. UI — `components/Knob.qml` (funcional) + `MixerStrip.qml`

- Reescribir `Knob.qml` como control funcional:
  - Props: `value` (dB), `minimum`/`maximum` (default ±12), `defaultValue` (0), `label`, `accent` (color por deck).
  - Drag vertical (MouseArea, `accent` al activo), sensibilidad ~0.15 dB/px; doble clic → `defaultValue` exacto; ToolTip con `+x.x dB` mientras se gira.
  - Dibujo: Canvas o ShaderEffect propio del archivo, dependiente de `value` (hoy el Canvas no se repinta).
  - Teclado: flechas ±; `Accessible.name`.
- `MixerStrip.qml`: fila de 3 knobs (HI, MID, LOW) arriba del fader de cada canal, compactos (~20 px + label 8 px). Ancho de canal ~62 px → 3 × 18 px + 2 × 3 px spacing = 60 px. Orden horizontal HI→MID→LOW (equivalente al orden vertical de un mixer clásico).
- Binding: `value: channel.deck.eqHigh` / `onValueEdited: channel.deck.setEqHigh(v)` (o `onMoved` como el fader).

### 4. Tests — `eq_dsp_test.cpp` (no publicado) (nuevo target CTest)

- **T-UNIT**: para cada banda, seno a f0/decenas/decenas → ganancia medida vs teórica (SC-001); identidad con 0 dB (SC-002 a nivel Biquad).
- **T-SUAVIZADO**: simular bloques con cambio de target → verificar que la ganancia converge en ~30 ms y que el máximo salto por muestra ≤ 1e-3 (SC-003, sin clicks).
- No hace falta audio real decodificado: los tests sintetizan senos y procesan buffers directamente (como hace `waveform_scratch_test` con su WAV generado). Para el bypass exacto a nivel Deck, extraer la lógica a un helper estático testeable o usar un WAV de 1 s generado en el test.
- Registrar target en `CMakeLists.txt` siguiendo el patrón existente y correr `ctest` antes de cerrar.

## Referencia: cómo lo hace Traktor (REA — `referencia-traktor/EQ-FILTER.md` (no publicado), referencia local **no publicada**)

- EQ de canal pluggable por modelos (Classic / Xone / P600 / P800 / P900 ISO);
  4 bandas máximo + kill por banda (`onEqualizerBandKill`). Curvas extraídas del
  binario: ganancia asimétrica (p.ej. +6/−26.5 dB en P800) y **frecuencia/Q que
  se mueven con la perilla** (shelves de codo variable, peaking 0.65→0.20).
- Filtro de canal con 3 modelos (Z-plane NI, Xone, Ladder Moog), knob con
  centro = off, izquierda = LP, derecha = HP (`filter_on`/`filter_value`).
- **Decisiones para v1**: mantenemos ±12 dB simétrico y frecuencias fijas
  100 Hz/1 kHz/8 kHz (más simple y testeable); kill por banda queda P3 (ya
  previsto); filtro NO entra en 013 (candidato a spec 014 con un solo modelo).

## Archivos tocados

| Archivo | Cambio |
|---|---|
| `audioformat.h` (no publicado) | +3 fábricas Biquad |
| `waveformanalyzer.cpp` (no publicado) | implementación RBJ de las 3 fábricas |
| `deck.h` (no publicado) | props `eqLow/eqMid/eqHigh`, atomics, 6 Biquads, buffer helpers |
| `deck.cpp` (no publicado) | setters + aplicación/suavizado en `render()` + constantes de frecuencia |
| `components/Knob.qml` (no publicado) | reescritura funcional (drag, reset, tooltip) |
| `MixerStrip.qml` (no publicado) | 3 knobs por canal |
| `eq_dsp_test.cpp` (no publicado) + `CMakeLists.txt` | test de respuesta/suavizado |

## Riesgos y decisiones abiertas

- **Clipping por boost**: +12 dB simultáneo en 3 bandas puede saturar la suma con masterVol; no se añade limitador en esta entrega (documentado en spec). Si molesta, follow-up: soft-limiter en `Mixer::process`.
- **Orden EQ vs vúmetro**: se elige post-EQ pre-fader (paridad mixer DJ). Si se prefiere el medidor "crudo", mover la medición antes del EQ (1 línea).
- **Kill (P3)**: decidir más adelante; las constantes dejan la puerta abierta sin re-diseño.
- **Knob actual no funcional**: la reescritura elimina el Canvas estático; verificar que ningún otro archivo lo use (grep `Knob {` antes de tocar).
- **No regresión**: correr `waveform_scratch_test` (única falla conocida: píxeles, preexistente) y `sync_audio_test`.
