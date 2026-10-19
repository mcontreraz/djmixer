# Research: Needle Search

Sin incógnitas técnicas: todo lo necesario ya existe y está probado.

## Decisión 1: Mecanismo de salto

- **Decision**: llamar al slot existente `Deck::seek(seconds)` desde QML.
- **Rationale**: ya es thread-safe (flag atómico + `pendingSeek`), preserva
  play/pausa y está cubierto por el autotest. Cero cambios en C++ de motor.
- **Alternatives considered**: nuevo slot `seekFraction` (rechazado: QML calcula
  `fracción × duration` en una línea, no justifica API nueva).

## Decisión 2: Coordenada en overview

- **Decision**: `fraction = mouse.x / width`, `seek(fraction × duration)`.
- **Rationale**: el overview siempre muestra el tema completo (coordenada lineal).
- **Alternatives considered**: ninguna.

## Decisión 3: Coordenada en waveform grande con scroll

- **Decision**: reutilizar la fórmula del pintado:
  `t = position + (x − w/2) / (w / visibleSeconds)`, ignorar si fuera de
  `[0, duration]`.
- **Rationale**: misma correspondencia tiempo↔píxel del scroll (contrato F3);
  el click cae exactamente donde el usuario ve la forma.
- **Alternatives considered**: seek por fracción como el overview (rechazado:
  la vista grande no muestra el tema completo).

## Decisión 4: Gesto

- **Decision**: `MouseArea.onClicked` (click izquierdo).
- **Rationale**: el drag-scrub es scratch (F3, requiere motor); el doble-click
  son dos seeks sin acción especial.
- **Alternatives considered**: press-and-hold / drag (fuera de alcance, ver spec).
