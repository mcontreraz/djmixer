# Data Model: Needle Search

Sin entidades nuevas. Reutiliza:

| Entidad existente | Uso en esta feature |
|---|---|
| `Deck.position` / `Deck.duration` | base del cálculo fracción→segundos y tiempo visible |
| `Deck::seek(seconds)` | único punto de salto (hilo UI → flag atómico → hilo audio) |
| `WaveformView.visibleSeconds` | escala tiempo↔píxel en las grandes |

Sin contratos nuevos (`contracts/` queda vacío a propósito): la interfaz es
`Deck.seek`, ya cubierta.
