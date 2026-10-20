# Tasks: Waveform Heatmap

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Input**: Design documents from `/specs/001-waveform-heatmap/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Build wiring y base sin lógica de análisis

- [X] T001 Add `waveformcache`/`waveformanalyzer` sources to `CMakeLists.txt`
- [X] T002 [P] Define `.wfcache` binary format constants (magic `DJW1`, version) in `waveformcache.h` (no publicado)

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Entidad caché + worker + extensión Deck; nada visual aún

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Implementar lector/escritor sidecar + clave sha1(ruta|tamaño|mtime) en `waveformcache.cpp` (no publicado)
- [X] T004 [P] Implementar banco de 3 biquads (lowpass 250 Hz / highpass 4 kHz / medios por diferencia) en `waveformanalyzer.cpp` (no publicado)
- [X] T005 Implementar worker `WaveformAnalyzer` (QThread, job por deck, aborto por `analysisGeneration`, entrega queued) en `waveformanalyzer.cpp` (no publicado)
- [X] T006 Extender `Deck` (`deck.h/.cpp` (no publicado)): contador generacional, propiedad `waveform`, señales `waveformChanged`/`waveformReady`
- [X] T007 Limpieza LRU (techo 500 MB) al arrancar en `main.cpp` (no publicado)

**Checkpoint**: Foundation ready - user story implementation can now begin

## Phase 3: User Story 1 - Overview real (Priority: P1) 🎯 MVP

**Goal**: El overview del deck dibuja picos reales del tema cargado

**Independent Test**: Cargar el WAV de prueba → overview con forma real + playhead proporcional (captura `DJMIXER_SCREENSHOT`)

- [X] T008 [US1] Decode miniaudio + picos overview (256 buckets) en worker `waveformanalyzer.cpp` (no publicado)
- [X] T009 [US1] Disparar análisis en `Deck::loadFile` y publicar caché en `deck.cpp` (no publicado)
- [X] T010 [US1] Dibujar overview desde `cache` + fondo vacío si nula en `components/WaveformView.qml` (no publicado)
- [X] T011 [US1] Extender autotest en `main.cpp` (no publicado): existe sidecar tras la corrida
- [X] T012 [US1] Verificar con captura: overview real vs simulación anterior

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

## Phase 4: User Story 2 - Heatmap por bandas (Priority: P2)

**Goal**: Waveforms grandes con colores graves/medios/agudos deterministas

**Independent Test**: Tema con intro suave + drop → colores distintos por sección; mismo tema recargado = mismos colores

- [X] T013 [P] [US2] Calcular RGB por bucket desde envolventes de banda en `waveformanalyzer.cpp` (no publicado)
- [X] T014 [P] [US2] Nivel detalle (4096 buckets) en formato + lectura en `waveformcache.cpp` (no publicado)
- [X] T015 [US2] Waveforms grandes desde nivel detalle (beat numbers + playhead) en `components/WaveformView.qml` (no publicado)
- [X] T015b [US2] Modo scroll en grandes: línea central fija, la forma avanza con `position`, rejilla de segundos (propiedades `scrolling`, `visibleSeconds`, `position`) en `components/WaveformView.qml` (no publicado)
- [X] T015c [US2] Botones zoom +/− por fila (escala `visibleSeconds` en pasos 15/30/60/120/240) en `Main.qml` (no publicado)
- [X] T016 [US2] Assert determinismo: doble análisis del WAV produce bytes idénticos (autotest `main.cpp` (no publicado))

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

## Phase 5: User Story 3 - Fondo + caché (Priority: P3)

**Goal**: Análisis sin cortar audio, recarga instantánea, cancelación y degradación limpia

**Independent Test**: Play en deck B + análisis en deck A sin clicks; recarga <300 ms; archivo corrupto sin crash

- [X] T017 [US3] Probar no-interferencia: autotest con play en deck B durante análisis en deck A
- [X] T018 [US3] Medir recarga cacheada <300 ms (log de tiempos en autotest `main.cpp` (no publicado))
- [X] T019 [US3] Cancelación: recargar deck a mitad de análisis, verificar descarte limpio
- [X] T020 [US3] Degradación: `.txt` renombrado a `.wav` → overview vacío + log, deck operativo

**Checkpoint**: All user stories should now be independently functional

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cierre F2

- [X] T021 Ejecutar las 5 validaciones de `quickstart.md` y adjuntar evidencias
- [X] T022 [P] Eliminar path de simulación vieja de `WaveformView.qml` si queda muerto
- [X] T023 Actualizar `README.md` (hito M5 waveform) y el `README.md` de la referencia local de Serato (`referencia-serato/README.md` (no publicado), no publicada) si aplica

## Dependencies & Execution Order

- **Setup (Phase 1)**: no dependencies, inmediato.
- **Foundational (Phase 2)**: bloquea todo (T003→T005→T006 en orden; T004 y T007 en paralelo).
- **US1 → US2 → US3** secuencial por prioridad; US2 reutiliza worker y caché de US1.
- **Polish**: al final.

### Parallel Opportunities

- T002, T004, T007 corren en paralelo (archivos distintos).
- T013 y T014 en paralelo (cálculo vs formato).
- T021 corre captura+autotest juntos; T022 independiente.

## Implementation Strategy

**MVP**: Fases 1+2+3 (setup, fundación, overview real) → STOP y validar con captura.
Incremental: +US2 heatmap → +US3 fondo/caché. Commits en español por tarea o grupo.
