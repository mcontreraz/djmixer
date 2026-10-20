# Tasks: Key Lock + Key Analysis

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Entrada**: [spec](spec.md), [plan](plan.md), [research](research.md),
[contrato](contracts/keylock.md).
**Estado**: F0–F3 cerradas en `main`; F4 abierta.

> **Reconciliada con el código (2026-10-19).** Esta lista mezclaba tareas
> hechas contra un motor WSOLA propio que se descartó, con tareas hechas
> contra el motor que hoy se despacha. Cada tarea dice ahora contra qué
> commits y con qué fichero de test se sostiene, y las que se hicieron con
> código que ya no existe están marcadas como **sustituidas**, no como
> completadas. Los ficheros citados son los que existen hoy en el repo.

Formato: `Txxx [USn] tarea — ruta`. `[P]` permite trabajo independiente una vez
cumplidos los prerrequisitos de la fase. Los tests son obligatorios para esta
feature de DSP/transporte/análisis; no sustituirlos por comprobación visual.

Leyenda de estado: `[x]` = hecha y **verificada por un test que existe en el
repo**; `[~]` = hecha pero sustituida por otro camino (se conserva el rastro
del commit); `[ ]` = pendiente.

## F0 — Evidencia/auditoría RT y oráculos (bloqueante)

- [x] T001 Auditar el callback (`render`) para enumerar alloc/locks/I-O residuales
  y diseñar el handoff del motor de stretch (buffers preasignados); registrar
  deuda heredada del decoder/refill — `deck.cpp` (no publicado), `mixer.cpp` (no publicado).
  Auditoría publicada en `docs/loop-validation.md`.
- [~] T002 [P] Crear fixtures y oráculos independientes: seno de referencia
  + arpegios/acordes con fundamental conocida (Do mayor, La menor, …) y ruido
  "sin tonalidad" — **sustituida**: los fixtures viven hoy dentro de
  `keyanalysis_test.cpp` (no publicado) (arpegios, ruido) y `keylock_loop_test.cpp` (no publicado)
  (seno de 480 Hz). No hay fichero generador de fixtures aparte.
- [~] T003 [P] Definir la API del motor de stretch y el snapshot de estado;
  tests de estado/invalidación — **sustituida** por `04e8de0` (el motor pasó a
  ser Rubber Band) y `64cf46b` (motor siempre caliente). La API real es la de
  `RubberBand::RubberBandStretcher`; no hay módulo propio `KeylockStage` ni
  `KeylockSnapshot`: el estado vive en `Deck::m_keyLock` (atómico) y en
  `Deck::m_kl*`.
- [~] T004 Registrar targets CTest de key lock + instrumentación de operaciones
  RT prohibidas — **parcialmente sustituida**: los targets CTest existen
  (`CMakeLists.txt`: `keylock_audio`, `keylock_loop`, `keylock_loop_phase`,
  `keylock_click`, `keyanalysis`). La instrumentación RT existe para el camino
  de loop (`loop_rt_test.cpp` (no publicado)) pero **no** para el camino de key lock
  (SC-008 abierto).

**Gate F0**: los oráculos fallan por ausencia del motor, no por una expectativa
ambigua; se distinguen continuidad de pitch, bypass bit-exacto, latencia y key.
API revisada contra el contrato.

## F1 — US1/US2: motor de stretch + bypass + toggle

- [~] T005 [US1] Implementar el motor de stretch sin alloc en el callback —
  **sustituida** por `04e8de0`: el motor es `RubberBand::RubberBandStretcher`
  (GPL) en modo real-time con transientes mixtos, con buffers preasignados
  (`Deck::m_klInL/R`, `m_klOutL/R`, `m_klFadeBuf`, `m_klLoopIn`).
- [~] T006 [US1] Integrar en el path normal de `Deck::render` — **sustituida**
  por `04e8de0`, `10a21d7` (ratio invertido) y `117c768`/`64cf46b` (alimentación
  exacta, motor caliente). La integración vive en `deck.cpp` (no publicado).
- [x] T007 [US2] Crossfade de toggle entre path directo y stretch — 1024 frames
  de rampa propia, simétrica, en entrada y en salida (`a1adeda` entrada,
  `1bfd056` salida). El crossfade **hizo clic** y se corrigió en `a0a837e`
  (rampa que se reiniciaba por bloque, el path de loop que releía el
  transporte, el buffer del bloque anterior en el fade de salida y el resto
  fraccionario del acumulador). La prueba que lo afirma, con umbral y prueba
  de la prueba, está en `keylock_click_test.cpp` (no publicado)
  ([DJM-28](/DJM/issues/DJM-28)).
- [x] T008 [US1] Validar continuidad de pitch con KEY ON y bypass con KEY OFF —
  `keylock_loop_test.cpp` (no publicado) (480 Hz conservados a rate 1.2 dentro del loop;
  576 Hz con KEY OFF) y `keylock_audio_test.cpp` (no publicado) (480 Hz con y sin KEY a
  rate 1.0).
- [x] T009 [US2] Validar la transición de toggle (SC-003) y la latencia
  (SC-007) — la transición está **afirmada** por `keylock_click_test.cpp` (no publicado)
  (umbral contra la referencia en régimen, en path normal y de loop, más la
  prueba de la prueba con el crossfade a 0); la latencia está **medida**:
  `getLatency()` = 1024 muestras ≈ 21.3 ms a 48 kHz con la configuración real
  del deck.
- [ ] T010 [US1] Validar cero RT prohibidas en el camino de key lock con KEY
  ON (SC-008) — el arnés de `loop_rt_test.cpp` (no publicado) no cubre este camino;
  falta el oráculo.

**Gate F1**: SC-001/002/007/008 verdes. Mostrar por separado error de pitch y
modificación intencional de la señal en la unión del crossfade.

## F2 — US3/US5: UI/KEY y convivencia con transporte

- [x] T011 [US5] Exponer `Q_PROPERTY(bool keyLock)` + `setKeyLock(bool)` y su
  `NOTIFY` — `deck.h` (no publicado), `deck.cpp` (no publicado). Ojo: el `NOTIFY` se emite en el hilo
  de UI al conmutar; no hay confirmación separada desde el hilo de audio.
- [x] T012 [US5] Cablear el botón KEY de `DeckPanel.qml` al slot — `DeckPanel.qml` (no publicado).
- [x] T013 [US3] Verificar que sync/bend/scratch no rompen el key lock —
  `keylock_loop_phase_test.cpp` (no publicado) (la fase audible se compensa: un deck
  con loop+KEY y otro con play+KEY no derivan) y `keylock_loop_test.cpp` (no publicado).
  El scratch queda fuera del key lock por construcción (su propio resampler).
- [ ] T014 [P] [US5] Acción lógica MIDI `key_lock` + feedback sin inventar CC;
  note-on/off y ordenación — `midicontroller.cpp` (no publicado) (hoy `keylock` está en la
  lista de acciones reservadas), `midi_binding_test.cpp` (no publicado).
- [ ] T015 [P] [US5] Tests QML con backend real o fixture contractual para el
  toggle y su confirmación — `qml/` (no publicado) (hoy solo hay `tst_mixer_controls.qml`).

**Gate F2**: SC-009 (regresión sync/scratch) verde; el botón refleja el estado
confirmado y no dispara doble toggle.

## F3 — US4: key analysis + Camelot + caché

- [x] T016 [US4] Detectar key en el hilo del analyzer con `qm-dsp GetKeyMode`
  sobre `monoBuf` (A=440), con umbral de confianza → `analyzedKey` —
  `keyanalyzer.cpp` (no publicado) (detector), `waveformanalyzer.cpp` (no publicado) (invocación).
- [x] T017 [US4] Extender `TrackMeta` (`analyzedKey`, `keySource`) y versionar
  el sidecar; precedencia tag>análisis; persistir/leer en `WaveformCache` —
  `waveformcache.h` (no publicado), `waveformcache.cpp` (no publicado).
- [x] T018 [US4] Mapeo índice `GetKeyMode` (0–24) → Camelot `1A`–`12B` (tabla
  propia) + test de biyección (SC-005) — `keynotation.h` (no publicado),
  `keyanalysis_test.cpp` (no publicado).
- [x] T019 [US4] Alimentar el badge del deck (`Deck::key`/`keyText`) y la
  columna `key` de la biblioteca con el key (tag o análisis) — `deck.cpp` (no publicado),
  `DeckPanel.qml` (no publicado), `LibraryPanel.qml` (no publicado).
- [x] T020 [US4] Validar key de fixtures conocidos (SC-004), mapeo (SC-005) y
  caché sin re-decodificar (SC-006) — `keyanalysis_test.cpp` (no publicado),
  `grid_cache_test.cpp` (no publicado).

**Gate F3**: SC-004/005/006 verdes; un análisis obsoleto (generación vieja) no
pisa la pista actual.

## F3bis — Alineación del motor con el path directo (DJM-36)

- [ ] T025 [US2] Calibrar el retardo efectivo del motor **en el hilo de UI, al
  construir el deck** (no `getLatency()`): una ráfaga por el motor, medir el
  desfase real del contenido → `deck.h` (no publicado), `deck.cpp` (no publicado).
- [ ] T026 [US2] Alimentar el motor `Δ` muestras de fuente por delante del
  cursor (Δ = retardo calibrado), en el path normal **y** en el de loop, para
  que el crossfade mezcle el mismo instante de material — `deck.cpp` (no publicado)
  (FR-018).
- [ ] T027 [US2] Compensar la fase audible de sync con el retardo calibrado
  (FR-019) — `deck.cpp` (no publicado) (`syncPositionSeconds`).
- [ ] T028 [US2] Oráculos C1 (sin deslizamiento: correlación cruzada con pico
  en lag 0 ± 64 frames a `rate=1.0`) y C4 (fase de sync dentro de 2 ms), con
  su "prueba de la prueba" — `keylock_alignment_test.cpp` (no publicado).
- [ ] T029 [US2] Publicar la profundidad del batido durante la transición
  (C3) como métrica del test, no como afirmación — `keylock_alignment_test.cpp` (no publicado).

**Gate F3bis**: C1 y C4 verdes (hoy fallan), C3 medida y publicada, C2 sin
regresión.

## F4 — Cierre de implementación

- [ ] T021 Ejecutar la suite completa y guardar métricas, WAVs sintéticos
  comparativos (pitch fijo vs varispeed) y resultados RT — informe de
  validación de key lock.
- [ ] T022 Capturar app (1600×860 y mínimo vigente) con KEY ON/OFF y key visible
  en deck/biblioteca; revisar visualmente.
- [ ] T023 Escuchar fixtures (manual): seno/arpegio con KEY ON en barrido,
  música propia y percusión; registrar límites y artefactos — con la validación
  auditiva de [DJM-2](/DJM/issues/DJM-2).
- [ ] T024 Revisar FR→tests, presupuesto, no regresión y licencias (qm-dsp y
  Rubber Band son GPL: todo binario distribuido trae el source completo;
  el árbol del Pro sustituye el motor, no lo licencia) — `docs/promise.md`,
  `docs/business-model.md`.

Dependencias: F0→F1→F2→F3→F4. T014 puede prepararse con el contrato, pero no
habilitar acciones de producción hasta disponer del motor y su confirmación.
