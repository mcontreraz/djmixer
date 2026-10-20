# Tasks: Serato Grid Import

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

**Feature**: `008-serato-grid-import` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Setup

- [x] T001 Crear `seratogrid.h/.cpp` (no publicado) vacíos con `SeratoGrid::parse()` stub (retorna `ok=false`) + wiring en CMake
- [x] T002 Añadir al autotest (`main.cpp` (no publicado)) un caso `serato-grid` que corre `parse()` sobre fixture y reporta PASS/FAIL sin romper el resto

## Phase 2: Foundational (bloquea US1/US2/US3)

- [x] T003 Implementar lector payload v1 (cabecera, N BE+syncsafe, records 8 B, terminal, tail 0-2 B) según `serializer-v1.md`
- [x] T004 Implementar validador (tiempos crecientes, BPM>0 finito, ≤128 marcadores, N=0 → inválido)
- [x] T005 Verificar T003-T004 contra oráculo: los 12 casos de `verify_blob.py` reproducidos en C++ dan idéntico veredicto
- [x] T006 Bump sidecar a v8 (`locked:u8` + `source:u8`, lector v7+v8) en `waveformcache.*` (no publicado)

## Phase 3: US1 — MP3 con grid Serato (P1)

- [x] T007 [US1] Extraer frame GEOB `Serato BeatGrid` vía TagLib ID3v2 en `SeratoGrid::parse()`
- [x] T008 [US1] Conversión payload→beats (interpolar por tramo + extender terminal) y poblar `BeatGrid{source=serato}`
- [x] T009 [US1] Enganchar en `WaveformAnalyzer`: intentar import antes de detectar; fallback intacto
- [x] T010 [US1] Exponer `Deck.gridSource` (Q_PROPERTY solo lectura) + badge en `DeckPanel.qml`
- [x] T011 [US1] Autotest con MP3 tageado real: BPM == tag ±0.01, beats == `beatgrid_blob.py`

## Phase 4: US2 — M4A con grid Serato (P2)

- [x] T012 [US2] Inspeccionar bytes reales del átomo en un .m4a propio (script solo-lectura) y documentar wrapper
- [x] T013 [US2] Extraer `----:com.serato.dj:beatgrid` vía TagLib MP4 y reutilizar T003/T008
- [x] T014 [US2] Verificación con M4A tageado real (mismo criterio que T011)

## Phase 5: US3 — Locked + fallback (P2)

- [ ] T015 (PLUMBING HECHO: campo+caché v8; bit de lock en Markers2 pendiente de formato) [US3] Detectar lock en tags (`Markers2`/BpmLock si presente) → `BeatGrid.locked`
- [x] T016 [US3] Re-análisis con caché v8 locked → conservar sin tocar
- [x] T017 [US3] Payload corrupto / versión != 1.0 → fallback a detección + log, deck suena igual
- [x] T018 [US3] Sin tag → comportamiento idéntico al actual (autotest completo verde)

## Phase 6: Polish

- [x] T019 Limpiar instrumentación/debug del feature; `008-*/checklists` (no publicado) al día
- [ ] T020 Commit en español con la feature + actualizar `docs/` (no publicado) si cambia el formato sidecar

## Dependencies

T003→T004→T005→(T007,T012); T006∥cualquiera; T007→T008→T009→T010→T011; T012→T013→T014; T015→T016; T017,T018 tras T009.
