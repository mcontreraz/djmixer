# Contracts: Beat Sync (QML ⟷ C++)

## SyncEngine (QObject)

| Miembro | Forma | Descripción |
|---|---|---|
| `mode` | `Q_PROPERTY int READ mode WRITE setMode NOTIFY modeChanged` | `0=Off 1=Simple 2=Smart` |
| `primaryIndex` | `Q_PROPERTY int READ primaryIndex NOTIFY primaryChanged` | `-1` (ninguno) / `0` / `1` |
| `stateA` / `stateB` | `Q_PROPERTY int READ ... NOTIFY stateChanged` | `0=Off 1=Armed 2=Tempo 3=Beat` |
| `setSync(int deck, bool on)` | `Q_INVOKABLE` | activa/desactiva sync en el deck (UI) |

## Deck (ya existente, consumido por SyncEngine)

| Miembro | Uso |
|---|---|
| `setPitch(double)` | ajusta `rate` atómico (tempo match + PLL) |
| `seek(double seconds)` | nudge de fase |
| `beatGrid()` / `bpm` | referencia de tempo y fase |
| `pitch` / `position` | lectura de estado |

## Reglas de threading (contrato duro)

1. `SyncEngine::tick()` corre SOLO en el hilo UI (QTimer).
2. El `rate` y el `seek` se escriben por sus APIs atómicas; `render()` no se toca.
3. El `BeatGrid` se lee solo cuando `valid == true`; si no, el deck queda en `Tempo` (nunca `Beat`).
