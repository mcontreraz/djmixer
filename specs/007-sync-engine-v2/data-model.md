# Data Model: Sync Engine v2

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

## SyncState (por deck, existe en `SyncEngine`; se recalibra)

| Campo | Tipo | Reglas |
|---|---|---|
| `state` | Off/Armed/Tempo/Beat | Transiciones según `beat-sync.md` (Armed entra con Play) |
| `quantize` | bool | gate de la corrección de fase (pill Q) |
| `userOffset` | double beats | bend manual absorbido; se resetea al enganchar |
| `lastAdjustment` | double | para el tope de delta 0.02 por tick |

## SyncMetrics (solo test)

| Campo | Tipo | Reglas |
|---|---|---|
| `lockMs` | i64 | ms hasta phaseErr <0.02 estable 500 ms |
| `phaseErr` | double beats | error final líder–seguidor |
| `overshoot` | double | máximo sobrepaso observado (informativo) |

## BeatGrid (existente, sin cambios)

`phaseAt(t)` + `nextBeatAtOrAfter(t)` alimentan distancia de beat y seek de
enganche. Downbeat real sigue futuro (heurística módulo 4 cuando toque).
