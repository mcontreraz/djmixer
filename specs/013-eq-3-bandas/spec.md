# Feature Specification: EQ de 3 bandas (HI/MID/LOW)

**Feature Branch**: `013-eq-3-bandas`

**Created**: 2026-10-17

**Status**: Draft

**Input**: User description: "planifiquemos un equalizador de tres bandas high mid bass"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ecualizar cada canal (Priority: P1)

Cada deck tiene 3 perillas (HI, MID, LOW) en la franja MIXER. Girar una
perilla cambia esa banda en tiempo real (±12 dB, centro = plano). El
resultado se oye en el main y en el cue (el EQ es del canal, no del master).

**Why this priority**: es el core del feature: sin audio ecualizado no hay
nada que mostrar.

**Independent Test**: con un track sonando en el deck 1, girar LOW a +12 dB →
el grave sube audiblemente; girar a −12 dB → baja. Medible con sweep de senos
(test C++).

**Acceptance Scenarios**:

1. **Given** un deck reproduciendo, **When** LOW sube a +12 dB, **Then** se oye refuerzo de graves (≈+12 dB a 50 Hz, plano a 10 kHz).
2. **Given** cualquier banda en 0 dB, **When** los 3 knobs están en 0, **Then** la salida es idéntica a la de hoy (sin filtros aplicados, sin pérdida).
3. **Given** MID a −12 dB, **When** suena música, **Then** se atenúa la zona de 1 kHz (voz/snare) sin tocar graves ni agudos.

---

### User Story 2 - Reset rápido a plano (Priority: P2)

Doble clic sobre un knob lo devuelve a 0 dB (centro). Tooltip/label muestra el
valor en dB mientras se gira.

**Why this priority**: en cabina hay que volver a plano con un gesto, como el
botón 0 del pitch.

**Independent Test**: girar HI a +8 dB, doble clic → vuelve exactamente a 0.0.

**Acceptance Scenarios**:

1. **Given** un knob en ±x dB, **When** doble clic, **Then** queda en 0.0 dB y el audio vuelve a plano.
2. **Given** el mouse sobre un knob, **When** se arrastra vertical, **Then** el valor cambia proporcionalmente y se muestra el dB actual (ToolTip).

---

### User Story 3 - Sin clicks al mover perillas (Priority: P3)

Mover una perilla durante la reproducción no produce clicks ni zipper noise;
el cambio se suaviza en el hilo de audio.

**Why this priority**: es la diferencia entre "demo" y "usable en vivo", pero
sin esto el feature sigue siendo funcional en reposo.

**Independent Test**: mover LOW de tope a tope repetidamente con seno
constante sonando → no hay discontinuidades medibles en el test C++ (salto de
muestra < umbral) y no se oyen clicks.

**Acceptance Scenarios**:

1. **Given** audio sonando, **When** se gira un knob rápido, **Then** la transición se completa suave (~30 ms) sin salto audible.

---

### User Story 4 (P3, opcional) - Kill / ISO por banda

Con la perilla al tope izquierdo la banda se corta (kill total, estilo mixer
Serato/DJM ISO), no solo −12 dB.

**Why this priority**: lo usan los scratch DJs para cortes de batalla; puede
quedar fuera de la primera entrega sin bloquear nada.

**Acceptance Scenarios**:

1. **Given** LOW en tope izquierdo (modo kill activo), **When** suena el track, **Then** los graves desaparecen (≤ −40 dB a 50 Hz).

---

### Edge Cases

- EQ con pista pausada: los knobs siguen funcionando y el valor se aplica al volver a reproducir.
- Carga de pista nueva: el EQ del canal NO se resetea (es estado del canal, como el fader).
- +12 dB en las 3 bandas a la vez: puede clipar la suma con master — se documenta; el master no añade limitador en esta entrega.
- Karaoke/scratch (path scratch del deck): el EQ aplica igual (post-resample).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `Deck` expone `eqHigh`, `eqMid`, `eqLow` (dB, double, −12..+12, default 0.0) con setters seguros para el hilo UI (atómicos).
- **FR-002**: LOW = low-shelf a 100 Hz; MID = peaking a 1 kHz (Q≈0.8); HIGH = high-shelf a 8 kHz (fórmulas RBJ, reutilizando `Biquad`).
- **FR-003**: El EQ se aplica por canal (estéreo) en `Deck::render`, después del resample/scratch y antes del fader de canal y del crossfader (cadena clásica EQ→fader→cross).
- **FR-004**: Con las 3 bandas en 0.0 dB el camino no procesa (bypass exacto, salida bit a bit igual a la actual).
- **FR-005**: Los cambios de perilla se suavizan en el hilo de audio (objetivo ~30 ms, sin recalcular por muestra).
- **FR-006**: La franja MIXER muestra 3 perillas funcionales por canal con etiqueta HI/MID/LOW; drag vertical y doble clic = 0 dB.
- **FR-007**: El vúmetro de canal pasa a medir post-EQ pre-fader (comportamiento de mixer real; hoy ya es pre-fader).
- **FR-008**: (Opcional P3) Kill total al tope izquierdo de cada banda.
- **FR-009**: (Fuera de alcance) mapeo MIDI `deck_eq_hi/mid/lo` — reservados por spec 011, se cablean en otra entrega.

### Key Entities

- **Banda de EQ**: `{frecuencia, tipo de filtro (shelf/peak), ganancia dB}` ×3 por deck.
- **Estado interno por deck**: 6 `Biquad` (3 bandas × 2 canales) + ganancias objetivo/actuales por banda.
- **Knob QML**: control de perilla reutilizable (valor, rango, default, drag, doble clic).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Test C++ con senos: LOW +12 dB → 50 Hz sube 12±1 dB y 10 kHz varía <1 dB; MID +12 dB → 1 kHz sube 12±1 dB; HIGH +12 dB → 16 kHz sube 12±1 dB (frecuencia de sample 48 kHz).
- **SC-002**: Bypass plano bit-exacto: render con EQ en 0 == render sin EQ (test C++).
- **SC-003**: Sin clicks: con seno constante, un barrido de perilla de tope a tope produce saltos de muestra bajo el umbral del test (y audibles: ninguno).
- **SC-004**: UI verificable a ojo: 3 perillas por canal en la franja MIXER, valores −12..+12, doble clic vuelve a 0.0 exacto.
- **SC-005**: `waveform_scratch_test` y `sync_audio_test` siguen igual (la única falla conocida es el check de píxeles preexistente, ajeno al EQ).

## Assumptions

- ±12 dB es el rango estándar (Serato/Pioneer DJM); el kill ISO (FR-008) es opcional por banda.
- Frecuencias fijas 100 Hz / 1 kHz / 8 kHz (constantes ajustables en una sola línea); no hay selector de frecuencias en esta entrega.
- El EQ es por canal, no hay EQ en el master (como Serato software).
- No se persiste entre sesiones (mismo criterio que volumen/crossfader).
