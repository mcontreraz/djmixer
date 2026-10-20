# Research: Serato Grid Import

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

**Feature**: `008-serato-grid-import` | **Date**: 2026-10-13

## R0. Payload BeatGrid v1 — DECIDIDO

Formato recuperado en `referencia-serato/replica/beatgrid-datos/serializer-v1.md` (no publicado)
(referencia local, **no publicada**):

- Cabecera: `01 00` + N uint32 BE (con reinterpretación syncsafe si la longitud no cuadra).
- Records de 8 B: float32 BE (tiempo s) + uint32 BE (beats hasta próximo marker).
- Terminal: float32 tiempo + float32 BPM.
- Validador: tiempos crecientes, BPM>0, ≤128 marcadores, 0-2 bytes opacos finales.
- Herramienta: `beatgrid_blob.py` + `verify_blob.py` (12 pruebas verdes).

**Decisión**: implementar el parser C++ contra esa spec, byte a byte; `verify_blob.py` es el oráculo.

**Alternativa rechazada**: copiar el parser Python a C++ sin entender → no; se reimplementa desde la tabla de layout, se verifica contra el oráculo.

## R1. Wrappers por contenedor — PARCIAL

- **MP3**: frame GEOB `Serato BeatGrid` (ID3v2). TagLib: `ID3v2Tag::frameList("GEOB")` + MIME/desc. Verificado por Mixxx (contraste, no copia).
- **M4A**: átomo freeform `----:com.serato.dj:beatgrid`. TagLib: `MP4Tag::itemMap`. Contenido = mismo payload v1.
- **OGG/FLAC**: nombres `SERATO_BEATGRID` documentados en strings, wrapper pendiente → **fuera de alcance** (fallback a detección).

**Decisión**: MP3 GEOB + M4A freeform; resto = fallback.

## R2. Conversión payload → BeatGrid — DECIDIDO

Cada tramo marker[i]→marker[i+1] con `beatsToNext` beats: interpolar beats
uniformes a BPM local del tramo (`beatsToNext / Δt × 60`). Tramo terminal:
extender con BPM final. Resultado: `beats[]` (segundos) + bpm + downbeat
(marker[0], Serato cuenta desde downbeat) + locked + source=serato.

Límite honesto: si `beatsToNext` no es múltiplo cercano de 4 (gate
`101925f34`), el payload es válido pero "no 4/4 puro" → importar igual, el
sync por distancia lo absorbe; documentar, no rechazar.

## R3. Dónde enganchar — DECIDIDO

`WaveformAnalyzer` (worker): antes de detectar, intentar `SeratoGrid::parse(file)` →
éxito = rellenar `BeatGrid` + source; fallo = detección actual sin cambios.
Sin tocar `SyncEngine` (consume `BeatGrid` igual) ni el hilo de audio.

## R4. Sidecar v8 — DECIDIDO

`.wfcache` v7 ya guarda beats+bpm+downbeat. Bump a v8 añadiendo
`locked:u8` + `source:u8`; lector v7→v8 con defaults (unlocked, detected).
Sin migración de archivos viejos: se re-analizan bajo demanda.

## R5. Lock — DECIDIDO

Fuente del lock: XML `<BpmLock>` / UI grid-locked (evidencia: ACI
`grid_lock`, `asset.is_beatgrid_locked`). En tags: `Serato Markers2` puede
traerlo; si no se encuentra, lock=false pero source=serato igual.
Re-análisis con locked → conserva caché sin tocar.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Wrapper M4A difiere (prefijos) | inspeccionar bytes reales de un .m4a propio con script antes de codificar |
| Payload v2 en archivos nuevos | versión != 1.0 → fallback + log, sin romper |
| TagLib no expone GEOB crudo | fallback: parseo ID3v2 manual mínimo solo del frame GEOB |
