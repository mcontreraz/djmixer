# Contracts: Cue Points (QML ⟷ C++)

## Deck (extensión)

| Miembro | Forma | Descripción |
|---|---|---|
| `cuePosition` | `Q_PROPERTY double READY NOTIFY cueChanged` | segundos del cue |
| `cueValid` | `Q_PROPERTY bool READY NOTIFY cueChanged` | hay cue guardado |
| `cuePressed()` | slot | (a) sonando → return+pause; (b) pausado → set+play |
| `cueReleased()` | slot | si venía de preview → seek(cue)+pause; si no, nada |
| `cueChanged()` | señal | set / clear / carga con sidecar |
| `hotCueList` | `Q_PROPERTY QStringList READY NOTIFY hotCuesChanged` | 8 entradas (`""` o segundos) para los pads |
| `setHotCue(i, pos)` | slot/`Q_INVOKABLE` | guarda + persiste |
| `clearHotCue(i)` | slot/`Q_INVOKABLE` | borra + persiste |
| `jumpHotCue(i)` | slot/`Q_INVOKABLE` | seek + play |
| `hotCuesChanged()` | señal | set / clear / carga |

## WaveformView

| Miembro | Forma | Descripción |
|---|---|---|
| `cueTime` | `property real (-1 = sin cue)` | marca fija: overview en fracción, scroll en tiempo absoluto |

## Reglas

1. `cuePressed` con deck vacío/corrupto no hace nada (FR-007).
2. Nueva carga limpia el cue en memoria y reintenta leer sidecar.
3. El `.cuepoint` solo se escribe en `set`, nunca en preview ni por frame.
