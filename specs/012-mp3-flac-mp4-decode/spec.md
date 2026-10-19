# 012 — Decodificación MP3 / FLAC / MP4

## Contexto

La app decodifica con miniaudio embebido (`third_party/miniaudio.h`), cuyo
resumen oficial declara solo tres decodificadores build-in: **WAV, MP3 y
FLAC**. Esta feature asegura esa cobertura y añade **MP4/M4A (AAC)**.

Requisito del usuario: soportar *decodificación* de MP3, FLAC y MP4
(solo el audio del video; la mezcla de video es una fase futura — FR-VIDEO-MIX).

## Alcance

### En alcance
1. **MP3 y FLAC**: verificación por ejecución (/fr-verify) con archivos reales
   generados por ffmpeg; el motor ya los decodifica vía dr_mp3/dr_flac.
2. **MP4/M4A/AAC**: backend custom de miniaudio (`ma_decoding_backend_vtable`)
   que abre el archivo con `ExtAudioFile` (AudioToolbox, ya linkeada en el
   proyecto) y convierte SIEMPRE a f32 estéreo 48 kHz — el formato interno que
   Deck, el analizador de waveform, el beatgrid y el sync asumen.
3. **Browser**: el escaneo de biblioteca incluye las extensiones nuevas
   (`mp4`, `mov`) en `TrackListModel::kExts` (wav/mp3/flac/m4a/aac ya estaban).
4. Deck, WaveformAnalyzer y cualquier `ma_decoder` futuro comparten el
   registro de backends custom (`decode::attach(cfg)`).

### Fuera de alcance
- Reproducción de video (video-latency, timestamps, vías de render).
- Mezcla de videos (fase futura FR-VIDEO-MIX).
- Decodificadores de Vorbis (este build de miniaudio no trae `MA_VORBIS`;
  .ogg queda sin soporte — documentado, no bloquea).
- ALAC en .m4a llega gratis vía ExtAudioFile (bonus, no se testea aparte).

## Reglas de negocio

- **FR-DECODE-1**: `ma_decoder_init_file` acepta .mp3/.flac (built-in) y
  .mp4/.m4a/.aac/.mov (backend custom) con el mismo flujo que WAV.
- **FR-DECODE-2**: el backend custom emite **f32 / 2 ch / 48 kHz** siempre,
  sin importar el formato nativo del archivo (AAC a 44.1 kHz se resamplea en
  la conversión de ExtAudioFile, no en el resampler del Deck).
- **FR-DECODE-3**: `onGetLength` devuelve la duración exacta convertida a
  frames cliente (FileLengthFrames × 48000/nativa) — Deck la usa para
  duration, waveform y fin de pista.
- **FR-DECODE-4**: seek por frames cliente con `ExtAudioFileSeek` (los
  offsets de ExtAudioFile son en frames del formato cliente).
- **FR-DECODE-5**: si la extensión no es mp4/m4a/aac/mov, `onInitFile`
  devuelve `MA_INVALID_FILE` para que miniaudio siga con los built-in
  (un .mp3 **nunca** pasa por el backend custom).
- **FR-DECODE-6**: en plataformas que no sean Apple el backend es stub
  (`MA_INVALID_FILE`) sin compilar AudioToolbox.
- **FR-DECODE-7**: sin bloqueo compartido: cada `ma_decoder` instancia su
  propio `ExtAudioFile`; el backend se usa desde el hilo de audio o el hilo
  de análisis (uno por instancia, nunca compartido).

## Verificación (constitution II)

- Fixtures en `/tmp` generadas con ffmpeg (sine 440 Hz, 30 s): `.mp3`,
  `.flac`, `.mp4`, `.m4a`.
- Arnés existente: `DJMIXER_AUTOTEST=<fixture>` para cada formato —
  verifica carga, duración, determinismo, declick y reanudación.
- `ctest` (4 tests existentes) sigue en verde.

## Riesgos

- El mapeo frames cliente→nativos de ExtAudioFile: se cubre el caso AAC
  44.1 kHz con fixture \*.m4a y verificando posiciones deterministas.
- VBR/AAC con duración estimada: `FileLengthFrames` es del AudioFile real
  (no estimación del header), así que es constante por pista.
