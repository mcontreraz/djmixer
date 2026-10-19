# Contrato propuesto de Deck: loops

Estado: diseño, no API existente. UI/teclado/MIDI deben converger aquí.

## Propiedades de solo lectura

| Nombre | Tipo/unidad | Significado |
|---|---|---|
| `loopState` | enum Off/Preparing/Armed/Active | Estado confirmado por el motor |
| `loopAvailable` | bool | Pista+grid válidos; no promete caché ya residente |
| `loopLengthBeats` | double beats | Selección vigente; región activa publicada aparte si resize pendiente |
| `activeLoopLengthBeats` | double beats | Longitud efectivamente activa, 0 si Off |
| `loopIn`, `loopOut` | double segundos fuente | Límites de región activa/última válida; -1 si no existen |
| `loopPending` | bool | Solicitud aún no aplicada |
| `canReloop` | bool | Última región compatible con pista/revisión |
| `loopError` | enum | None/NoTrack/NoGrid/InvalidGrid/OutOfTrack/TooLong/Busy/CacheFailed |
| `loopAppliedSerial` | uint64 | Última intención confirmada, no último click |

`loopChanged` y rechazo se notifican en el hilo UI desde snapshot. No expone
punteros PCM ni hace que una escritura QML eluda el scheduler.

## Intenciones

- `toggleAutoLoop(double lengthBeats)`: longitudes `{0.125,0.25,0.5,1,2,4,8,16}`.
  En Active la misma longitud sale; otra cambia tamaño conservando IN.
- `halveLoop()` / `doubleLoop()`: selección Off o Resize Active. Saturar en el
  mínimo/máximo sin volver a alternar Active.
- `exitLoop()`: idempotente y prioritario; cancela también preparación/armado.
- `reloop()`: requiere región última válida; no cambia `playing`. Si está fuera
  de ella posiciona en IN por la ruta preparada; con sync conserva fase continua.
- `cancelLoopForTransport(reason)`: llamada interna antes de scratch/seek/cue/load;
  política de conservar/borrar last según el modelo de datos.

La API no recibe directamente muestras enteras desde UI. Captura posición en el
hilo de audio, valida la orden y devuelve aplicación/rechazo mediante serial.

## MIDI

Acciones lógicas propuestas: `auto_loop`, `loop_half`, `loop_double`, `loop_exit`,
`reloop`. `auto_loop` lleva longitud explícita, no índice de slot ambiguo.
Note-on/press ejecuta una vez; note-off/release no alterna. Repetición de encoder
se traduce a pasos discretos serializados. Feedback nunca llama estos setters.
Los aliases de ACI Serato son evidencia de interfaz, no bytes MIDI para Vestax.

## Prioridad y grid

Por callback: aplicar cambio de pista/cancelación prioritaria → consumir intenciones
válidas → adoptar ventanas listas → resolver frontera → render spans → publicar
snapshot. Sync recibe la misma revisión y coordenadas antes de calcular ajustes.
No ejecutar un comando de otra generación aunque su caché haya llegado después.

Auto Loop v1 usa grid siempre; un futuro Quantize OFF necesitará contrato nuevo
para captura libre/manual. No reutilizar `SyncEngine` On/Off como interruptor de
cuantización del loop.

## Compatibilidad

Se conservan volumen, EQ, filtro, gain y crossfader durante wraps. El loop no
reescribe tags musicales, grid, cues ni sidecars. La posición visible sigue siendo
la del archivo; `continuousBeat` es interno al transporte/sync y al diagnóstico.
