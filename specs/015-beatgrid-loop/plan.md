# Implementation Plan: Loops exactos por beatgrid

**Feature**: `015-beatgrid-loop` · **Fecha**: 2026-10-18 · [Spec](spec.md)
**Estado**: Plan preparado; ninguna fase de implementación ejecutada.

## Contexto técnico y constitución

C++17, Qt 6, miniaudio, PCM interno float estéreo a 48 kHz. Plataforma principal:
macOS arm64. Sin dependencias nuevas ni código/recursos propietarios copiados.
La evidencia previa se usa para contratos, no como implementación.

- **RT**: datos/órdenes preparados fuera del callback; ownership explícito y
  retirada de buffers fuera de audio. La deuda de decoder/refill actual es un
  prerrequisito del camino de loop, no una excepción silenciosa.
- **Verificación**: tests de transporte/DSP antes de habilitar botones; captura
  QML y escucha con fixtures al implementar. Esta entrega es documentación.
- **Simplicidad**: una región por deck, último intervalo de sesión, sin base de
  datos ni Roll/Slip. Usar el mailbox existente como patrón, no una arquitectura
  genérica de efectos.
- **Claridad**: código futuro en inglés; documentos en español; unidades explícitas.

## 1. Matemática musical y de transporte

Sea `Fs=48000`, revisión de grid fija `G`, inicio musical `b`, longitud `L` beats:

```text
A = Fs * G.timeAt(b)
B = Fs * G.timeAt(b + L)
D = B - A                          # frames fuente, double; D > 0
q = min(1, L)                      # paso Auto Loop, en beats
b = floor(G.beatAt(p/Fs) / q) * q  # caché lista; posición del hilo de audio
```

Validar `0<=A<B<=duration*Fs`. No corregir un OUT fuera de pista truncándolo,
porque cambiaría la longitud musical. Si el snap anterior cae antes de cero,
programar la primera frontera válida futura; no inventar un beat en cero.

El renderer conserva fase fraccional. Por cada muestra, lee en `p∈[A,B)` y
avanza con la tasa vigente `r`; normaliza antes de la siguiente lectura:

```text
u = p + r
k = floor((u - A) / D)
p_next = A + ((u - A) - k*D)
wrap_count += k
```

El caso normal v1 tiene `r>0`; aun así `positiveModulo` y las validaciones deben
ser correctos en números negativos. Acotar errores de redondeo en el extremo
sin convertir `B` en una muestra emitida. Partir callbacks en spans contiguos
para eventos/detector y permitir múltiples wraps. Los tamaños de bloque no
cambian el resultado para el mismo stream de tasas/órdenes por frame.

**Interpolación, oráculo v1**: primero envolver la coordenada double y luego
reconstruir la señal PCM original por interpolación lineal:

```text
u = A + positiveModulo(p - A, D)
i = floor(u); f = u - i
F(u) = (1-f)*PCM[i] + f*PCM[min(i+1, N-1)]
y = F(u)                          # antes de anti-click / EQ
```

N es el total de frames PCM internos. La extensión en el EOF físico mantiene
la última muestra para el tap derecho; solo se usa como guard de interpolación.
No envolver los taps enteros de forma independiente: sería otro interpolador.
Si A/B son fraccionales, sus vecinos de reconstrucción pueden caer fuera de la
región musical; se preparan como guards intencionales del mismo archivo. No
hacer un tile de `round(D)` muestras. F puede ser discontinua al envolver; ese
salto se trata en la etapa anti-click, sin alterar la coordenada ni la cadencia.
El oráculo independiente debe incluir los casos inmediatamente antes/después
de B, A no entero y OUT coincidente con EOF.

## 2. PCM, preparación y ownership

Introducir un worker de lectura PCM por deck y una interfaz de lectura residente
para el renderer. El decoder del worker es exclusivo: no compartir un decoder
mutable con el callback. El trabajo de decode/seek/reserve/resize/destrucción
queda en ese worker. No reutilizar `ensureSourceFor()` en cada vuelta.

Propuesta de archivos: `src/looptransport.h/.cpp` para matemáticas/estado;
`src/looppcmcache.h/.cpp` para ventanas y publicación. La implementación puede
integrarlos con el buffer existente, manteniendo los contratos y pruebas.

- Presupuesto **64 MiB PCM por deck**, con un pool de ventanas fijables y una
  ventana de preparación/retirada. Máximo intervalo de loop **64 s** de fuente.
  Contabilizar márgenes, cabezas anti-click, doble buffer y estado retirado.
- Una ventana activa no se puede expulsar ni sobrescribir. Un candidato no se
  publica hasta contener todos los frames y guards necesarios. Si no cabe,
  rechazar; mantener el loop previo.
- Prelectura alrededor del cabezal para Auto Loop; si hay miss, `Preparing`.
  El worker devuelve rango realmente residente y generación. El audio decide
  una frontera futura cubierta por ese rango, no usa un timestamp UI atrasado.
- Si no hay una región completa futura cubierta, solicitar otra preparación;
  reproducción normal continúa. Nunca anunciar Active mientras falta PCM.
- Retener continuación desde la posición audible para Exit y prefetch desde OUT.
  Al salir se cambia de lector por handoff coherente; no se vuelve a la ruta
  que hace `ma_decoder_seek_to_pcm_frame` dentro del callback.
- Liberar o reciclar ventanas tras acuse de retiro del consumidor. No usar
  destrucción del último `shared_ptr` desde audio ni spin-wait.
- La ruta streaming preparada que permite entrar/salir debe continuar funcionando
  después de Exit. La prueba RT incluye varios callbacks posteriores; no basta
  esconder el seek un bloque más tarde.

## 3. Comandos y scheduling

Un único productor serializa QML/teclado/MIDI en el hilo UI. Cola SPSC fija para
intenciones con `serial`, generación de pista y revisión solicitada. Capacidad
inicial 64, límite de consumo por callback; sin “latest wins” para toggles.
Exit/Cancel tiene una señal/serial prioritario independiente para funcionar aun
con cola llena; las órdenes anteriores a ese serial quedan canceladas.

Resultados de worker viajan por mailbox de ownership separado. Solo audio
confirma Active y publica snapshot. Cache preparada no equivale a orden aplicada.

- **Listo**: captura usando posición de ejecución al comienzo del callback,
  sin seek y con región anterior que contiene el cabezal.
- **Miss**: prepara, arma la siguiente subdivisión futura cubierta y ejecuta
  en su offset exacto dentro del bloque. Se integra la tasa vigente para
  detectar el cruce; un cambio de pitch no deja un contador obsoleto.
- **Tarde**: no disparar con posición pasada; rearme/repreparación explícitos.
- **Pausa**: preparar y activar región sin cambiar `playing`.
- **Resize**: mantener A; prevalidar/cachear B nuevo. Al aplicar, si p queda
  fuera, remapear por módulo y ajustar el offset musical para no perturbar sync.

## 4. Continuidad sonora sin alterar duración

La fase de prueba compara primero un wrap duro contra el oráculo del transporte.
Después incorpora anti-click independiente; nunca “arreglar” un click moviendo
IN/OUT al cruce por cero o solapando W frames que acorten la vuelta.

Diseño inicial: dos lectores temporales tras la frontera: continuación de cola
`B+delta` y cabeza `A+delta`, ambos avanzan con la misma tasa. `delta`
inicial incluye el overshoot fraccional del cruce; no reiniciar ambos lectores
en A/B enteros ni descartar la fracción al iniciar el fundido. Fundido de suma
unitaria con ventana raised-cosine durante **1 ms de salida**, acotada a ≤1/16
del período más corto vigente. La duración del loop sigue siendo D. Si los
extremos ya son continuos, evitar modificar innecesariamente el transitorio.

Medir el máximo salto en toda la ventana, incluida entrada y salida, para no
aceptar que el click simplemente se desplace. La ventana de 1 ms es un diseño
inicial sometido a esos gates, no una garantía universal para cualquier audio.

La cola requiere guard preparado más allá de B. En EOF se usa una extensión
acotada/continua preparada fuera del callback; no leer fuera de rango ni insertar
silencio como parche. Las fixtures deciden si esta extensión satisface SC-003.
Una alternativa de corrección de discontinuidad solo puede sustituir el fundido
si cumple los mismos oráculos de duración, pico y transitorio; documentar el
resultado medido. No se atribuye esta ventana a Serato/Traktor.

El fundido no restablece filtros, EQ ni resampler. Tampoco garantiza equivalencia
bit a bit con el original junto a una unión deliberadamente discontinua.

## 5. Sync: dos coordenadas

```text
localBeat = G.beatAt(p / Fs)        # posición audible del track
continuousBeat = localBeat + beatOffset
beatOffset += k * L                # cada wrap normal
```

Calcular fase de sync a partir de `continuousBeat` y el downbeat fijado. El BPM
local y la lectura de waveform siguen usando p y su grid fijado. No sustituir
la posición de audio con `timeAt(continuousBeat)`: después de muchas vueltas
caería en otra región de tempo del archivo.

Resize/reloop con salto intencional ajusta `beatOffset` por `oldLocal-newLocal`,
salvo un snap solicitado explícitamente por el usuario. Exit conserva offset y
engage; los seeks/cues/scratch explícitos siguen su política de nuevo transporte.
No dejar que `processSync()` llame `seekAudio()` solo porque ocurrió un wrap.

Publicar un snapshot coherente con ambas posiciones antes/después del mismo
bloque. Extender `syncalign::phaseError` para recibir coordenadas musicales,
conservando conversión de octavas. Grid de sync y grid de loop deben ser la
misma revisión fijada mientras el loop esté activo; un análisis nuevo se
publica pendiente, sin sustituir solamente la mitad de esa pareja.

En mapas variables, la fase integra los intervalos que realmente se recorren;
no se usa un avance constante basado en BPM global. El cambio de tempo al
retornar a A es real, distinto de un salto de fase ficticio. Validar que el
controlador reaccione a tempo real sin deshacer la intención de loop.

El detector en vivo se suspende durante Active en v1 y se reinicia al salir;
no sustituye el grid del loop por transientes repetidos con timestamps falsos.

## 6. UI, comandos e integración

- `Deck` publica API del [contrato](contracts/loop.md); sin escrituras desde QML
  que suplanten el estado confirmado de audio.
- Activar la grilla de botones actual; incorporar ÷2/×2, Exit/Reloop compactos,
  estado de preparación y tooltips. Mantener el fondo/faders ya aprobados.
- Dibujar IN/OUT y relleno de región en overview y waveform; p local sigue
  moviéndose dentro del intervalo. Las etiquetas de tiempo nunca usan beatOffset.
- MIDI usa las mismas acciones tipadas; añadir únicamente mappings de hardware
  que estén documentados. Probar eventos sintéticos y releases sin doble toggle.
- Capturas a 1600×860 y al mínimo vigente del proyecto, incluidos Preparing,
  Active y sin grid. No ampliar otras secciones de la app en esta feature.

## Fases y gates

1. Oráculos de beatgrid, cursor y discontinuidad; decisiones RT auditadas.
2. Worker/caché/ownership/handoff y rechazo de comandos obsoletos.
3. Motor loop/resize/exit/reloop + exactitud fraccional y EOF.
4. Anti-click + sync musical continuo y grids por revisión.
5. QML/MIDI y regresión completa + capturas/escucha.

Cada fase depende de los tests anteriores. Un gate fallido no se resuelve
bajando la tolerancia o deshabilitando sync. No se implementa Roll/Slip por
analogía con el contador continuo: ese contador no es un playhead Slip.
