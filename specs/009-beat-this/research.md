# Research: Beat This! (009)

## R0. Fuente — DECIDIDO

`mosynthkey/beat_this_cpp` (MIT): port C++ con `onnx/beat_this.onnx` (79 MB,
preconvertido), `Source/beat_this_api.h` (`BeatThis::process_audio` →
`{beats, downbeats, beat_counts}`), Mel (PocketFFT, BSD) + resample r8brain
(MIT) + ORT. Submódulos pocketfft/r8brain por https (el .gitmodules usa SSH,
no sirve tal cual).

## R1. Integración — DECIDIDO

Submódulo shallow de beat_this_cpp + init solo de `Submodule/pocketfft` y
`Submodule/r8brain` (miniaudio ya propio). Se compilan: MelSpectrogram,
InferenceProcessor, Postprocessor, DBNPostprocessor, beat_this_api + fuentes
pocketfft/r8brain necesarias. ORT vía brew (1.31, dylib) con rpath. Modelo
como gitlink (no se commitea el binario).

## R2. Modo — DECIDIDO

Minimal primero (picos sobre logits). DBN (HMM+Viterbi) solo si Minimal no
cumple SC-001/SC-002. beat_counts del modelo → downbeatIdx directo.

## R3. Cadena — DECIDIDO

Serato tag → Beat This! → QM → propio. Sin modelo en disco: skip silencioso
(SC-004). Sin cambios en `BeatGrid`, sync ni sidecar (v8 ya guarda todo).

## R4. Riesgos

| Riesgo | Mitigación |
|---|---|
| ORT 1.31 vs opset del modelo (1.18-era) | probar inferencia en 1 archivo; si falla, pinnear ORT |
| 79 MB en cada clon | shallow + modelo solo en quien compila |
| Latencia (transformer en CPU) | worker + caché; medir y reportar s/archivo |

## SHAs fijados (2026-10-14)

- beat_this_cpp: `07ab790` + commit local `b0603d2` (header use_dbn, miniaudio declaraciones)
- pocketfft (https manual): `c90e55b`
- r8brain-free-src (https manual): `cb2abb9`
- qm-dsp: `e34a3cc` · qm-vamp-plugins: `c918afc`
- ONNX Runtime: brew 1.31.0 (dylib). Bug teardown: no destruir Ort::Env (se fuga a propósito).
