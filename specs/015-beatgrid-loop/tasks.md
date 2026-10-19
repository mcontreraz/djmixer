# Tasks: Loops exactos por beatgrid

**Entrada**: [spec](spec.md), [plan](plan.md), [research](research.md),
[modelo](data-model.md), [contrato](contracts/loop.md).
**Estado**: Todo pendiente. Esta lista no declara implementación ni tests ejecutados.

Formato: `Txxx [USn] tarea — ruta`. `[P]` permite trabajo independiente una vez
cumplidos los prerrequisitos de la fase. Los tests son obligatorios para esta
feature de transporte/DSP; no sustituirlos por comprobación visual de botones.

## F0 — Oráculos y base RT (bloqueante)

- [x] T001 Auditar lectura/seek/refill/alloc/destrucción del callback y diseñar handoff
  streaming↔loop; registrar deuda residual — `src/deck.cpp`, `src/mixer.cpp`, `docs/loop-validation.md`.
- [x] T002 [P] Crear fixtures sintéticos y oráculo independiente de grid/cursor:
  BPM no entero, grid variable, extremos fraccionales y loop corto — `tests/loop_transport_test.cpp`.
- [x] T003 [P] Definir intenciones/snapshots, seriales, generaciones y prioridades;
  tests de invalidación/cola llena — `src/looptransport.h`, `tests/loop_state_test.cpp`.
- [x] T004 Registrar targets CTest de loop y la instrumentación de operaciones RT
  prohibidas — `CMakeLists.txt`, `tests/loop_rt_test.cpp`.

**Gate F0**: oráculos fallan por ausencia del motor, no por una expectativa ambigua;
se distinguen datos de grid, cadencia, sonido y sync. API revisada contra contrato.

## F1 — PCM preparado y publicación

- [x] T005 Crear worker de PCM con decoder exclusivo, pool limitado y contabilidad
  de memoria — `src/looppcmcache.h`, `src/looppcmcache.cpp`.
- [x] T006 Implementar pin/retire/ack, guards y rechazo de resultados obsoletos;
  ninguna liberación por último refcount en audio — `src/looppcmcache.*`.
- [x] T007 Integrar lector residente y continuación normal tras Exit sin seek/I/O
  en callback; preparar regiones antes de publicar Ready — `src/deck.h`, `src/deck.cpp`.
- [x] T008 Probar 16 beats a 120 BPM (>5.5 s de historial), máximo 64 s, presión
  de memoria, dos decks, load durante preparación y continuidad al salir — `tests/loop_rt_test.cpp`.

**Gate F1**: cero operaciones RT prohibidas en el camino adoptado; presupuesto de
64 MiB/deck incluye buffers simultáneos. Miss nunca se transforma en silencio.

## F2 — US1: Auto Loop y wrap

- [x] T009 [US1] Validar mapa y calcular A/B con `timeAt`, snap por subdivisión y
  límites de pista; conservar double — `src/looptransport.cpp`.
- [x] T010 [US1] Implementar Preparing/Armed con frontera futura y late-event policy,
  captura con caché lista y estados en pausa — `src/looptransport.*`, `src/deck.*`.
- [x] T011 [US1] Renderizar `[A,B)` con overshoot, múltiples wraps, interpolación
  periódica y EOF posterior al wrap; no reutilizar seek — `src/deck.cpp`.
- [x] T012 [US1] Validar 10 000 vueltas, bloques 1/64/127/256/1024, tasas variables,
  límites fraccionales, EOF y cruces de tempo — `tests/loop_transport_test.cpp`.
- [x] T013 [US1] Añadir anti-click de duración acotada que no cambia D; preparar
  guards/EOF y medir discontinuidad/transitorios — `src/looptransport.*`, `tests/loop_audio_test.cpp`.

**Gate F2**: SC-001/002/003/004 verdes. Mostrar por separado error del reloj y
modificación intencional de la señal en la unión.

## F3 — US2: Resize, Exit, Reloop y gestos

- [x] T014 [US2] Implementar misma longitud=Exit, otra=Resize, ÷2/×2 y región last;
  commit solo con caché lista — `src/looptransport.*`.
- [x] T015 [US2] Exit desde p con handoff preparado; Reloop pausado/sonando sin
  adoptar semántica Slip — `src/deck.cpp`, `tests/loop_state_test.cpp`.
- [x] T016 [US2] Cablear cancelación previa a scratch/needle/cues/seek/load y
  adopción diferida de revisiones — `src/deck.*`, `tests/loop_state_test.cpp`.
- [x] T017 [US2] Probar reducción con p fuera, ampliación fallida, seriales tardíos,
  cola llena y Exit prioritario — `tests/loop_state_test.cpp`, `tests/loop_rt_test.cpp`.

## F4 — US3: fase musical y sync

- [x] T018 [US3] Publicar cursor audible y beat continuo coherentes; acumular L
  por wrap y preservar fase al resize/Exit — `src/deck.*`, `src/mixer.*`.
- [x] T019 [US3] Extender cálculo de fase para coordenadas musicales, mantener
  BPM local de p y revisión fijada; no generar engage/seek por wrap — `src/syncalign.h`, `src/audiosync.h`, `src/syncengine.cpp`.
- [x] T020 [US3] Suspender/reiniciar detector en vivo durante loop sin publicar
  timestamps falsos; conservar grid fijado — `src/deck.cpp`, `src/beatdetector.*`.
- [x] T021 [US3] Cubrir maestro/seguidor, microloops, 1/2 beats en compás, octavas,
  grid variable, pitch bend, salida/reloop y cambio de maestro — `tests/loop_sync_test.cpp`.

**Gate F4**: SC-005/006 verdes; loop no altera las guardas de sync para reproducción normal.

## F5 — US4: UI y MIDI

- [x] T022 [US4] Exponer propiedades/acciones y NOTIFY desde snapshots — `src/deck.h`, `src/deck.cpp`.
- [x] T023 [US4] Habilitar botones existentes y controles compactos Exit/Reloop/÷2/×2;
  estado Preparing y razones de indisponibilidad — `src/DeckPanel.qml`.
- [x] T024 [US4] Dibujar intervalo activo y marcas IN/OUT en overview/scroll sin
  cambiar posición audible — `src/components/WaveformView.qml`, `src/Main.qml`.
- [x] T025 [P] [US4] Añadir acciones lógicas MIDI y feedback, sin inventar CC físicos;
  probar note-on/off y ordenación — `src/midicontroller.*`, `tests/midi_binding_test.cpp`.
- [x] T026 [US4] Tests QML con backend real o fixture contractual para activación,
  preparación, rechazo, resize y feedback sin recursión — `tests/qml/tst_loop_controls.qml`.

## F6 — Cierre de implementación

- [x] T027 Ejecutar suite completa y guardar métricas del [quickstart](quickstart.md),
  WAVs sintéticos comparativos y resultados RT — `docs/loop-validation.md`.
- [x] T028 Capturar app en 1600×860 y mínimo vigente, con pista/loop preparado,
  activo y sin grid; revisar visualmente — `docs/loop-validation.md`.
- [ ] T029 Escuchar fixtures periódicos (manual: pendiente de escucha en la app;
  la cobertura programática de discontinuidad/anti-click vive en loop_audio_test), DC/discontinuidad, percusión y música
  propia en entradas/wraps/resize/Exit; registrar límites — `docs/loop-validation.md`.
- [x] T030 Revisar FR→tests, presupuesto, no regresión y licencias; actualizar
  estado de esta feature solo tras cumplir gates — `specs/015-beatgrid-loop/`.

Dependencias: F0→F1→F2→F3→F4→F5→F6. T025 puede prepararse con el contrato, pero
no habilitar acciones de producción hasta disponer del motor y su confirmación.
