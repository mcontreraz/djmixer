# Feature Specification: Needle Search

**Feature Branch**: `002-needle-search`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "needle search en deck: al hacer click en algún punto del waveform del deck saltamos a ese punto de la canción"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Click en overview salta (Priority: P1)

El DJ hace click en un punto del overview del deck y la reproducción salta
ahí de inmediato, con o sin pausa (si sonaba, sigue sonando desde el punto
nuevo).

**Why this priority**: Es el needle drop clásico; usa el `seek()` ya existente
del motor, solo falta el gesto en la UI.

**Independent Test**: Cargar el WAV, click a mitad del overview → el tiempo del
jog y el playhead saltan a ~50% y el audio continúa desde ahí.

**Acceptance Scenarios**:

1. **Given** un tema cargado en pausa, **When** click al 75% del overview, **Then** la posición queda en ~75% sin empezar a sonar.
2. **Given** reproducción en curso, **When** click al 25% del overview, **Then** el audio sigue desde ~25% sin cortarse.

---

### User Story 2 - Click en waveform grande salta (Priority: P2)

Lo mismo sobre las waveforms grandes con scroll: click en un punto visible
salta a ese tiempo (misma correspondencia tiempo↔píxel del scroll).

**Why this priority**: Completa el gesto en la vista principal de mezcla.
Depende de US1 (mismo `seek`, distinta coordenada).

**Independent Test**: Con el WAV sonando, click en el borde derecho de la
waveform grande → salta cerca del tiempo visible ahí.

**Acceptance Scenarios**:

1. **Given** waveform grande visible con scroll, **When** click en un punto con tiempo válido, **Then** la posición salta a ese tiempo.
2. **Given** click fuera del rango con audio (zona vacía antes del 0 o tras el fin), **When** click, **Then** no pasa nada.

---

### Edge Cases

- ¿Click sin tema cargado? → se ignora (duración 0).
- ¿Click durante análisis de waveform? → el seek funciona igual (el audio no depende del análisis).
- ¿Arrastrar (drag) en vez de click? → fuera de alcance: es scratch (F3). Solo click.
- ¿Doble-click? → un doble-click son dos seeks; sin acción especial.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST convertir click en overview a fracción y llamar `seek(fracción × duración)` del deck.
- **FR-002**: El sistema MUST convertir click en waveform grande a tiempo con la misma fórmula del scroll (`position + (x − centro) / pxPorSegundo`).
- **FR-003**: Clicks fuera del rango de audio MUST ignorarse.
- **FR-004**: El seek MUST preservar el estado play/pausa (no auto-play, no stop).
- **FR-005**: El gesto MUST funcionar con mouse (click izquierdo); touchpad hereda el click.

### Key Entities

- Ninguna nueva (usa `Deck.seek`, `position`, `duration` y `WaveformCache` existentes).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Click al 50% del overview deja la posición entre 48% y 52% de la duración.
- **SC-002**: El audio no se corta al hacer seek sonando (la posición avanza continua tras el salto).
- **SC-003**: Click sin tema cargado no hace nada (sin crash, sin log de error).

## Assumptions

- `Deck::seek()` ya es thread-safe (flags atómicos) y no necesita cambios.
- Sin indicador visual extra del punto clickeado (el playhead existente basta).
- El drag-scrub queda para F3 (motor de scratch).
