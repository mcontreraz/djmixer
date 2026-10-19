# Plan: MasterClock explícito (010)

**Fecha**: 2026-10-14 | **Ref**: `docs/referencia-traktor/` (MasterClock,
SyncUnit, `canPhaseSync`, `setSyncMaster`) + Serato (primario implícito).

## Diagnóstico

Hoy el "maestro" es implícito y disperso: `m_tempoRef`/`m_phaseRef` +
`ensurePrimary` + `recomputeRefs` + regla takeover en `setSync`. Funciona
pero cada caso (pausa, re-enganche, doble sync) es una rama más. Traktor lo
centraliza: un **MasterClock** con autoridad de tempo y SyncUnits que miden
offset en beats contra el reloj.

## Qué cambia (6 piezas)

### 1. MasterClock con dueño explícito
- Nuevo: `masterDeck: int (-1)` + `masterAuto: bool (default true)`.
- Auto: primer deck sonando con datos (equivale al implícito actual).
- Manual: botón MASTER por deck (como Traktor) fija dueño; otro botón lo
  libera a auto. `setSyncMaster` existe en la evidencia: hay que cablearlo.
- El maestro nunca se corrige; si deja de sonar/datos → auto reelige.

### 2. Slaves miden offset contra el reloj
- Hoy: esclavo vs grid del maestro directamente.
- Nuevo: `phaseOffsetBeats(deck)` centralizado (equivale a
  `computePhaseSyncOffsetInBeats`): error envuelto en beats + eBar para el
  snap a downbeat. Misma matemática, una sola autoridad.
- El objetivo de tempo sale del reloj (tempo local del maestro × su pitch),
  no de cada esclavo por su lado.

### 3. Gates `canPhaseSync`
- Fase solo si: ambos con grid válida + sonando + tempo en rango + no
  scratch. Si no → Tempo Sync (solo BPM). Hoy está desperdigado en `tick`;
  pasa a una función que el test puede llamar directo.

### 4. Takeover → reasignación de master
- La regla actual (enganche fresco + otro sonando = otro manda) se
  reexpresa: enganchar X con master en auto y otro sonando = el otro sigue
  (o pasa a) maestro. Sin ramas nuevas: es `setSyncMaster(auto)`.
- Doble sync: el primero en enganchar lidera (coincide con REA Serato).

### 5. UI: indicador + botón MASTER por deck
- Badge MASTER en el deck dueño (como Traktor); click fija/libera.
- El pill SYNC sigue igual (esclavo). Nada más cambia visualmente.

### 6. Quantize alineado al reloj
- Q hoy no gatea nada. Definición: eventos (cue/play/snap de enganche)
  cuantizados al reloj del master. Sin inventar: solo enganche + cue.

## Qué NO cambia

Bandas Mixxx, octavas 4/3-2/3, snap a downbeat al enganchar, cadena de
detección, sidecar, pitch relativo, display states.

## Orden + verificación

1. MasterClock + gates con tests del harness (direcciones A↔B ya verdes).
2. Offset centralizado (misma matemática; el sync-test no debe moverse).
3. UI MASTER + quantize de enganche.
4. Veredicto: sync 120vs126 ambas direcciones + pausa-del-maestro (flip)
   + re-enganche, todo exit=0.

## Riesgo

Regresión de comportamiento que hoy "se siente bien": cada pieza se
mergea con el sync-test en verde antes/después (mismos lockMs ±20%).
