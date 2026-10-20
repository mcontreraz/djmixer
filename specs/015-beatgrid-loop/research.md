# Research: revisión de REA existente para loops

> **Material de referencia local, no publicado.** Las rutas
> `referencia-*/` (no publicado) y los nombres de fichero sueltos de ese material que se
> citan aquí viven **solo en la máquina de desarrollo**: no están en el repo
> público. Lo que se publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

**Fecha**: 2026-10-18 · **Base local**: `20cf1c9`.
Se reutilizaron informes, inventarios e índices ya generados. No se reabrieron
los binarios, no se corrieron decompilaciones ni se observaron nuevas ejecuciones.

## Evidencia y alcance

Los IDs `LOOP-*` del [manifest](evidence.json) identifican esta revisión local;
no se presentan como nuevos Evidence IDs de REA. Se conservan hashes, rutas y
líneas para volver a las fuentes. El único Evidence ID REA citado directamente
identifica el artefacto Traktor, no su algoritmo de loop.

| ID | Observación verificable | Conclusión permitida y límite |
|---|---|---|
| LOOP-T01 | REA `ev_5d2115f8863b5b2a6a5f98286a2405f219450878e9a33dcf42e4756950c9a9be`, bundle Traktor Pro 3, SHA en manifest | Identidad del target del análisis previo; inspección estática |
| LOOP-T02 | Inventario guardado `nm -C`: `AudioDeckStream::setLoop(double,double,int,bool)` en `0x1001d2320`; posición en samples double; `getFastLoopLengthInBeats`, `isNonIntegralLoopRunning`; fetch de caché | Existen interfaces separadas de loop, posición, longitudes musicales y lectura de caché. Nombres/tipos no prueban fórmula, unidades de cada argumento ni flujo de llamadas |
| LOOP-T03 | Strings `loop.set.in/out/auto/auto_with_size`, `loop.active`, `loop.is_in_active_loop`; referencias a caches de hotcue | Superficie de control y estados distintos. No prueban qué caché usa el loop |
| LOOP-S01 | Índice QML recuperado: `SeratoAutoloop.qml` líneas 107/114 Output/Click `auto_loop_specific_length`, 121 Alt-click `auto_loop_roll_specific_length`; `SeratoSavedLoopsSlot.qml` 151/158/187 reloop/exit/slot_loop | Auto Loop, Roll y saved loops tienen contratos diferenciados; feedback no es un comando. No establece el código C++ del loop |
| LOOP-S02 | Informe anterior separa DOC/BIN/DISEÑO para Quantize y loops | Hay un contrato funcional de captura/redimensionado/reloop. El módulo fraccional propuesto en ese informe es diseño propio, **no** pseudocódigo recuperado de Serato |
| LOOP-S03 | TempoMap, conversiones beats/ticks/seconds, marcadores y serializer BeatGrid v1 | Se requiere mapa musical, no solo BPM nominal. No identifica el algoritmo de transición sonora |
| LOOP-S04 | Análisis nativo de SyncLogic y fases beat/compás | Usar la unidad musical correcta; no convertir Quantize ni el umbral de estado 1/64 en fórmula de loop |

Fuentes (los informes REA son **referencia local, no publicada**; el símbolo
seleccionado sí está en el repo):

- Identidad Traktor (grafo de dylibs, local no publicado:
  `referencia-traktor/traktor-inspect.json` (no publicado)),
  [símbolos seleccionados del análisis previo](traktor-loop-symbols.tsv) y
  volcado de cadenas (local no publicado:
  `referencia-traktor/traktor-strings.txt` (no publicado)).
- Índice QML de Serato (local no publicado:
  `referencia-serato/replica/contratos/qml-api.json` (no publicado)) e interpretación de
  eventos (local no publicado:
  `referencia-serato/replica/contratos/interfaz-y-eventos.md` (no publicado)).
- Contrato de transporte (local no publicado:
  `referencia-serato/replica/contratos/transporte-y-audio.md` (no publicado)), grid y
  TempoMap (local no publicado:
  `referencia-serato/replica/beatgrid-datos/README.md` (no publicado)), serializer
  (local no publicado:
  `referencia-serato/replica/beatgrid-datos/serializer-v1.md` (no publicado)) y sync
  nativo (local no publicado:
  `referencia-serato/replica/beatsync-native/README.md` (no publicado)).

El informe de transporte cita los manuales públicos de Auto Loop y Quantize,
consultados en la investigación anterior. Aquí se revisó ese informe guardado;
no se afirma una nueva comprobación de los sitios ni del comportamiento en runtime.
Los árboles QML temporales ya no contienen los archivos recuperados: se usa el
índice persistido con SHA y líneas, y se registra esa limitación.

## Comparación útil

| Pregunta | Traktor guardado | Serato guardado | Decisión de esta app |
|---|---|---|---|
| Longitud musical | Método explícito `getFastLoopLengthInBeats()` | Auto Loop y aliases/slots; unidad completa beats/bars no resuelta por el índice | Beats explícitos en API y UI |
| Límites y posición | `setLoop` y posiciones sample double | Grid/TempoMap y controles; núcleo de loop no recuperado | Límites fraccionales derivados de `timeAt` |
| Estado activo vs región | `isLoopActive` / `isInActiveLoop` | Slots, selección, reloop y feedback diferenciados | Último intervalo separado de Active |
| Quantize | `computeQuantizedBeatPhase`, consulta de Quantize | Comando en cola y contrato de cues/loops | Separar elegir límite de programar ejecución |
| Audio residente | Interfaces CachedAudioStream y LoopFetcher | No demostrado para el loop por la evidencia revisada | PCM preparado y fijado por ownership |
| Empalme exacto | No recuperado | No recuperado | Diseño propio y pruebas de reloj + anti-click |

**Inferencia**, no hallazgo binario: el diseño necesita conservar fracción y
posición musical para repetir a pitch arbitrario sin deriva. Que un producto
tenga un `double` o un `LoopFetcher` no demuestra que use nuestro módulo, caché,
ventana anti-click ni política de sincronización.

## Brechas del proyecto actual

| Fuente en `20cf1c9` | Hallazgo | Consecuencia |
|---|---|---|
| `beatgrid.h:45,81` (no publicado) | `beatAt`/`timeAt` soportan intervalos variables | Derivar IN y OUT por la inversa, congelar revisión |
| `deck.cpp:782` (no publicado) | Cursor double e interpolación por muestra | Integrar wrap aquí, antes de EOF |
| `deck.cpp:562,695,701` (no publicado) | Seek trunca a entero, reposiciona decoder y limpia caché | Prohibido usar seek para cada vuelta |
| `deck.cpp:1140,1157` (no publicado), `deck.h:264` (no publicado) | Refill con I/O/insert y descarte de historial ~5.5 s | 16 beats a 120 BPM = 8 s: pin de PCM obligatorio |
| `deck.cpp:821` (no publicado) | Detector recibe bloque como tiempo continuo | Segmentar o suspender durante loop |
| `mixer.cpp:305` (no publicado), `syncalign.h:20` (no publicado) | Fase derivada de posición audible | Loops fraccionales, y 1/2 beats en fase de compás, crean error artificial |
| `audiosync.h:19` (no publicado) | Mailbox SPSC con ownership | Patrón útil; no usarlo como cola de toggles que se puedan perder |
| `DeckPanel.qml:258` (no publicado), `midicontroller.cpp:368` (no publicado) | UI deshabilitada, acciones MIDI reservadas | Motor y contratos primero; activar UI después |

La constitución exige cero I/O/alloc/locks en audio. El motor actual aún tiene
esa deuda; esta feature no puede declarar que todo el callback ya es seguro.
Su camino de loop, incluidos preparar su entrada y continuar tras Exit, necesita
caché y handoff explícitos. La auditoría de RT debe enumerar la deuda residual.

## Decisiones de diseño

1. **Exactitud temporal**: `[A,B)`, módulo positivo y fracción preservada.
2. **Grid variable**: `A=Fs*timeAt(b)`, `B=Fs*timeAt(b+L)`, nunca BPM global.
3. **Dos coordenadas**: readhead envuelto para audio/UI y beat continuo para sync.
4. **Preparación explícita**: reservar/decodificar fuera de audio; activar solo
   cuando todos los datos de loop, interpolación y continuación están listos.
5. **Empalme**: prototipo de fundido corto entre continuación de cola y cabeza,
   con ambos lectores avanzando, sin acortar el período. Se valida antes de UI.
6. **Alcance controlado**: Auto Loop/Reloop/Resize; Roll/Slip y persistencia después.

## Registro de preguntas

| Pregunta | Estado tras esta revisión | Trabajo restante |
|---|---|---|
| ¿Qué controles expone cada app? | Respondida parcialmente con símbolos/QML | Semántica runtime exacta y slots no cubiertos |
| ¿Grid variable y unidades? | Modelo temporal establecido; unidades de Auto Loop parcialmente resueltas | No heredar bars/beats ambiguos; API propia explícita |
| ¿Cómo hacen el wrap y evitan clicks? | No resuelta por el material guardado | Decompilación dirigida/medición futura si se exige paridad exacta |
| ¿Cómo conviven microloops y sync? | Sync recuperado, interacción con loop no demostrada | Ensayos comparativos futuros; contrato propio definido |
| ¿Cómo implementarlo aquí? | Diseño listo para implementación | Tareas y pruebas pendientes, no se modificó el motor |

No se bloquea una implementación original por desconocer el DSP propietario;
sí se impide etiquetarla como réplica exacta de Traktor o Serato.
