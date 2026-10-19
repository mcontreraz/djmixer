# Research: Scratch

## Decisión 1: Posición autoritativa de la mano

- **Decision**: mientras `grabbed`, cada callback parte de `handPos` (atómico,
  en frames fuente) en vez de avanzar `m_playedFrames`; el render interpola
  entre la última posición servida y la actual (pitch correcto a cualquier
  velocidad de mano, incluida reversa y mano quieta = repetición ≈ silencio).
- **Rationale**: una sola fuente de verdad evita drift entre UI y audio; la
  interpolación por tramo suaviza los 60 Hz del mouse a nivel de muestra.
- **Alternatives considered**: seeks rápidos por movimiento (rechazado: clicks
  por discontinuidad + seeks caros en MP3).

## Decisión 2: Reversa sin re-seek

- **Decision**: `discardConsumed` retiene ~5.5 s (262144 frames) en vez de 1024;
  si el rango pedido sale del buffer, seek al decoder y refill (igual que hoy).
- **Rationale**: el scratch típico vive en ±5 s; 2 MB/deck es barato; fuera de
  rango se acepta micro-corte en MP3 (WAV: instantáneo).
- **Alternatives considered**: buffer infinito (memoria); pre-decode total al
  cargar (latencia de carga y RAM en temas largos).

## Decisión 3: Spin al soltar

- **Decision**: `scratchRelease(v)` recibe velocidad en frames/frame con signo;
  si |v| ≥ 0.02 entra modo spin: cada callback avanza `v` y decae
  `v *= pow(0.9999, frames)` (~1 s audible); al bajar del umbral retoma
  (si venía sonando) o frena.
- **Rationale**: un flick = spin real en ambas direcciones con física creíble
  y fin determinado.
- **Alternatives considered**: velocidad en QML con timer propio (rechazado:
  el decaimiento debe vivir en el callback para ser sample-accurate).

## Decisión 4: Click vs drag (sin regresión needle)

- **Decision**: press = grab+scratchTo; move = scratchTo; release quieto
  (|v| < umbral y |Δt| pequeño) = resume normal (equivale al needle al mismo
  punto); el `onClicked` existente se mantiene como fallback.
- **Rationale**: un click es un drag de longitud cero: mismo destino, sin
  código duplicado ni doble salto observable.
- **Alternatives considered**: suprimir needle en vistas scroll (rechazado:
  rompería US-002).

## Decisión 5: Plato angular

- **Decision**: `Δt = Δángulo / 2π × 2.0 s`; velocidad angular → misma
  `scratchRelease()`. Constante `kSecondsPerRev = 2.0` documentada.
- **Rationale**: 1 vuelta = 2 s es el estándar de facto (sensación vinilo 33⅓
  llevaría a confusión con pitch).
