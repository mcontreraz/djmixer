# Feature Specification: Franja MIXER completa (EQ + Filtro + Gain, layout mockup)

**Feature Branch**: `014-mixer-strip`

**Created**: 2026-10-18

**Status**: Draft

**Input**: mockup visual del mixer (imagen del usuario) + trabajo previo: EQ de 3
bandas (spec 013, DSP commiteado, UI pendiente) y filtro de canal (docs
`referencia-traktor/EQ-FILTER.md`, fuera de alcance de 013).

## Resumen

La franja MIXER pasa de "fader + vúmetro + CUE" a la disposición del mockup:
por canal, fila de EQ HI/MID/LOW (wiring a los `eqLow/eqMid/eqHigh` ya
implementados), perilla de FILTRO de canal (LP/HP barrido con resonancia,
centro = off) y perilla de GAIN (trim de canal), con fader + vúmetro + CUE
debajo. Crossfader y cabecera se conservan.

## Layout objetivo (interpretación del mockup)

```
      [1]      [2]        ← número de canal (accent)
   HI  MID  LOW          ← fila de 3 knobs EQ por canal (±12 dB, dbl-click = 0)
   GAIN  FILTRO          ← fila de 2 knobs por canal
   [fader]  [vúmetro]    ← existente, más alto que hoy
   [CUE]                 ← existente
   ---- crossfader ----  ← existente (horizontal, abajo)
```

Nota: el mockup es una imagen sin etiquetas legibles en este entorno; el orden
de filas (EQ arriba, GAIN+FILTRO al medio, fader abajo) es la interpretación
adoptada. Las posiciones exactas se ajustan en la implementación (T008).

## User Scenarios & Testing *(mandatory)*

### US-1 — Ecualizar el canal con la franja (P1)

Girar HI/MID/LOW cambia la banda en tiempo real; doble clic vuelve a 0 dB.
(Continúa spec 013: el DSP ya está; falta la UI.)

**Independent Test**: con un track sonando, girar LOW → se oye el cambio y el
vúmetro post-EQ reacciona; doble clic → plano.

### US-2 — Filtrar el canal (P1)

Perilla bipolar de FILTRO: centro = off (sin efecto), izquierda = barrido
lowpass (se cierra el brillo hasta graves), derecha = barrido highpass (se
cierran graves hasta agudos). Girar durante la reproducción NO produce clicks.

**Independent Test**: senos de 300 Hz + 10 kHz sonando: filtro a media
perilla izquierda (cutoff ≈ 894 Hz) → 10 kHz baja ≥ 24 dB y 300 Hz queda; a
media perilla derecha → al revés. Centro → bypass (idéntico a hoy). A fondo
el cutoff llega a 40 Hz/18 kHz (corte profundo).

### US-3 — Gain de canal (P2)

Perilla GAIN (0–2×, default 1.0 = sin cambio) recorta el nivel del canal
pre-fader. Doble clic vuelve a 1.0.

**Independent Test**: GAIN a 0 → silencio del canal (con fader arriba); GAIN a
2× → vúmetro sube ~6 dB.

### US-4 — Sin clicks ni zipper al girar perillas (P1)

EQ, filtro y gain suavizan sus cambios en el hilo de audio (mismo patrón que
013: one-pole por bloque + interpolación de coeficientes por muestra).

**Independent Test**: test C++ mide saltos de muestra bajo umbral al barrer
filtro de tope a tope (como `eq_dsp_test`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `Deck` expone `filterAmount` (−1..+1, default 0) y `trimGain`
  (0..2×, default 1.0 = sin cambio audible; el fader existente conserva
  `channelGain` 0..1) con setters thread-safe (atómicos) y notify.
- **FR-002**: Filtro = cascada LP+HP (Biquad existentes) por canal, aplicado
  post-EQ, pre-vúmetro/pre-fader:
  - `filterAmount < 0`: lowpass, cutoff barrido logarítmico 20 kHz → 40 Hz.
  - `filterAmount > 0`: highpass, cutoff barrido 20 Hz → 18 kHz.
  - `|filterAmount| < 0.5%`: bypass (sin proceso, como el EQ plano).
  - Resonancia fija v1 (Q ≈ 1.0), sin selector de modelo.
- **FR-003**: La cadena por canal queda: resample/scratch → EQ (3 bandas) →
  filtro → vúmetro → channelGain → fader/crossfader.
- **FR-004**: Los cambios de filtro/gain se suavizan ~30 ms sin recalcular por
  muestra (patrón `eqRampBlock`, generalizado).
- **FR-005**: `components/Knob.qml` pasa a ser funcional: drag vertical,
  doble clic = default, ToolTip con el valor, pintado dependiente de `value`,
  teclado (flechas) y `Accessible.name`. Reutilizable para EQ (±12 dB), filtro
  (−1..+1) y gain (0..2).
- **FR-006**: `MixerStrip.qml` reorganizado según el layout objetivo: fila
  EQ (HI/MID/LOW) + fila GAIN/FILTRO por canal, fader/vúmetro/CUE conservados,
  crossfader intacto. Bindings: `eqLow/eqMid/eqHigh`, `filterAmount`,
  `channelGain`.
- **FR-007**: El estado de EQ/filtro/gain es del canal (no se resetea al
  cargar pista) y no se persiste (igual criterio que volumen/crossfader).
- **FR-008**: (Fuera de alcance) mapeo MIDI de EQ/filtro/gain — reservado para
  la entrega de controladoras (spec 011).

### Key Entities

- **Filtro de canal**: `filterAmount` (−1..+1) → cutoff LP/HP; 4 `Biquad`
  (LP+HP × 2 canales) + estados de suavizado, solo hilo de audio.
- **Gain de canal**: `channelGain` (0..2) reemplaza el `m_channelGain` fijo.
- **Knob funcional**: componente QML reutilizable (rango, default, label,
  accent, unidades).

## Success Criteria *(mandatory)*

- **SC-001**: `filter_dsp_test` (ctest): LP media perilla atenúa 10 kHz
  ≥ 24 dB dejando 300 Hz ≥ −3 dB; HP simétrico; centro = bypass. EQ: kill al
  tope izquierdo ≤ −40 dB en la banda.
- **SC-002**: Barrido de filtro de tope a tope con seno constante: salto de
  muestra ≤ umbral (sin clicks).
- **SC-003**: GAIN a 0 silencia el canal; a 2× duplica la amplitud del bloque
  (±0.5 dB medido).
- **SC-004**: Suite completa verde: `eq_dsp`, `scratch_audio`, `sync_audio`,
  `waveform_scratch`, `grid_cache`, `midi_binding`.
- **SC-005**: Captura/manual: franja MIXER con las 5 perillas por canal
  funcionando (EQ audible, filtro barre, gain recorta, doble clic resetea).

## Assumptions

- Orden de filas según la interpretación del mockup (ajustable en T008).
- Frecuencias del filtro fijas al barrido descrito (constantes en una línea).
- Sin EQ ni filtro en el master (el EQ/filtro es de canal).
- Sin selector de modelo de filtro (Z/Xone/Ladder quedan como referencia).
- `trimGain` default 1.0 conserva el nivel actual (sin cambio audible con
  la perilla en el centro). Kill = shelf −60 dB (≈ −42 dB a 50 Hz, ISO).
