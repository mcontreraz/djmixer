# Modelo de datos: loop por beatgrid

Todas las entidades son propuestas, todavía no existen en `Deck`.

| Entidad | Campos esenciales | Propietario / invariantes |
|---|---|---|
| `LoopIntent` | serial monotónico, trackGeneration, gridRevision, action, lengthBeats | UI productor; longitudes de una lista cerrada, unidades beats |
| `PreparedLoopWindow` | handle del pool, requestSerial, trackGeneration, gridRevision, firstFrame, frameCount, guards, PCM estéreo | Worker prepara; audio consume solo Ready; worker retira tras ack |
| `LoopRegion` | startBeat, lengthBeats, inFrame/outFrame double, gridRevision | `out>in`, ambos de la misma grid; dentro de duración; ≤64 s |
| `ActiveLoop` | región, handle fijado, localCursor double, wrapCount uint64 | Audio exclusivamente; p en `[A,B)`; contador no sustituye fracción |
| `MusicalTransport` | beatOffset double, continuousBeat, gridRevision, downbeat | Por deck, sobrevive a Exit/Off; la revisión define sus coordenadas |
| `LoopSnapshot` | appliedSerial, generation, state, pendingAction, current/last region, rejection, audiblePosition, continuousBeat | Audio→UI coherente; UI emite NOTIFY |
| `PendingGrid` | nueva revisión preparada, generación y mapa inmutable | No sustituye grid activo durante loop; adoptar fuera de él con rebase de fase |

## Estados

```text
Off --AutoLoop reproduciendo, miss--> Preparing --Ready--> Armed --frontera--> Active
Off --AutoLoop pausado/Reloop, miss--> Preparing --Ready/posición preparada--> Active
Off --AutoLoop/Reloop, ready------------------------------------------------> Active
Active --Resize miss--> Active + pendingResize --Ready/commit-----------> Active
Active --Pause--------> Active (playing=false) --Play-------------------> Active
Preparing/Armed/Active --Exit/Cancel------------------------------------> Off
cualquier estado --Load nueva generación-------------------------------> Off + clear last
```

`Armed` es una frontera musical futura para Auto Loop reproduciendo, no una
demora UI en milisegundos. Reloop conserva su región y aplica el salto preparado
a IN si hace falta, sin esperar una frontera futura; Auto Loop pausado activa
su región al terminar la preparación, sin iniciar Play.
`Active + pendingResize` conserva región y caché antiguas hasta commit atómico.
Una orden nueva reemplaza la intención pendiente y retira sus buffers fuera
RT; no altera una región activa hasta que la nueva esté lista.

## Matriz de transiciones

| Acción | Off | Preparing / Armed | Active |
|---|---|---|---|
| AutoLoop(L) | Preparar/capturar L | Reemplazar intención; mismo L cancela | Mismo L=Exit; distinto L=Resize |
| ÷2 / ×2 | Cambiar selección, sin reproducir | Cambiar longitud solicitada | Resize dentro de límites |
| Exit | Idempotente | Cancelar preparación/armado | Continuar desde p; conservar último intervalo |
| Reloop | Recuperar último válido, preparar si hace falta | Reemplazar por último válido | No-op; salida tiene comando explícito |
| Pause | Pausar | Pausar y permitir terminar preparación sin arrancar | Conservar región, cursor, offset y estado |
| Play | Reproducir normal | Continuar preparación/armado | Reanudar desde cursor activo |
| Scratch / seek / cue | Flujo existente | Cancelar primero | Exit primero; gesto tiene autoridad de posición |
| Carga nueva | Borrar last | Invalidar serial y devolver resultados tardíos | Retirar caché; borrar last y offset |
| Grid nueva | Adoptar y validar last | Cancelar candidato y recalcular | Fijar revisión anterior; marcar nueva pendiente |

Al adoptar otro grid, el último intervalo antiguo pierde elegibilidad para
Reloop hasta validación/reconstrucción explícita. No reinterpretarlo en silencio.

## Propiedad y concurrencia

- No leer un QVector mutable del `WaveformCache` desde audio. Mapa congelado
  publicado por ownership, junto a sus revisiones.
- Una respuesta lleva **generación + revisión + serial**; coincidir solo con la
  ruta del archivo no basta si la misma pista se volvió a cargar.
- No confundir `analysisGeneration` existente con revisión editable de grid.
  Crear contadores distintos si el código actual no separa esos eventos.
- Cola fija de 64 intenciones; un rechazo Busy es visible. Exit tiene serial
  prioritario para invalidar órdenes viejas aun con cola llena.
- Snapshot tipo mailbox/seqlock; sin signals, alloc ni destrucción en audio.
- Resetear beatOffset en carga/seek deliberado. Cada wrap lo incrementa en L;
  pausa y Exit conservan su valor. Resize y Reloop conservan **continuousBeat**,
  recalculando beatOffset cuando cambia el cabezal (`oldLocal-newLocal`).
