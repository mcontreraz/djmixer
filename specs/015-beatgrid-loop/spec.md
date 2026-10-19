# Feature Specification: Loops seamless exactos por beatgrid

**Feature**: `015-beatgrid-loop` · **Creada**: 2026-10-18
**Estado**: Especificada; implementación pendiente
**Base revisada**: `20cf1c9` · **Rama de implementación propuesta**: `015-beatgrid-loop`
**Solicitud**: «deja un sdd feature loop revisa como lo hace traktor y serato en rea porque tienen el seamless loop exacto por beatgrid».

## Objetivo y alcance

Activar loops musicales en ambos decks, con los botones existentes de **1/8,
1/4, 1/2, 1, 2, 4, 8 y 16 beats**. Un beat significa una negra, no un compás.
El beatgrid determina los límites; el transporte de audio ejecuta el retorno
sin perder fracciones de muestra, insertar silencios ni acumular deriva.

“Exacto” significa exacto respecto del grid disponible; no corrige un grid mal
analizado. “Seamless” exige dos verificaciones distintas: continuidad temporal
sin huecos y tratamiento audible de una discontinuidad entre extremos. Un beat
correcto no garantiza que las amplitudes de inicio y final coincidan.

Se revisaron los REA ya guardados de Traktor Pro 3 y Serato DJ Pro 4.0.10.213.
[Research](research.md) separa observaciones, inferencias y decisiones propias.
No se afirma haber recuperado ni medido el algoritmo propietario de empalme.

V1 incluye Auto Loop, cambio de longitud, ×2/÷2, Exit y Reloop del último loop
de la sesión. No incluye loops manuales IN/OUT, slots persistentes, importación
de loops Serato/Traktor, Roll/Slip, reverse-loop, time-stretch ni un detector nuevo.
Scratch y saltos explícitos tendrán una política de salida definida, no un modo
implícito de scratch dentro del loop.

## User Scenarios & Testing

### US1 — Capturar un loop exacto (P1)

Con pista y grid válidos, pulso una longitud y esa región se repite sin deriva.
Si el PCM necesario aún no está listo veo `Preparing`; la pista continúa y el
botón solo se ilumina como activo tras confirmación del motor.

**Aceptación**:
1. A 120 BPM, 4 beats delimitan 2 s de fuente; a 123.45 BPM se conservan extremos
   fraccionales, sin redondear la duración a frames enteros.
2. Si la región cruza un cambio de tempo, OUT es `timeAt(startBeat + length)`;
   no se calcula con el BPM nominal de la biblioteca.
3. Los wraps ocurren dentro de cada callback, también si hay varios en un bloque.
4. Sin grid válido o con límites fuera del audio, no se activa un loop aproximado.

**Prueba independiente**: referencia matemática con 10 000 vueltas, todos los
bloques de prueba y pitch fraccional; comparar cursor, eventos y salida PCM.

### US2 — Cambiar tamaño, salir y volver (P1)

Otra longitud conserva IN y cambia OUT. Pulsar la longitud activa o Exit desactiva
el loop y continúa desde la posición audible. Reloop recupera el último intervalo.

**Aceptación**:
1. Reducir el loop cuando el cabezal queda fuera lo remapea mediante módulo,
   sin descartar el exceso ni esperar a un timer QML.
2. Ampliarlo espera PCM listo, manteniendo entretanto el loop anterior.
3. Exit nunca salta a una posición Slip/continuación imaginaria; conserva límites.
4. Reloop estando pausado activa los límites sin iniciar reproducción. Si el
   cabezal está fuera, se posiciona en IN mediante la ruta preparada del motor.
5. Una carga nueva cancela preparaciones, estado activo y último intervalo.

**Prueba independiente**: secuencia 8→1/8→16→Exit→Reloop, incluyendo órdenes rápidas.

### US3 — Mantener sync sin que pelee con el loop (P1)

Loops de cualquier longitud funcionan con el deck como maestro o seguidor.
El retorno intencional no dispara una corrección, reenganche o seek de sync.

**Aceptación**: probar 1/8, 1/4, 1/2, 1, 2 y 4 beats con sincronización de beat y
compás, pitch bend y relación de octava. Waveform/tiempos muestran el cabezal
local; sync usa una fase musical continua. Al salir no hay snap automático.

### US4 — Estado visible y acciones equivalentes (P2)

Botones, atajos y acciones MIDI usan el mismo contrato. Se ve la región IN–OUT,
longitud, estado de preparación y motivo de indisponibilidad.

**Aceptación**: note-off no vuelve a alternar el loop; `Output`/NOTIFY no reenvía
órdenes; una respuesta tardía de otro archivo nunca ilumina el deck actual.
Los mensajes MIDI se pueden probar sintéticamente sin inventar CC de hardware.

## Functional Requirements

- **FR-001**: Longitudes musicales explícitas de 1/8 a 16 beats; default 4.
- **FR-002**: Validar grid estrictamente creciente, valores finitos, revisión,
  generación de pista, límites `[0,duration]` y longitud positiva.
- **FR-003**: Derivar ambos extremos mediante `BeatGrid::timeAt`, a 48 kHz del
  dominio PCM interno, con precisión fraccional. Nunca usar el sample rate del
  archivo original para indexar ese PCM.
- **FR-004**: Auto Loop queda siempre anclado al grid en v1. Con PCM listo y
  reproduciendo: IN es la subdivisión anterior a la posición de ejecución,
  paso `q=min(1,lengthBeats)`, relativo al primer beat del grid. No hay salto al
  activarlo porque el cabezal ya pertenece a `[IN,OUT)`.
- **FR-005**: Sin PCM listo: `Preparing`, reproducción normal; tras prepararlo se
  arma una frontera futura dentro del rango residente. Si se pierde, se rearma
  la siguiente frontera cubierta o se sigue preparando; nunca se ejecuta tarde
  con límites antiguos. Pausado: activar/posicionar sin cambiar Play.
- **FR-006**: Intervalo semiabierto `[IN,OUT)`; módulo positivo del cursor
  fraccional conserva overshoot y permite múltiples vueltas por bloque.
- **FR-007**: Preservar cadencia y estado de remuestreo/DSP en el wrap; no llamar
  a `seek`, al decoder ni a un timer UI para repetir.
- **FR-008**: Empalme anti-click acotado que no mueve IN/OUT, no acorta el período,
  no agrega frames y no reinicia EQ/filtro. Validarlo separado del reloj.
- **FR-009**: PCM residente antes de activación, con márgenes de interpolación,
  empalme y salida. Sin I/O, mutex, asignaciones o liberaciones en la ruta de
  activación, repetición, cambio de tamaño y salida del loop.
- **FR-010**: Presupuesto v1: máximo 64 s de fuente por intervalo y 64 MiB de PCM
  por deck, incluidos buffers de preparación/retirada. Excederlo produce un
  rechazo explícito, sin truncar la longitud musical ni expulsar el loop activo.
- **FR-011**: Separar posición audible envuelta de fase musical continua para
  sync. Un wrap no cambia el serial de engage ni activa un seek correctivo.
- **FR-012**: Exit conserva fase continua y sale desde posición audible. Cambios
  explícitos de posición invalidan/rebasan ese offset según el contrato.
- **FR-013**: Resize conserva IN y publica intervalo+cache coherentes; un error
  de preparación no destruye el loop previo. Reloop conserva último intervalo
  válido durante la sesión de la pista.
- **FR-014**: Pausa conserva estado y posición del loop. Scratch, needle, hot cue,
  cue temporal y seek explícitos desactivan/cancelan el loop antes de ejecutar
  el gesto; retienen último intervalo, salvo cambio de pista/revisión inválida.
- **FR-015**: Cada orden y respuesta lleva serial y generación de pista. Se fija
  la revisión del grid durante el loop; un análisis tardío no mueve sus límites.
  Adoptar otra revisión requiere transición explícita tras salir o reactivar.
- **FR-016**: Procesar wrap antes de EOF; `OUT==duration` es válido. Interpolación
  y empalme no leen fuera del PCM. Preparar continuación normal antes de Exit.
- **FR-017**: El detector de beats no recibe un bloque como continuo cuando cruza
  un wrap: segmentar su alimentación o suspenderla durante loop y reiniciarla al
  salir. El grid fijado sigue siendo la autoridad musical.
- **FR-018**: Estado QML confirmado desde audio; `Preparing`, `Armed`, `Active`,
  `Off`, longitud vigente y rechazo distinguibles. Un resize pendiente mantiene
  visible el intervalo activo anterior.

## Success Criteria

- **SC-001**: En 10 000 vueltas, desviación del instante de wrap <1 frame de
  salida respecto del oráculo fraccional, sin tendencia acumulativa. Límites
  calculados con error <1e-6 frame respecto de `timeAt` usando la misma revisión.
- **SC-002**: Mismo stream de comandos/tasas por frame produce los mismos wraps
  para bloques de 1, 64, 127, 256 y 1024 frames. El render puro sin anti-click
  coincide con un lector periódico de referencia dentro de 1e-5 de amplitud.
- **SC-003**: Fixture periódico sin discontinuidad: ningún hueco ni duplicación.
  Fixture discontinuo: empalme reduce ≥20 dB el máximo salto en toda la ventana de unión (entrada/salida incluidas) frente al wrap
  duro, sin overshoot sobre el máximo de las dos ramas y sin modificar SC-001.
  Se mide también material percusivo para evitar aceptar un click oculto por mute.
- **SC-004**: Cero operaciones RT prohibidas en el intervalo instrumentado de
  activación/loop/resize/Exit; memoria PCM dentro del presupuesto en dos decks.
- **SC-005**: Con grid constante y lock previo, ningún seek/re-engage causado por
  1000 wraps; discontinuidad artificial de fase <1e-6 beat. En grid variable,
  continuidad de fase conservada y sin corregir un salto de índice como error.
- **SC-006**: Nueva pista, grid revisado y 100 órdenes rápidas no publican estado
  de generaciones obsoletas; cola llena rechaza explícitamente sin perder Exit.
- **SC-007**: Pruebas de motor, UI/MIDI y regresión existentes verdes; capturas
  de tamaños normal y mínimo sin solapes y loop dibujado sobre ambas waveforms.

## Entidades y decisiones

`LoopCommand`, `PreparedLoopWindow`, `ActiveLoop`, `LoopSnapshot`, fase musical
continua. [Modelo](data-model.md), [contrato](contracts/loop.md), [plan](plan.md),
[tareas](tasks.md) y [validación](quickstart.md).

Decisiones propias: tamaños en beats, snap hacia atrás con caché lista, frontera
futura al preparar, Exit inmediato, scratch cancela, límites congelados por revisión.
No se atribuyen estas políticas exactas a Traktor ni Serato sin evidencia adicional.
