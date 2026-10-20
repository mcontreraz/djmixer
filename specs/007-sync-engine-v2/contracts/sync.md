# Contracts: Sync Engine v2 (QML ⟷ C++)

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../../docs/referencia-local.md, no publicado).

## SyncEngine (existente, se extiende)

| Miembro | Forma | Descripción |
|---|---|---|
| `quantize` | `Q_PROPERTY bool` | gate de fase (pill Q); sin Q solo tempo |
| `engageDeck(i)` | slot/Q_INVOKABLE | beat-match seek (regla 1/8) + PLL |
| `lockMs` / `phaseErr` | solo test (log) | métricas de convergencia |

## Reglas

1. Corrector solo vía `Deck::setPitch`/`seek` (nunca toca audio).
2. Scratch/grab congela la aportación de ese deck al sync.
3. Sin beatgrid válido en algún deck: solo tempo, nunca fase.
4. Citar origen de cada constante en comentario (`Mixxx bpmcontrol.cpp` o `beat-sync.md`+función).
