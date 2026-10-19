# Data Model: Waveform Heatmap

## WaveformCache

Caché de análisis por archivo de audio. Clave = `sha1(ruta_absoluta | tamaño_bytes | mtime)`.
Archivo: `<CacheLocation>/waveforms/v1/<clave>.wfcache`.

| Campo | Tipo | Reglas |
|---|---|---|
| magic | `char[4]` = `DJW1` | validación de formato |
| version | u32 = 2 | v1 escribía floats como double (bug QDataStream); se rechaza |
| durationSec | f64 | `lengthFrames / sampleRate` |
| overviewBuckets | u32 = 256 | nivel 0 |
| detailBuckets | u32 = 4096 | nivel 1 |
| buckets | array `{min,max,r,g,b}` f32 | `min ≤ 0 ≤ max` normalizado a −1..1; rgb 0..1 determinista por contenido |

Relaciones: `Track (url) 1—0..1 WaveformCache` (ausencia = aún no analizado).
Estados: `missing → analyzing → ready | failed`. `failed` degrada a overview
vacío (FR-008) y no reintenta hasta que cambie el archivo.

## Deck (extensión)

| Miembro | Rol |
|---|---|
| `analysisGeneration` (atómico u64) | invalida jobs viejos; se incrementa en cada `loadFile` |
| `waveformCache` (propiedad QML, solo lectura) | puntero al caché listo o nulo + señal `waveformReady()` |

## Límites LRU

Techo 500 MB en `waveforms/v1/`; al arrancar se borran los más antiguos por
fecha de acceso hasta volver bajo el techo.
