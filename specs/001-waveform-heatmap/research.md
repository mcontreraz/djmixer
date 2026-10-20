# Research: Waveform Heatmap

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

## Decisión 1: Dónde corre el análisis

- **Decision**: `QThread` worker dedicado (`WaveformAnalyzer`), un job por deck con
  contador generacional; resultado vuelve por señal queued.
- **Rationale**: separa el decode pesado del hilo de audio (constitución I) y del
  hilo UI (SC-002). `QtConcurrent` descartado: peor control de cancelación.
- **Alternatives considered**: analizar en el hilo de audio aprovechando el
  decode existente del `Deck` (rechazado: contamina `render()` y mezcla ritmos);
  analizar en UI con `Timer` por chunks (rechazado: congela frames).

## Decisión 2: Cómo se decodifica

- **Decision**: `ma_decoder` independiente en el worker (mismo `miniaudio.h` (no publicado)).
- **Rationale**: cero dependencias nuevas (constitución IV); el Deck sigue con su
  propio decoder de streaming sin interferencias.
- **Alternatives considered**: FFmpeg/QtMultimedia (rechazados: peso y permisos nuevos).

## Decisión 3: Cómo se calcula el color por bucket (sin FFT externa)

- **Decision**: banco de 3 biquads propios (lowpass 250 Hz, highpass 4 kHz, medios
  por diferencia) + envolvente por rectificación y suavizado; mapeo
  graves→rojo, medios→verde, agudos→azul, con realce de pico global→amarillo.
- **Rationale**: sin dependencias, determinista, barato (3 filtros por muestra).
  La paleta imita la lectura Serato sin copiar nada suyo.
- **Alternatives considered**: kissfft vendorizada (más precisa, +1 dependencia y
  más CPU; diferida a beatgrid si hace falta); Essentia (pesada para F2, queda
  para análisis BPM/key posterior).

## Decisión 4: Formato y ubicación de la caché

- **Decision**: sidecar binario versionado
  `<CacheLocation>/waveforms/v1/<sha1hex(ruta|tamaño|mtime)>.wfcache`:
  header (magic `DJW1`, sampleRate, buckets, duración) + array de
  `{min,max,r,g,b}` float32.
- **Rationale**: lectura O(1) con `mmap`-like (`QFile::map`), sin motor SQL
  (constitución IV). Clave invalida sola si el archivo cambia (FR/edge de spec).
- **Alternatives considered**: tabla SQLite con blobs (requiere QtSql + driver
  desplegado; overkill); QSettings (formato texto, lento para miles de floats).

## Decisión 5: Resoluciones

- **Decision**: dos niveles por archivo: overview 256 buckets + detalle 4096
  buckets. Las grandes interpolan el detalle; el overview usa el nivel 0.
- **Rationale**: 4096×5 floats ≈ 80 KB por tema (9000 temas ≈ 700 MB sin LRU;
  con LRU 500 MB + limpieza al arranque). Suficiente para overview y zoom F2b.
- **Alternatives considered**: un solo nivel (pierde detalle en zoom); tiles
  progresivos (complejidad prematura).

## Decisión 6: Cancelación y concurrencia

- **Decision**: cada `Deck` lleva `analysisGeneration` atómico; el worker
  chequea cada N buckets y aborta si cambió; QML solo acepta el resultado con
  generación vigente.
- **Rationale**: cumple FR-007 sin locks entre worker y UI.
