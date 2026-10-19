# Tasks: Key Lock + Key Analysis

**Entrada**: [spec](spec.md), [plan](plan.md), [research](research.md),
[contrato](contracts/keylock.md).
**Estado**: Todo pendiente. Esta lista no declara implementación ni tests ejecutados.

Formato: `Txxx [USn] tarea — ruta`. `[P]` permite trabajo independiente una vez
cumplidos los prerrequisitos de la fase. Los tests son obligatorios para esta
feature de DSP/transporte/análisis; no sustituirlos por comprobación visual.

## F0 — Evidencia/auditoría RT y oráculos (bloqueante)

- [x] T001 Auditar el callback (`render`) para enumerar alloc/locks/I-O residuales
  y diseñar el handoff del stage de stretch (buffers preasignados); registrar
  deuda heredada del decoder/refill — `src/deck.cpp`, `src/mixer.cpp`.
- [x] T002 [P] Crear fixtures y oráculos independientes: seno 440 Hz + patrón
  rítmico de referencia, arpegios/acordes con fundamental conocida (Do mayor,
  La menor, …) y ruido "sin tonalidad" — `tests/keylock_fixtures.cpp` (generador).
- [x] T003 [P] Definir `KeylockStage` (API header-only) y snapshot de estado;
  tests de estado/invalidación — `src/keylockstage.h`, `tests/keylock_state_test.cpp`.
- [x] T004 Registrar targets CTest de key lock + instrumentación de operaciones RT
  prohibidas — `CMakeLists.txt`, `tests/keylock_rt_test.cpp`.

**Gate F0**: los oráculos fallan por ausencia del motor, no por una expectativa
ambigua; se distinguen continuidad de pitch, bypass bit-exacto, latencia y key.
API revisada contra el contrato.

## F1 — US1/US2: stage WSOLA + bypass + toggle

- [x] T005 [US1] Implementar `KeylockStage::process` (correlación cruzada +
  crossfade equal-power) sin alloc en el callback; bypass exacto a `rate==1.0` —
  `src/keylockstage.h` (header-only, como `looptransport`).
- [x] T006 [US1] Integrar en el path normal de `Deck::render`: bifurcar
  `!keyLock || rate==1.0` → lineal actual, si no → `KeylockStage`; conservar
  `m_playedFrames += rate` y `discardConsumed` — `src/deck.h`, `src/deck.cpp`.
- [x] T007 [US2] Añadir crossfade de toggle ≤ ~10 ms entre bypass y stretch sin
  seek ni cambio de fase — `src/keylockstage.h`, `src/deck.cpp`.
- [x] T008 [US1] Validar continuidad de pitch en barrido 0.5→1.5 (SC-001) y
  bypass bit-exacto en 1.0 (SC-002) para bloques 1/64/127/256/1024 —
  `tests/keylock_dsp_test.cpp`.
- [x] T009 [US2] Validar toggle ON→OFF→ON sin discontinuidad/flanger (SC-003) y
  latencia ≤ 40 ms (SC-007) — `tests/keylock_dsp_test.cpp`.
- [x] T010 [US1] Validar cero RT prohibidas en el camino adoptado con KEY ON
  (SC-008) — `tests/keylock_rt_test.cpp`.

**Gate F1**: SC-001/002/003/007/008 verdes. Mostrar por separado error de pitch y
modificación intencional de la señal en la unión del crossfade.

## F2 — US3/US5: UI/KEY y convivencia con transporte

- [x] T011 [US5] Exponer `Q_PROPERTY(bool keyLock)` + `setKeyLock(bool)` y NOTIFY
  desde snapshot — `src/deck.h`, `src/deck.cpp`.
- [x] T012 [US5] Cablear el botón KEY de `DeckPanel.qml` (ya stubbed) al slot;
  LED solo tras confirmación del motor — `src/DeckPanel.qml`.
- [ ] T013 [US3] Verificar que sync/bend/scratch no rompen el key lock: bend pasa
  por el stage; scratch conserva su resampler y retoma KEY al soltar —
  `tests/keylock_sync_test.cpp`, `src/deck.cpp`.
- [ ] T014 [P] [US5] Acción lógica MIDI `key_lock` + feedback sin inventar CC;
  note-on/off y ordenación — `src/midicontroller.*`, `tests/midi_binding_test.cpp`.
- [ ] T015 [US5] Tests QML con backend real o fixture contractual para el toggle
  y su confirmación — `tests/qml/tst_keylock_controls.qml`.

**Gate F2**: SC-009 (regresión sync/scratch) verde; el botón refleja estado
confirmado y no dispara doble toggle.

## F3 — US4: key analysis + Camelot + caché

- [x] T016 [US4] Detectar key en `WaveformAnalyzer` con `qm-dsp GetKeyMode` sobre
  `monoBuf` (A=440), con umbral de confianza → `analyzedKey` — `src/waveformanalyzer.cpp`.
- [x] T017 [US4] Extender `TrackMeta` (`analyzedKey`, `keySource`) y versionar el
  sidecar; precedencia tag>análisis; persistir/leer en `WaveformCache` —
  `src/waveformcache.h`, `src/waveformcache.cpp`.
- [x] T018 [US4] Mapeo índice `GetKeyMode` (0–24) → Camelot `1A`–`12B` (tabla
  propia) + test de biyección (SC-005) — `src/keynotation.h`, `tests/key_analysis_test.cpp`.
- [x] T019 [US4] Alimentar el badge del deck (`Deck::key`/`keyText`) y la columna
  `key` de la biblioteca con el key (tag o análisis) — `src/deck.cpp`,
  `src/DeckPanel.qml`, `src/LibraryPanel.qml`.
- [x] T020 [US4] Validar key de fixtures conocidos (SC-004), mapeo (SC-005) y
  caché sin re-decodificar (SC-006) — `tests/key_analysis_test.cpp`,
  `tests/grid_cache_test.cpp`.

**Gate F3**: SC-004/005/006 verdes; un análisis obsoleto (generación vieja) no
pisa la pista actual.

## F4 — Cierre de implementación

- [ ] T021 Ejecutar suite completa y guardar métricas, WAVs sintéticos
  comparativos (pitch fijo vs varispeed) y resultados RT — `docs/keylock-validation.md`.
- [ ] T022 Capturar app (1600×860 y mínimo vigente) con KEY ON/OFF y key visible
  en deck/biblioteca; revisar visualmente — `docs/keylock-validation.md`.
- [ ] T023 Escuchar fixtures (manual): seno/arpegio con KEY ON en barrido,
  música propia y percusión; registrar límites y artefactos — `docs/keylock-validation.md`.
- [ ] T024 Revisar FR→tests, presupuesto, no regresión y licencias (qm-dsp GPL ya
  licenciado); actualizar estado de esta feature solo tras cumplir gates —
  `specs/016-key-lock/`.

Dependencias: F0→F1→F2→F3→F4. T014 puede prepararse con el contrato, pero no
habilitar acciones de producción hasta disponer del motor y su confirmación.
