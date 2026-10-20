# Especificaciones técnicas

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

Índice de referencia de las specs del proyecto: qué está especificado,
qué está implementado y qué queda. Es un índice **generado**
(`publica-docs.py` (no publicado)), no se escribe a mano: si una spec cambia, el
índice cambia con ella.

| Spec | Título | Ficheros | Tareas |
|---|---|---|---|
| [`001-waveform-heatmap`](001-waveform-heatmap/spec.md) | Feature Specification: Waveform Heatmap | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md, contracts/ | 25/25 tareas |
| [`002-needle-search`](002-needle-search/spec.md) | Feature Specification: Needle Search | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md | 7/7 tareas |
| [`003-bpm-detection`](003-bpm-detection/spec.md) | Feature Specification: BPM Detection | spec.md, plan.md | — |
| [`004-beat-sync`](004-beat-sync/spec.md) | Feature Specification: Beat Sync | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md, contracts/ | 0/13 tareas |
| [`005-cue-points`](005-cue-points/spec.md) | Feature Specification: Cue Points (CDJ) | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md, contracts/ | 9/9 tareas |
| [`006-scratch`](006-scratch/spec.md) | Feature Specification: Scratch (plato + waveform) | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md, contracts/ | 7/7 tareas |
| [`007-sync-engine-v2`](007-sync-engine-v2/spec.md) | Feature Specification: Sync Engine v2 (síntesis Serato + Mixxx) | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md, contracts/ | 8/8 tareas |
| [`008-serato-grid-import`](008-serato-grid-import/spec.md) | Feature Specification: Serato Grid Import | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md, contracts/ | 18/20 tareas |
| [`009-beat-detector`](009-beat-detector/spec.md) | Feature Specification: Real-time Beat Detector + Zapateo | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md, contracts/ | 0/9 tareas |
| [`009-beat-this`](009-beat-this/spec.md) | Feature Specification: Beat This! (009) | spec.md, research.md, tasks.md | 7/7 tareas |
| [`010-master-clock`](010-master-clock/plan.md) | Plan: MasterClock explícito (010) | plan.md | — (solo plan) |
| [`010-traktor-sync`](010-traktor-sync/spec.md) | Feature Specification: Traktor-parity Sync (010) | spec.md, research.md, tasks.md | 0/8 tareas |
| [`011-vestax-vci100mk2-midi-audio`](011-vestax-vci100mk2-midi-audio/spec.md) | Feature Specification: Vestax VCI-100MK2 — MIDI + Audio | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md, contracts/ | 0/20 tareas |
| [`012-mp3-flac-mp4-decode`](012-mp3-flac-mp4-decode/spec.md) | 012 — Decodificación MP3 / FLAC / MP4 | spec.md, plan.md | — |
| [`013-eq-3-bandas`](013-eq-3-bandas/spec.md) | Feature Specification: EQ de 3 bandas (HI/MID/LOW) | spec.md, plan.md, tasks.md | 5/12 tareas |
| [`014-mixer-strip`](014-mixer-strip/spec.md) | Feature Specification: Franja MIXER completa (EQ + Filtro + Gain, layout mockup) | spec.md, plan.md, tasks.md | 0/15 tareas |
| [`015-beatgrid-loop`](015-beatgrid-loop/spec.md) | Feature Specification: Loops seamless exactos por beatgrid | spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md, contracts/ | 29/30 tareas |
| [`016-key-lock`](016-key-lock/spec.md) | Feature Specification: Key Lock + Key Analysis | spec.md, plan.md, research.md, tasks.md, contracts/ | 12/24 tareas |

## Convenciones

- `spec.md` — qué y por qué; `plan.md` — cómo; `tasks.md` — el desglose;
  `contracts/` — los contratos verificables. No todas las specs tienen
  todos los ficheros: una spec cerrada con `plan.md` y `spec.md` no tiene
  `tasks.md`.
- Las rutas de fichero dentro de las specs apuntan al árbol de código, que
  se publica con la primera release (obligación de GPL-2.0-or-later).
- Cada spec tiene su checklist de requisitos y su evidencia de validación
  donde aplica.
