# Validación prevista de loops

Este documento describe **pruebas a implementar**. No hay todavía motor de loop,
fixtures nuevos, binarios `loop_*_test` ni resultados de audio para esta feature.

## Oráculos independientes

1. **Geometría musical**: `A=48000*timeAt(b)`, `B=48000*timeAt(b+L)`.
   Grid constante 123.45 BPM con origen no cero; grid variable explícita
   `beats={0,0.5,1.0,1.5,2.1,2.7,3.3,...}`: b=2, L=4 produce A=1 s, B=3.3 s.
   Usar 4×60/120 daría 3 s de OUT y debe fallar.
2. **Cursor**: referencia de alta precisión con suma de tasas por muestra y
   módulo sobre límites fraccionales. Nunca usar el mismo helper del motor
   para generar el esperado. Contar vueltas y preservar el sobrante.
3. **PCM**: implementar independientemente `F(A+positiveModulo(p-A,B-A))`,
   con F lineal y guard EOF de última muestra según el plan. No envolver taps
   enteros por separado. Primero anti-click desactivado.
   Después medir ventana anti-click como modificación de señal separada.
4. **Sync**: fase continua esperada por integración de beats recorridos;
   comprobar que la posición visible vuelve mientras la fase no retrocede.

## Matriz mínima

| Caso | Variantes | Aserción |
|---|---|---|
| Longitudes | 1/8…16 beats | IN/OUT exactos y misma política de unidades |
| Tasas | 0.4, 0.923, 1, 1.137, 1.6; pitch bend por frame | Wraps sin pérdida fraccional |
| Callbacks | 1,64,127,256,1024; alternados | Invarianza para comandos y tasas en mismos frames |
| Duración | 10 000 vueltas; varios wraps por callback | <1 frame de error de evento, sin deriva acumulativa |
| Grid | importada, detectada, variable, origen no cero, sin grid | Inversa musical, validación y rechazo explícito |
| Extremos | A/B fraccionales, OUT=EOF, IN=0, región fuera de archivo | Sin acceso OOB ni truncado de duración |
| Caché | 8 s de loop, límite 64 s, miss, presión, resize con dos buffers | No expulsión de Active ni I/O en callback |
| Formatos | WAV/MP3/FLAC y decodificación disponible; 44.1/48/96 kHz origen | Índices del PCM interno a 48 kHz, sin huecos de codec |
| Concurrencia | load/reanálisis/resize rápidos, 100 órdenes, cola llena | Generaciones respetadas, Exit no se pierde |
| Gestos | pausa/play, Exit/Reloop, scratch/needle/hotcue/cue | Política de estados y last verificable |
| Sync | ambos roles, beat/compás, todos tamaños, octavas, cambio maestro | Sin seek/engage causados por wraps |
| Sonido | seno periódico, rampa/DC discontinuos, clicks/percusivo | Reloj intacto; salto reducido ≥20 dB; sin overshoot |
| Interfaz | mouse/atajo/MIDI, press/release, Preparing/Active/rechazo | Confirmación real; feedback no genera comandos |

Un error máximo de salto entre muestras de música arbitraria no demuestra por
sí solo ausencia de clicks. Comparar el mismo fixture/oráculo y localizar la
costura y toda la ventana (entrada/salida); verificar también que no se haya ocultado con un mute.

## Ejecución futura

Una vez agregados los targets de tasks.md:

```sh
cmake -S . -B build -DCMAKE_PREFIX_PATH="$(brew --prefix qt)" -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 4
ctest --test-dir build --output-on-failure -R 'loop_'
ctest --test-dir build --output-on-failure
```

Targets propuestos: `loop_transport`, `loop_state`, `loop_audio`, `loop_rt`,
`loop_sync`; QML dentro del runner ya disponible. **Antes de interpretar un
resultado vacío como éxito, comprobar `ctest --test-dir build -N`**: actualmente
estos targets no existen.

Instrumentar contadores de decoder seek/read, alloc/free y locks en el hilo de
audio. El tramo medido incluye activación, wraps, resize y salida+continuación,
no solo el bucle interno con datos calientes. No tolerar un único seek por vuelta.

## Evidencia de cierre

`docs/loop-validation.md` deberá registrar commit/build, sample rate, tamaños de
bloque, fixtures/hashes, error máximo de cursor/eventos, número de wraps, métricas
anti-click, memoria máxima, contadores RT y tests ejecutados. Adjuntar capturas
revisadas y límites de la escucha. No llamar «paridad Traktor/Serato» a un test
contra nuestro oráculo; una comparación real requiere medir esos productos.
