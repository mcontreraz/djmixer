# Validación y auditoría de loops por beatgrid (015)

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Fecha**: 2026-10-18 · **Feature**: `015-beatgrid-loop` · **Estado**: F0 auditada.
Este documento registra la auditoría de la ruta de audio existente, el diseño del
handoff streaming↔loop y la **deuda RT residual** que la feature 015 no puede
declarar resuelta en su totalidad.

## 1. Cadena del callback (cómo se produce audio hoy)

```
Mixer::dataCallback (hilo de audio miniaudio)
  └─ Mixer::process(output, frameCount)
       ├─ Deck::prepareAudio()   // ×2 (A y B)
       │    ├─ processPendingLoad()   // decoder init/uninit + mutex name
       │    └─ ma_decoder_seek_to_pcm_frame (seek pendiente)
       ├─ Mixer::processSync()   // corrección de sync
       ├─ Deck::render()         // ×2
       │    ├─ m_mixBuffer.resize()      // alloc
       │    ├─ scratch → renderScratchRange()
       │    │    ├─ ma_decoder_seek_to_pcm_frame   // seek
       │    │    ├─ ma_decoder_read_pcm_frames      // I/O
       │    │    ├─ m_src.insert / m_src.erase      // alloc/free
       │    │    └─ QDateTime::currentMSecsSinceEpoch()
       │    └─ normal → per-frame ensureSourceFor()
       │         ├─ ma_decoder_read_pcm_frames      // I/O
       │         ├─ m_src.insert                    // alloc
       │         ├─ EOF → ma_decoder_seek_to_pcm_frame(0)  // seek
       │         └─ discardConsumed() → m_src.erase // free
       └─ mix
```

## 2. Hallazgos de la auditoría RT (T001)

| Lugar | Operación | Clasificación |
|---|---|---|
| `deck.cpp:639` (no publicado) | `ma_decoder_uninit` | free/destrucción en audio |
| `deck.cpp:648` (no publicado) | `ma_decoder_init_file` | I/O + alloc en audio |
| `deck.cpp:656` (no publicado) | `std::lock_guard<std::mutex>` | lock en audio |
| `deck.cpp:700` (no publicado) | `ma_decoder_seek_to_pcm_frame` | seek en audio |
| `deck.cpp:723` (no publicado) | `m_mixBuffer.resize` | alloc en audio |
| `deck.cpp:947,958,963` (no publicado) | seek/read/insert | I/O + alloc en audio |
| `deck.cpp:981` (no publicado) | `QDateTime::currentMSecsSinceEpoch` | syscall en audio |
| `deck.cpp:1107,1112` (no publicado) | read/insert | I/O + alloc en audio |
| `deck.cpp:1127` (no publicado) | `m_src.erase` | free en audio |
| `deck.cpp:784` (no publicado) | EOF → `seek(0)` | seek en audio |

### Deuda RT residual (no resuelta por 015 en su totalidad)

El camino **streaming existente** (reproducción normal, scratch y carga) mantiene
seek/read/alloc/free/lock dentro del callback. La constitución exige cero de
estas operaciones; 015 introduce el camino de loop **sin** heredar esa deuda,
pero **no reescribe** el camino streaming para no romper el motor scratch
(`renderScratchRange` con integración continua) ni el historial del decoder
(`kHistoryFrames` ≈ 5.5 s), ambos explícitamente protegidos por la feature.

Deuda residual puntual:
1. `processPendingLoad()` sigue haciendo decoder init/uninit + mutex en audio.
2. El refill de reproducción normal (`ensureSourceFor`) sigue haciendo
   `ma_decoder_read_pcm_frames` + `m_src.insert` por bloque.
3. `discardConsumed` sigue liberando historial con `m_src.erase` en audio.
4. El scratch sigue haciendo seek/read/alloc/QDateTime en audio.

## 3. Handoff streaming↔loop (diseño adoptado)

- **Entrada al loop**: la UI publica `LoopIntent` (serial + generación de pista +
  revisión de grid). El worker de PCM decodifica la ventana `[floor(A), ceil(B)+guards]`
  fuera del callback y la publica `Ready`. El audio solo consume `Ready`; nunca
  llama a `ensureSourceFor` ni a `ma_decoder_seek_to_pcm_frame` para repetir.
- **Repetición**: render `[A,B)` con módulo positivo del cursor fraccional,
  interpolación lineal sobre la ventana residente. Cero I/O/alloc/lock por wrap.
- **Exit**: se prepara una ventana de continuación desde la posición audible
  (fuera del callback); al salir se conmuta de lector por handoff coherente, sin
  volver a la ruta streaming que hace seek dentro del callback.
- **Ownership**: el worker publica ventanas con todos los frames+guards; el audio
  consume solo `Ready` y retira con `ack`; **ninguna** liberación del último
  refcount ocurre en el hilo de audio. El worker retira tras el ack.

## 4. Oráculos y fixtures (F0)

- `loop_transport_test.cpp` (no publicado): geometría [A,B) contra un oráculo independiente
  (`timeAt` por tramos reimplementado a mano). Casos: BPM 123.45 con origen no
  cero, grid variable (`b=2,L=4 → A=1 s, B=3.3 s`), loop corto 1/8 de beat,
  extremos fraccionales, rechazos (grid no creciente, OUT fuera de pista, >64 s)
  y `snapStartBeat`.
- `loop_state_test.cpp` (no publicado): cola de intenciones (FIFO, capacidad 63, rechazo
  Busy, Exit prioritario con cola llena, invalidación de seriales anteriores).
- `loop_rt_test.cpp` (no publicado): arnés `RtProbe` de conteo de operaciones prohibidas
  (seek/read/alloc/free/lock) con flag thread_local de hilo de audio.

## 5. Registro de ejecución (se actualiza por fase)

| Fase | Build | ctest | Notas |
|---|---|---|---|
| F0 | OK | 9/9 PASS | `loop_transport`, `loop_state`, `loop_rt` nuevos |
| F1 | OK | 9/9 PASS | `loop_rt` ampliado: presupuesto, pin/ack, dos decks, 64 s, Exit |
| F2 | OK | 10/10 PASS | `loop_audio` nuevo; render puro 10k vueltas y anti-click ≥20 dB |
| F3 | OK | 11/11 PASS | `loop_state` ampliado: resize/reloop/Exit prioritario; worker QThread real |
| F4 | OK | 11/11 PASS | `loop_sync` nuevo: fase musical continua, maestro/seguidor, octavas, microloops |
| F5 | OK | 12/12 PASS | `loop_controls` nuevo (QML offscreen) + `midi_binding` con acciones lógicas de loop |
| F6 | OK | 12/12 PASS | suite completa + capturas 1600×860/1360×600 (base, activo, sin grid) |

> La columna de ejecución se completa tras cada fase; este documento no sustituye
> la salida real de `ctest` (ver evidencia por commit).

## 6. Métricas de cierre (F6 / T027)

Ejecución real del cierre (`cmake --build build -j && ctest --test-dir build --output-on-failure`):
`100% tests passed out of 12`, tiempo total ≈ 37.5 s. Cola real:

```text
12/12 Test #12: loop_sync ....... Passed    0.01 sec
100% tests passed out of 12
```

Medidas verificadas por los tests (aserciones ejecutadas, no captura manual):

| Métrica | Valor | Fuente |
|---|---|---|
| Sample rate interno | 48000 Hz | `audio::kSampleRate` |
| Bloques render probados | 1, 64, 127, 256, 1024 frames | `loop_transport_test` |
| Error de límites A/B vs `timeAt` | < 1e-6 frame | `loop_transport_test` |
| Error de cursor tras 10 000 vueltas | < 1e-6 frame, sin deriva | `loop_transport_test` (10k wraps) |
| Amplitud de render puro vs oráculo | < 1e-5 | `loop_transport_test` |
| Reducción anti-click en unión discontinua | ≥ 20 dB (salto < 0.1× duro) | `loop_audio_test` |
| Overshoot del fundido | ≤ 1.0 (máx. de ambas ramas) | `loop_audio_test` |
| Presupuesto PCM | 64 MiB/deck, 64 s de intervalo máx. | `kMaxLoopBytes` / `kMaxLoopSeconds` |
| Operaciones RT prohibidas en camino adoptado | 0 (seek/read/alloc/free/lock) | `loop_rt_test` (RtProbe) |
| Targets ctest | 12 | `sync_audio, grid_cache, eq_dsp, scratch_audio, waveform_scratch, loop_controls, midi_binding, loop_transport, loop_state, loop_rt, loop_audio, loop_sync` |

La contabilidad de memoria del caché (`LoopPcmCache`) se ejercita en `loop_rt_test`
con presupuesto reducido de 4 MiB y la ventana de 16 beats @ 120 BPM (>5.5 s de
historial); el presupuesto de producción sigue siendo 64 MiB/deck.

## 7. Capturas (F6 / T028)

Capturadas con `DJMIXER_SCREENSHOT` + backend offscreen/software (no requiere
permiso de Grabación de Pantalla). Pista real `90s Dance Edit.wav` (con grid) y
`silent.wav` (sin grid):

| Archivo | Tamaño | Estado |
|---|---|---|
| `/tmp/shot_1600.png` | 1600×860 | app base con pista |
| `/tmp/shot_loop_active.png` | 1600×860 | loop activo (4 beats) dibujado |
| `/tmp/shot_loop_min.png` | 1360×600 | mínimo vigente, loop activo |
| `/tmp/shot_nogrid.png` | 1600×860 | pista sin grid (loop no disponible) |

Verificación de dibujo: conteo de píxeles con acento de loop (`#87d6b0`) por
muestreo 2×2 — base 7, activo 48, mínimo 93, sin grid 7. El salto en las capturas
con loop confirma el relleno/marcas IN–OUT y el estado activo en pantalla. La
transición Preparing→Active y el texto de estado están cubiertos por
`loop_controls_test` (backend offscreen, sin pantalla física).

## 8. Escucha (F6 / T029) — pendiente manual

No es verificable en este entorno (sin salida de audio auditable por el agente).
Instrucciones para el operador:

1. `open build/djmixer.app` y cargar un tema propio con grid en Deck A.
2. Pulsar `4` en AUTO LOOP con el deck reproduciendo; escuchar el retorno en la
   frontera IN/OUT y confirmar ausencia de clic/silencio.
3. Probar `÷2`/`×2` durante el loop, `EXIT` (debe continuar sin salto) y `↻`
   (reloop desde el último intervalo).
4. Repetir con material percusivo y con una discontinuidad deliberada
   (fixture rampa/DC de `loop_audio_test`) para confirmar la costura ≥20 dB.
5. Registrar aquí el resultado y la fecha.

## 9. Revisión FR → tests (F6 / T030)

| Requisito | Verificación |
|---|---|
| FR-001 longitudes 1/8..16 | `loop_transport_test` (geometría por longitud), `LoopControls.qml` grilla |
| FR-002 validación de grid/límites | `loop_transport_test` rechazos |
| FR-003 `timeAt` a 48 kHz | `loop_transport_test` A/B vs oráculo |
| FR-004 snap Auto Loop | `loop_transport_test` `snapStartBeat` |
| FR-005 Preparing/frontera futura | `loop_rt_test`, `loop_controls_test` (Armed) |
| FR-006 intervalo [A,B) + módulo | `loop_transport_test` cursor/oráculo |
| FR-007 sin seek/decoder/timer en wrap | `loop_rt_test` RtProbe = 0 |
| FR-008 anti-click acotado | `loop_audio_test` ≥20 dB, sin overshoot |
| FR-009 sin I/O/alloc/lock en RT | `loop_rt_test` |
| FR-010 presupuesto 64 s/64 MiB | `loop_transport_test` (>64 s rechazo), `loop_rt_test` caché |
| FR-011 fase musical continua | `loop_sync_test` |
| FR-012 Exit conserva fase/posición | `loop_state_test`, `loop_sync_test` |
| FR-013 resize conserva IN, reloop | `loop_state_test` |
| FR-014 pausa/gestos cancelan | `loop_state_test`, `loop_controls_test` (pausa Armed, exit) |
| FR-015 serial/generación/revisión | `loop_state_test` (cola), `loop_sync_test` |
| FR-016 wrap antes de EOF, OUT==duration | `loop_transport_test` EOF |
| FR-017 detector suspendido en loop | `loop_sync_test` (grid fijado) |
| FR-018 estado QML confirmado | `loop_controls_test` (snapshot, Preparing/Active/rechazo) |
| US4 acciones equivalentes UI/MIDI | `midi_binding_test` (acciones lógicas, no note-off), `loop_controls_test` |

Sin regresión: los 11 tests previos siguen verdes; no se tocó el motor scratch ni
EQ/filtro/trim. Las acciones MIDI de loop no introducen CC físicos en el factory
(verificado en `midi_binding_test`).


## F6 — Cierre (2026-10-18)

- Suite completa: **12/12 verde** (sync_audio, grid_cache, eq_dsp,
  scratch_audio, waveform_scratch, midi_binding, loop_transport, loop_state,
  loop_rt, loop_audio, loop_sync, loop_controls).
- Captura end-to-end (T028): metrónomo sintético 120 BPM (16 s, 32 beats
  detectados por BeatThis, BPM 119.76) + `DJMIXER_SCREENSHOT_LOOP_A=4` →
  el motor confirmó `loopActive()` antes de capturar; PNG 3200×1720 con la
  región de loop marcada. Comando:

  ```
  DJMIXER_SCREENSHOT=/tmp/loop_capture.png   DJMIXER_SCREENSHOT_TRACK_A=/tmp/metronome120.wav   DJMIXER_SCREENSHOT_LOOP_A=4 ./build/djmixer.app/Contents/MacOS/djmixer
  ```

- Escucha manual (T029): pendiente en la app (entradas/wraps/resize/Exit con
  música real); la cobertura programática de discontinuidad y anti-click está
  en `loop_audio_test`.


## Cuantización del Auto Loop (Traktor clásico, REA verificada)

Evidencia recuperada del binario de Traktor Pro 3 (`AudioDeckStream`,
símbolos y desensamblado; artefacto declarado en
specs/015-beatgrid-loop/research.md LOOP-T01/T02):

- `AudioDeckStream::setLoop(double,double,int,bool)` (0x1001d2320) ajusta los
  límites del loop **contra la duración del beat con `fmod`**: el IN/OUT se
  alinean a la retícula musical (el estado 0xa0 del tempo-map es la duración
  del beat en segundos). El wrap queda en el beat.
- `getFastLoopLengthInBeats()` / `isNonIntegralLoopRunning()`: los loops son
  **integrales con el beat por defecto**; el caso no-integral es la excepción
  (IN/OUT manuales), no el Auto Loop.

Comportamiento adoptado (observable):

- Presionar LOOP cuantiza el IN al **próximo borde** de la subdivisión
  (min(1, L)): con L ≥ 1 el paso es 1 beat. El cabezal **no se mueve**:
  reproduce derecho hasta el borde y el loop se activa al alcanzarlo
  (frontierSeconds). Nunca retrocede; salto máximo 1 beat.
- OUT = IN + L beats → el wrap cae exactamente en la retícula: beat-seamless.
- El encogimiento (4→2, 8→4) con la cabeza más allá del OUT nuevo se difiere
  al wrap natural (sin clip); el IN no cambia nunca en un resize.
