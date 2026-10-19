# Feature Specification: Scratch (plato + waveform)

**Feature Branch**: `006-scratch`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "scratch en plato y waveform: al presionar el mouse en alguna línea del waveform se adelanta/retrasa la forma como en Serato; lo mismo en el plato con la línea roja; movimiento rápido = back/forward spin como Serato"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Drag en waveform mueve el audio (Priority: P1)

El DJ presiona sobre la waveform grande y arrastra: el audio sigue la mano
hacia adelante y hacia atrás (reversa audible incluida). Al soltar quieto,
sigue sonando normal desde ese punto.

**Why this priority**: Es el gesto pedido; sin motor bidireccional no hay scratch.

**Independent Test**: Sonando, arrastrar a la izquierda 5 s de audio → se
escucha reversa y la posición retrocede; soltar → sigue normal.

**Acceptance Scenarios**:

1. **Given** reproducción en curso, **When** se arrastra el waveform atrás, **Then** la posición retrocede siguiendo la mano.
2. **Given** agarre sin mover, **When** se mantiene 1 s, **Then** no avanza la posición (mano quieta = vinilo quieto).
3. **Given** release con velocidad ~0, **When** se suelta, **Then** retoma normal sin salto.

---

### User Story 2 - Plato angular + spin (Priority: P2)

Arrastrar circularmente el plato mueve el audio (1 vuelta = 2 s); soltar con
flick rápido produce backspin/forward-spin con decaimiento (~1 s) hasta
retomar o detenerse. La línea roja sigue la posición en todo momento.

**Why this priority**: Paridad Serato pedida explícita (línea roja + spin).

**Independent Test**: Flick rápido hacia atrás y soltar → se escucha el
rebobinado decayendo y la línea roja gira atrás.

**Acceptance Scenarios**:

1. **Given** plato agarrado, **When** se gira 180°, **Then** la posición se mueve ±1 s según sentido.
2. **Given** release con velocidad alta, **When** se suelta, **Then** el audio decae ~1 s (spin) en vez de cortar en seco.
3. **Given** scratch en curso, **When** se mira jog/waveforms/playhead, **Then** todo sigue la posición (sin UI congelada).

---

### Edge Cases

- ¿Scratch sin tema? → gestos ignorados, sin crash.
- ¿Scratch más allá del inicio/fin? → clamp (0 / duración), sin wrap.
- ¿CUE/pads durante agarre? → el agarre se cancela limpio y manda el cue/jump.
- ¿MP3 con seek lento hacia atrás? → historial de ~5 s en RAM evita re-seeks en el rango; fuera de rango se rebusca (puede micro-cortar en MP3, aceptado).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El motor MUST reproducir en reversa (tasa con signo) durante el agarre.
- **FR-002**: La posición durante el agarre MUST ser autoritativa de la mano (no del reloj).
- **FR-003**: Al soltar MUST aplicar inercia (velocidad medida) con decaimiento y luego retomar/detener según estado previo.
- **FR-004**: El buffer MUST retener ~5 s de historia para reversa sin re-seek.
- **FR-005**: Waveform grande MUST mapear drag a tiempo (fórmula scroll existente); plato MUST mapear ángulo a tiempo (1 vuelta = 2 s).
- **FR-006**: Click simple (sin drag) MUST seguir siendo needle (sin regresión).
- **FR-007**: Toda la UI de posición (jog, tick, playheads, tiempos) MUST seguir al scratch en vivo.

### Key Entities

- **ScratchState** (por Deck): `grabbed`, `handPos` (frames fuente), `spinVel` (frames/frame con signo), `grabWasPlaying`.
- **Deck (extensión)**: slots `scratchGrab()`, `scratchTo(seconds)`, `scratchRelease(velFramesPerSec)`; historial en `m_src`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Arrastrar atrás 5 s de audio retrocede la posición en 5 s (±0.5 s).
- **SC-002**: Flick con |v| alta produce spin audible ≥600 ms antes de retomar/detener.
- **SC-003**: Sin regresión: needle por click, play/pause/cue intactos (autotest verde).
- **SC-004**: La línea roja y los tiempos siguen la mano sin congelarse (captura con scratch activo).

## Assumptions

- 1 vuelta de plato = 2.0 s (constante documentada, ajustable).
- Spin: decaimiento exponencial ~1 s; umbral de quietud 0.02 frames/frame.
- Reversa fuera del historial (±5 s) = re-seek (micro-corte aceptado en MP3).
- Sin DVS/hardware: solo mouse.
