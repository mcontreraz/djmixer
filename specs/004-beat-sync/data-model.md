# Data Model: Beat Sync

## SyncState (enum, por deck)

| Valor | Significado |
|---|---|
| `Off` | sin sync; rate manual |
| `Armed` | armado; entra a sync al dar Play |
| `Tempo` | tempo alineado (rate = tempo del primario), fase libre |
| `Beat` | tempo + fase alineados (PLL activo) |

## SyncMode (enum, global)

| Valor | Significado (MVP) |
|---|---|
| `Off` | sync deshabilitado |
| `Simple` | alinea beat (transients) |
| `Smart` | = Simple en el MVP (downbeat real es F4b) |

## SyncEngine (QObject, hilo UI)

| Miembro | Rol |
|---|---|
| `Deck *primary` | el deck que impone el tempo (o null) |
| `SyncState state[2]` | estado por deck (A=0, B=1) |
| `SyncMode mode` | modo global |
| `double kp` | ganancia del PLL (calibrada) |
| `tick()` | cada 50 ms: aplica tempo + fase a cada esclavo |

Relaciones: `SyncEngine 1—2 Deck`. `Deck.beatGrid` (existente) aporta `bpm` y `phaseAt(t)`.
`Deck.pitch` es el `rate - 1` (atómico); `Deck.seek(seconds)` es el nudge.

## Invariantes

- `primary` es null ⟺ ningún deck en `Tempo`/`Beat`/`Armed`.
- El esclavo nunca escribe el rate del primario (solo el primario puede cambiar su propio pitch).
- Desactivar sync restaura el `rate` manual capturado al activar (FR-008).
