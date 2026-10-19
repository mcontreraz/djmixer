# Data Model: Scratch

## ScratchState (por Deck, UI→audio por atómicos)

| Campo | Tipo | Reglas |
|---|---|---|
| `grabbed` | `atomic<bool>` | true entre press y release del gesto |
| `handPos` | `atomic<double>` | frames fuente autoritativos (clamp `[0, total]`) |
| `spinVel` | `atomic<float>` | frames/frame con signo; 0 = sin spin |
| `grabWasPlaying` | bool (solo audio) | se captura al entrar en grab |

## Buffer (requisito)

`m_src` retiene últimos 262144 frames (~5.5 s @48 kHz) en vez de 1024.
`m_playedFrames` se mantiene sincronizado con lo servido (grab y spin) para
retomar sin salto.

## Deck (extensión)

| Miembro | Rol |
|---|---|
| `scratchGrab()` | slot: congela avance, captura estado |
| `scratchTo(seconds)` | slot: fija `handPos` (clamp) |
| `scratchRelease(v)` | slot: spin si \|v\|≥0.02, si no resume/detiene |
| `kSecondsPerRev = 2.0` | constante QML del plato |
