# Research: VCI-100MK2 MIDI + Audio

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

**Feature**: `011-vestax-vci100mk2-midi-audio` | **Date**: 2026-10-15

## R0. Cómo lo hace Serato (evidencia REA, solo lectura)

- `referencia-serato/replica/hardware-fx/README.md` (no publicado) (referencia local, **no publicada**)
  HW-04: 3 capas
  `Descriptor → Transporte → Acción ACI`. `hardware-contracts.json:171496` +
  `<artefacto local recuperado>/midi/midi_vestax_vci_100_mk2.xml`
  (93.670 B, sha `a7e822a0…`, 173 `control` = 123 Note On + 50 CC, 326 `userio`, 71 `case/condition`).
- Descriptor MK2: `VID 0x1AA1 / PID 0x0220 / midi_name "VCI-100MKII DJ-Controller" /
  mac_api CoreAudio / win_api WDMKS / rate DEVICE_DEFAULT / num_decks 4 /
  midi_mappable true / init F0 7E 00 06 01 F7`.
- Audio MK2: `outs [MasterOut, CueOut] / ins [Aux1In] / cue PER_CHANNEL_CUE /
  software_cue_gain+mix+master_cue`. Familia Vestax igual (Typhoon/300/380/400:
  MasterOut+CueOut; verificado por script en `plan-mode` 2026-10-15).
- Transporte MK2: **canal = deck** (ch1-4 decks 0-3, ch5 global). Controles
  clave decks 0/1: `play Note34, cue_play Note66, prev Note67, touch Note59,
  move CC16 (relativo), sync Note36 / sync_off Note68, pitch ch1-CC27/ch2-CC17
  (+shift CC30), keylock Note45, range Note77, upfader ch1-CC28/ch2-CC22,
  trim CC21, eq/filter CC17-28, pfl Note54, load Note55, fx Note37-44/CC22-26,
  deck_activate Note52/53, modifiers ch5-Note36/52`. Global ch5:
  `master CC20, cue_gain CC18, cue_mix CC19, cross CC16, browse Note55/56`.
- Salida: mismo `channel+control` con `event="output"`, `translation alias
  on=1/off=0 → 127/0`, `always_send`, `cache_id`.

## R1. Decisión MIDI: RtMidi (descartados libremidi/Drumstick/CoreMIDI directo)

| Opción | Licencia | CMake/macOS | Fallo para MVP |
|---|---|---|---|
| **RtMidi 6.x** | MIT (compatible GPL-2.0-or-later) | `brew` o submódulo, `__MACOSX_CORE__` + CoreMIDI/CoreAudio/CoreFoundation | — (elegida) |
| libremidi 5.x | BSD/MIT ok | CMake nativo, hotplug, MIDI 2.0 | exige **C++20** en todo `djcore`; overkill MIDI 1.0 2006 |
| Drumstick RT | GPL (fuerza GPL-3 al distribuir) | Qt6, no en brew-core | arrastra ALSA/widgets; nada extra en macOS |
| CoreMIDI directo | — | manual ObjC++/CF | cientos de líneas por nada |

Reglas: callback RtMidi en su hilo → solo `emit`; Qt `QueuedConnection`
al hilo UI; LEDs con `sendMessage({0x90,note,0x7F/0x00})`; re-scan por
`QTimer` (RtMidi sin hotplug).

## R2. Decisión audio: miniaudio existente, extendido a 4ch

- Hoy (`mixer.cpp:20-30`, `audioformat.h:7-8`): playback default 2ch f32 48 kHz.
- Plan: `ma_context_get_devices()` → abrir por nombre exacto; si `channels>=4`:
  `0-1 master post-cross, 2-3 cue pre-cross (PFL+c_gain+c_mix)`; si 2ch:
  fallback mezcla única (comportamiento actual). Rate = device default
  (no forzar 48 kHz). Switch de device fuera del callback; desconexión →
  fallback sin bloquear `render()`.

## R3. Riesgos y mitigaciones

- Números distintos por firmware/serie → Learn obligatorio + factory intacto.
- Jog relativo por ráfagas → acumular `delta=v-0x40`, un `scratchTo` por lote.
- Pitch invertido/hi-res → toggle `invert` + deadzone en binding.
- Curva cross del pot trasero → calibrar en software (equal-power ya existe).
- Shifts (`modifier_1/2`, `deck_activate`, 71 cases) → `conditions[]` en `Binding`,
  no botón→función plano.
- Límite legal: XML Serato nunca al repo (Constitución III); factory JSON propio.
