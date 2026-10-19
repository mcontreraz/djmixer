# Contracts: Scratch (QML ⟷ C++)

## Deck (extensión)

| Miembro | Forma | Descripción |
|---|---|---|
| `scratchGrab()` | slot | congela avance normal; recuerda si sonaba |
| `scratchTo(seconds)` | slot | `handPos` = clamp(segundos) (ignora sin track) |
| `scratchRelease(v)` | slot | `v` en frames/frame con signo; spin si \|v\|≥0.02 si no resume/detiene |

## WaveformView (scroll)

- Drag con botón izquierdo: `press → scratchGrab + scratchTo(t)`,
  `move → scratchTo(t)`, `release → scratchRelease(v medida)`.
- Click simple conserva needle (drag de longitud cero).

## JogWheel

- Drag angular: `Δt = Δángulo / 2π × 2.0`; misma terna de slots.
- La línea roja y los tiempos siguen solos (ya van ligados a `position`).

## Reglas

1. Sin track abierto los tres slots no hacen nada.
2. `cuePressed/jumpHotCue` cancelan un agarre en curso.
3. `v` se clampéa a ±4.0 frames/frame (±4×) en el motor.
