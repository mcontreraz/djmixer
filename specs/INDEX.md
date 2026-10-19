# Especificaciones técnicas

Las 17 specs del proyecto, cada una con su `spec.md`, su `plan.md`, sus `tasks.md` y sus contratos.
Es el índice de referencia: qué está especificado, qué está implementado y qué queda.

| Spec | Título | Propósito | Tareas |
|---|---|---|---|
| [`001-waveform-heatmap`](001-waveform-heatmap/spec.md) | Feature Specification: Waveform Heatmap |  | 25/25 tareas |
| [`002-needle-search`](002-needle-search/spec.md) | Feature Specification: Needle Search |  | 7/7 tareas |
| [`003-bpm-detection`](003-bpm-detection/spec.md) | Feature Specification: BPM Detection |  | — |
| [`004-beat-sync`](004-beat-sync/spec.md) | Feature Specification: Beat Sync |  | 0/13 tareas |
| [`005-cue-points`](005-cue-points/spec.md) | Feature Specification: Cue Points (CDJ) |  | 9/9 tareas |
| [`006-scratch`](006-scratch/spec.md) | Feature Specification: Scratch (plato + waveform) |  | 7/7 tareas |
| [`007-sync-engine-v2`](007-sync-engine-v2/spec.md) | Feature Specification: Sync Engine v2 (síntesis Serato + Mixxx) |  | 8/8 tareas |
| [`008-serato-grid-import`](008-serato-grid-import/spec.md) | Feature Specification: Serato Grid Import |  | 18/20 tareas |
| [`009-beat-detector`](009-beat-detector/spec.md) | Feature Specification: Real-time Beat Detector + Zapateo |  | 0/9 tareas |
| [`009-beat-this`](009-beat-this/spec.md) | Feature Specification: Beat This! (009) |  | 7/7 tareas |
| [`010-traktor-sync`](010-traktor-sync/spec.md) | Feature Specification: Traktor-parity Sync (010) |  | 0/8 tareas |
| [`011-vestax-vci100mk2-midi-audio`](011-vestax-vci100mk2-midi-audio/spec.md) | Feature Specification: Vestax VCI-100MK2 — MIDI + Audio |  | 0/20 tareas |
| [`012-mp3-flac-mp4-decode`](012-mp3-flac-mp4-decode/spec.md) | 012 — Decodificación MP3 / FLAC / MP4 |  | — |
| [`013-eq-3-bandas`](013-eq-3-bandas/spec.md) | Feature Specification: EQ de 3 bandas (HI/MID/LOW) |  | 5/12 tareas |
| [`014-mixer-strip`](014-mixer-strip/spec.md) | Feature Specification: Franja MIXER completa (EQ + Filtro + Gain, layout mockup) |  | 0/15 tareas |
| [`015-beatgrid-loop`](015-beatgrid-loop/spec.md) | Feature Specification: Loops seamless exactos por beatgrid |  | 29/30 tareas |
| [`016-key-lock`](016-key-lock/spec.md) | Feature Specification: Key Lock + Key Analysis |  | 17/24 tareas |

## Convenciones

- `spec.md` — qué y por qué; `plan.md` — cómo; `tasks.md` — el desglose; `contracts/` — los contratos verificables.
- Las rutas de fichero dentro de las specs apuntan al árbol de código, que se publica con la primera release.
- Cada spec tiene su checklist de requisitos y su evidencia de validación donde aplica.
