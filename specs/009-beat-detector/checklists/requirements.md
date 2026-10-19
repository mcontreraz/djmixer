# Specification Quality Checklist: Real-time Beat Detector + Zapateo

## Content Quality

- [x] No implementation details in spec (sin lowpass/hop/threshold en el spec)
- [x] Focused on user value (detectar el zapateo real entre 2 canciones)
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers
- [x] Requirements testable and unambiguous (intervalo ±5%, offset ±30 ms)
- [x] Success criteria measurable (ms, %, estado)
- [x] Acceptance scenarios defined
- [x] Edge cases identified (sin transientes, pausa, octava, clicks)
- [x] Scope bounded (2 decks; BPM real-time fuera de alcance)

## Feature Readiness

- [x] FRs tienen criterios claros
- [x] Escenarios cubren detector + zapateo + UI
- [x] Sin HOW en el spec (el HOW vive en research/plan)

## Notas

- El spec separa detector (P1), zapateo (P2) y visual (P3), cada uno testeable solo.
- Constitución I es explícita: el detector no puede bloquear `render()`.
- El "zapateo" se define técnicamente como offset envuelto a medio período.
