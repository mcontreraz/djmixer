# Research: Beat Sync

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

## Decisión 1: Dónde corre la corrección

- **Decision**: `SyncEngine` (QObject) en el hilo UI, tick cada ~50 ms (`QTimer`), misma cadencia
  que el refresh de posición.
- **Rationale**: constitución I — nunca se toca `render()`. El `rate` es atómico (`Deck::setPitch`)
  y el `seek` es pendiente (`m_pendingSeek`), ambos seguros desde UI.
- **Alternatives**: corregir en el hilo de audio (rechazado: contamina `render()` y mezcla ritmos);
  en el worker (rechazado: no tiene acceso al estado de play/seek de la UI).

## Decisión 2: Tempo match con octava

- **Decision**: `rateTempo = primaryEffectiveBpm / slaveBpm`, con plegado de octava: si el cociente
  cae fuera de [0.5, 2.0], se pliega ×2/×0.5 hasta quedar en ese rango (o se elige el múltiplo más
  cercano a 1.0). `primaryEffectiveBpm = primaryBpm × (1 + primaryPitch)`.
- **Rationale**: replica la equivalencia de octava observada (normaliza ×2/×0.5).
- **Alternatives**: ignorar octava (rechazado: 70 vs 140 se tratarían como tempos distintos).

## Decisión 3: Phase-lock (Beat Sync)

- **Decision**: PLL proporcional + nudge, clean-room (las ganancias de Serato no están en la ref):
  1. Error de fase en **beats**: `e = phase(primary) - phase(slave)`, envuelto a [-0.5, +0.5].
  2. Si `|e| > 0.45` beat → **nudge**: `seek` del esclavo al beat alineado más cercano (snap).
  3. Si `|e| ≤ 0.45` → corrección continua: `rate = rateTempo + kp · e`.
  4. `kp` calibrado en el autotest (arranque ~0.1, sin oscilar).
- **Rationale**: converge sin drift (SC-001) y es O(1). La fase sale de `BeatGrid::phaseAt(t)`.
- **Alternatives**: PID completo (rechazado: overkill para 2 decks; constitución IV); corrección
  solo por seek sin rate (rechazado: drift entre ticks).

## Decisión 4: Deck primario

- **Decision**: el primer deck en pasar `Off → (Armed|Tempo|Beat)` es el primario; al desactivar,
  el siguiente en sync (si hay) lo reemplaza.
- **Rationale**: replica "el primer deck impone el tempo" (beat-sync.md §Modelo).
- **Alternatives**: primario fijo (deck 1) (rechazado: no es lo que hace Serato).

## Decisión 5: Estados y modos

- **Decision**: estado por deck `Off/Armed/Tempo/Beat`; modo global `Off/Simple/Smart`. `Armed`
  entra al dar Play. `Smart` ≈ `Simple` en el MVP (downbeat = F4b).
- **Rationale**: replica los 3 modos observados y el modelo de estados documentado.
- **Alternatives**: solo on/off (rechazado: no cubre Armed ni la distinción tempo/beat).

## Decisión 6: Referencia de fase

- **Decision**: usar `BeatGrid.beats[]` + `phaseAt(t)` (ya en `beatgrid.h`) para el error de fase;
  no reanalizar.
- **Rationale**: el BeatGrid de 003 ya tiene la grilla; beat sync solo la consume.
