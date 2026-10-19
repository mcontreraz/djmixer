# Tasks: Traktor-parity Sync (010)

## Fase A — MasterClock

- [ ] T001 `SyncEngine`: `masterDeck/auto` + `setMasterDeck(i)` + badge Q_PROPERTY; `m_tempoRef` leído del reloj
- [ ] T002 Gates `canPhaseSync(deck)` centralizados (grids + sonando + rango + no scratch)
- [ ] T003 Offset en beats centralizado `phaseOffsetBeats()` (misma matemática del tick)
- [ ] T004 Takeover reexpresado como reasignación; UI MASTER por deck
- [ ] T005 Sync-test A→B + B→A + flip-por-pausa exit=0, lockMs ±20%

## Fase B — Histograma + coherencia

- [ ] T006 `IntervalHistogram` sobre onset-envelope (candidatos + coherencia + plantillas 4/4)
- [ ] T007 Enganche en la cadena (antes del refinado) + benchmark set conflictivo
- [ ] T008 Grep-control SC-003 + autotest completo exit=0 + commit
