# Beat sync: revisión y corrección, 2026-10-14

## Hallazgos confirmados en este repositorio

1. `SyncEngine::tick` aplicaba pitch y seeks desde el temporizador Qt de 50 ms. El seek se calculaba con posiciones publicadas por un callback anterior. El retraso hasta aplicar el comando no se compensaba.
2. El mismo motor hacía seeks de adquisición, recuperación y microanclaje; reiniciaba el error suavizado a cero. El autotest consumía ese error, por lo que podía informar lock sin comprobar posiciones reales.
3. `SyncLab` y la app tenían algoritmos y constantes distintos, pese al comentario que afirmaba que probaban el mismo código.
4. La fase de mitad/doble tempo restaba coordenadas de beats sin convertir unidades; igualar el tempo no impedía que la fase caminara.
5. `conformToBpm` multiplicaba todos los tiempos por el cociente BPM mediano/nominal. Ejemplo: mediana 0,48 s, BPM refinado 124,17: un beat de 180 s terminaba en 181,203 s. Esa transformación no tenía respaldo en el audio.
6. `cleanGrid` podía conservar un beat espurio y eliminar el siguiente real. El caso `[0,.31,.5,1,1.5,2]` ahora conserva `.5` y elimina `.31`.
7. Las detecciones antiguas seguían entrando desde caché aunque cambiara el análisis.

## Cambio implementado

- `Mixer` aplica transporte pendiente de ambos decks, calcula sync y renderiza ambos dentro del mismo bloque. Qt publica configuración y refresca la UI.
- Configuración mediante triple buffer SPSC; asignaciones y destrucción de grillas quedan en el productor UI. La restauración de pitch tiene un serial y se aplica en audio.
- Un único corrector compartido con SyncLab; los seeks quedan restringidos al enganche/reenganche. El mantenimiento usa velocidad continua, con límites y rampa escalados por duración del bloque.
- Simple engancha al beat cercano; Smart al ciclo de compás. Se convierten beats del maestro a unidades del seguidor antes de envolver por beat/ciclo.
- Para detecciones se estima el tempo sobre intervalos vecinos, reduciendo escalones causados por cuantización. Los mapas Serato usan tempo local exacto.
- La grilla detectada conserva sus timestamps; la limpieza solo elimina subdivisiones con evidencia de ambos vecinos. Caché v9 rechaza detecciones antiguas y conserva las importadas Serato v8.
- El indicador de lock depende del error medido. El autotest histórico mide posiciones del mismo bloque y ya no fuerza el error a cero.

## Referencias REA reutilizadas y límites

La revisión reutilizó los artefactos guardados; no abrió ni ejecutó Serato/Traktor:

- `referencia-serato/replica/beatsync-native/FUN_100420cdc.c`: rutas distintas Simple/Smart y conversión de error a desplazamiento temporal.
- `referencia-serato/replica/beatsync-native/FUN_1010c1c4c.c`: ciclo 4/2/8 según octava.
- `referencia-serato/replica/beatsync-native/README.md`, secciones de octava y limitaciones: umbrales 4/3 y 2/3; frecuencia de tick y precisión de audio **no medidas**.
- `referencia-traktor/decompiled/SyncUnit_computePhaseSyncOffsetInBeats.c`: offset envuelto por un período parametrizable; la decompilación es incompleta. No demuestra por sí sola PLL, ausencia de seeks o implementación exacta del reloj.
- En la búsqueda local de `docs` y `specs` no apareció código ni un análisis REA de Mixxx, solo atribuciones. No se afirma equivalencia con esos tres productos.

La ejecución por bloque es una decisión de diseño propia validada en este motor; no se presenta como implementación recuperada de un binario propietario.

## Validación reproducible

```sh
cmake -S . -B build
cmake --build build -j 6
ctest --test-dir build --output-on-failure
```

`sync_audio_test` usa el decoder, resampler, Deck, Mixer y SyncEngine de producción. Renderiza sin dispositivo y sin procesar eventos Qt durante el hold, con bloques de tamaños distintos. Verifica fase y clicks de salida, ambas direcciones, pausa/reanudación, scratch, recuperación de fase sin seeks, cambio de tempo del maestro, Simple/Smart, octavas con WAV correspondientes, mapas variables, armado antes de Play, ausencia de grid, OFF y restauración manual.

`grid_cache_test` verifica formato antiguo, revisión de detector, conservación de Serato, limpieza y roundtrip exacto de timestamps cuantizados.

Caso de la captura:

```sh
./build/sync_audio_test --tracks \
  '<HOME>/Documents/McBaez - Back to Studio/Deep Garage Groove (Variation).wav' \
  '<HOME>/Documents/McBaez - Back to Studio/Faster High-Energy Eurodance Cover.wav' \
  build/sync-case.wav
```

Analiza ambos temas desde cero, parte de 72,7 s y 35,6 s, renderiza 60 s y comprueba que no hay seeks durante el mantenimiento. Exporta A por el canal izquierdo y B por el derecho, más posiciones/errores y grillas en CSV. Usa caché temporal mediante `DJMIXER_CACHE_DIR`.

## Estado de las preguntas

- ¿Falla el mantenimiento del sync por diseño del motor? **Respondido y corregido**, con regresiones de audio.
- ¿Se alteran incorrectamente las posiciones detectadas? **Respondido y corregido**, incluida invalidación de caché.
- ¿Son Simple, Smart y octavas coherentes? **Verificado en las pruebas propias**; equivalencia completa con productos externos no establecida.
- ¿La grilla automática coincide siempre con los golpes musicales reales? **No resuelto universalmente.** Un test de fase de grilla no prueba esto. Una comprobación exploratoria de ataques de graves del par real mostró offsets dependientes de la pista; seleccionar el pico de graves tampoco constituye ground truth musical. La salida renderizada permite auditar ese límite por separado.
- ¿Time-stretch con keylock? **Fuera del cambio**: Deck sigue usando remuestreo, por lo que cambiar velocidad cambia tono.

## Resultado de esta ejecución

- Compilación Release sin warnings y CTest: **2/2 passed**.
- Clicks 120/126 BPM, hold 30 s: error máximo `0.0000124337` beats; comprobación adicional sobre impulsos renderizados dentro de 5 ms.
- Par real de la captura, 60 s: **sin seeks repetidos**, error máximo respecto de la grilla `0.0229844` beats, RMS `0.00349841` beats.
- Análisis fresco: BPM nominal A `136.463`, B `117.967`. Son resultados del detector, no BPM musicales certificados; difieren de la captura con caché anterior.
- En ese ensayo el rate de B varió entre `1.03712` y `1.25584`. La interpolación elimina los escalones directos del tempo local pero **no resuelve toda la variabilidad de la detección**. No se declara resuelto el seguimiento musical ni paridad de sonido con Serato/Traktor/Mixxx.

## Seguimiento: pitch estable y salida del maestro de la mezcla

El ensayo anterior de fase permitió una modulación excesiva de velocidad: el
rate base seguía el tempo local de cada intervalo detectado. Estar alineado no
inhibía esa modulación. Se sustituye ese criterio para grillas detectadas:

- Tempo base constante, estimado mediante la mediana de períodos de 32 beats.
  Se calcula al publicar una grilla nueva, fuera del callback. La razón base
  es `tempoMaestro * rateMaestro / tempoSeguidor`, con el plegado de octava.
- Un controlador separado observa fase suavizada y aplica solo corrección
  fina durante el mantenimiento: máximo ±0,005 de rate (±0,5 puntos de pitch),
  rampa máxima 0,001 por segundo (0,1 puntos/s), banda muerta de 0,01 beats.
- Un desfase mayor de 1/8 de beat, sostenido tras el filtrado, permite recuperar
  fase con un presupuesto separado. No genera seeks periódicos. La recuperación
  termina antes de declarar mantenimiento para no arrastrar un nudge grande.
- Los mapas importados de Serato mantienen su tempo local explícito; un warp
  real requiere cambiar la velocidad. No se confunde con jitter del detector.
- STOP, fader de canal cerrado o crossfader que saca al maestro de la mezcla
  ceden la referencia al deck sincronizado que queda audible. Este conserva
  exactamente su rate; reabrir el canal anterior no le devuelve el mando.
  Bajar parcialmente un fader no cambia automáticamente el maestro.
- La selección de referencia usa la misma función en UI y audio; el callback
  también puede efectuar la transferencia si la UI no está procesando eventos.

Las regresiones nuevas verifican explícitamente variación y rampa de pitch,
relojes musicales de clicks con grillas cuantizadas a 20 ms, salida del maestro
y conservación exacta del rate en las tres formas de terminar una transición.
El test opcional de canciones reales mide conjuntamente fase, variación y
rampa; ya no acepta como éxito seguir cada marcador a cualquier velocidad.
Su cota de fase bruta detecta pérdidas de beat (1/4 de beat); la precisión
sobre relojes musicales conocidos sigue cubierta por los clicks de salida.

Resultado del seguimiento: compilación sin warnings, CTest 2/2 y ensayo real
con los dos temas de la captura completado. En 60 s, rate `1.13987..1.14979`
(antes `1.03712..1.25584`), paso máximo por bloque de 512 frames `0.0000107288`.
Error de fase bruto: máximo `0.128872` beats, RMS `0.0456706`; el aumento frente
al seguimiento rígido es el coste explícito de no modular el audio para seguir
cada irregularidad detectada. Los tres ensayos de transferencia preservaron
exactamente el pitch. Con clicks y detecciones cuantizadas, fase musical máxima
`0.00866031` beats y amplitud de variación de rate en hold `0.00296164`.
