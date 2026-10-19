# Plan 012 — Decodificación MP3 / FLAC / MP4

No se buscó nada en bibliotecas: el archivo esencial es el miniaudio embebido
(`third_party/miniaudio.h`), que documentó el CD de formato y una API exacta
de backends custom (`ma_decoding_backend_vtable` + base de `ma_data_source`).
Ese es el flujo que se usa.

## Componentes

1. `src/mp4decoder.{h,cpp}`:
   - namespace `decode::attach(ma_decoder_config&)` — una función breve que
     recibe cualquier `ma_decoder_config` y le conecta los backends custom.
   - struct `Mp4File` con `ma_data_source_base` como primer miembro.
   - `onInitFile` solamente: miniaudio provee `onInit` via wrapper genérico si
     no existe (docs: "If these are not specified, miniaudio will deal with
     it for you via a generic implementation"). Suficiente para archivos.
   - Extensiones aceptadas: `mp4|m4a|aac|mov` (comparación ASCII, inversa).
   - Flujo open: suffix check → `CFURLCreateWithFileSystemPath` +
     `ExtAudioFileOpenURL` → `kExtAudioFileProperty_FileDataFormat` → client
     ASD (f32 packed, 8 B/frame, 2 ch, 48000) → `ClientDataFormat` →
     `FileLengthFrames` × 48000/rate → cachea `totalFrames`.
   - `read`: FIFO interno (4096 frames por refill con `ExtAudioFileRead`,
     que ya entrega f32 estéreo 48k). Devuelve `MA_AT_END` cuando no sirvió
     nada y llegó al final (Deck mejora EOF con `framesRead == 0`).
   - `seek(frameIndex)`: limpia FIFO, `ExtAudioFileSeek(xaf, frame)`.
   - `getCursor` / `getLength` / `getDataFormat` directos.
   - macOS-only: en otras plataformas stub `MA_INVALID_FILE` (FR-DECODE-6).

2. Wiring:
   - `Deck::processPendingLoad` → `decode::attach(cfg)`.
   - `WaveformAnalyzer` (2 sitios de `ma_decoder_init_file`) → `decode::attach`.
   - `TrackListModel::kExts` += `mp4`, `mov`.
   - CMake: AudioToolbox ya está linkeada (usada por el encoder WAV del
     análisis) — solo entra `mp4decoder.cpp` a `djcore`.

## Verificación

- Fixtures `/tmp/f012_{{mp3,flac,mp4,m4a}}` con ffmpeg (sine 440, 30 s).
- `DJMIXER_AUTOTEST=<fixture>` × cada formato; exit 0.
- `ctest` 4/4. Screenshot de carga en app de un .mp4 (informativa).

## 012-b (ralto en vivo)

Con los rips de YouTube (AV1+Opus) ExtAudioFile no abren: transcondenación-on-demand
más rápida vía stream-copy `ffmpeg -c:a copy` a `.opus` (0.4 s) y decodificación directas
con libopusfile — backend custom `src/opusdecoder.cpp` (48k nativo, fold-down estéreo,
seek op_pcm_seek). Registro combinado: `decode::attachCustomDecoders` incluye
ambas vtables (mp4 AudioToolbox + opus opusfile). Vorbis .ogg se rechaza.
