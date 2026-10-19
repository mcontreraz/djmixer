# Implementation Plan: Vestax VCI-100MK2 MIDI + Audio

**Branch**: `011-vestax-vci100mk2-midi-audio` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/011-vestax-vci100mk2-midi-audio/spec.md`

## Summary

RtMidi para MIDI (IN+OUT con `MidiController: QObject` + `QueuedConnection`
a los slots `Deck/Mixer/SyncEngine` existentes) y evolución de `Mixer` de
2ch fijos a selector por nombre con bus dual Master/Cue (4ch cuando la MK2
está presente, fallback 2ch intacto). Preset factory propio
`assets/midi/vestax_vci100mk2.json` convertido del XML de Serato (referencia
local, sin copiarlo). Jog relativo `delta=v-0x40`, LEDs por eco de nota,
Learn + `QSettings`. Diseño `UserIoEngine/Binding` genérico desde día 1 para
el salto a 208 MIDI + 14 HID sin reescribir.

## Technical Context

**Language/Version**: C++17 + Qt 6.5 (QML). Sin subir a C++20 (motivo por el
que se descarta libremidi para el MVP).

**Primary Dependencies**: NUEVA: RtMidi 6.x (MIT, base de QMidi/qmlmidi;
`brew install rtmidi` o submódulo `third_party/rtmidi`, backend
`__MACOSX_CORE__`, link `CoreMIDI+CoreAudio+CoreFoundation`). Resto ya
existe: miniaudio 0.11 (enumera y abre devices), TagLib, qmdsp, beatthis.

**Storage**: `assets/midi/vestax_vci100mk2.json` (factory, versionado) +
`QSettings` (user overrides + último puerto/device). Sin tocar sidecar `.wfcache`.

**Testing**: `midiprobe/midiin` de RtMidi + `Snoize MIDI Monitor` (volcado
usuario) + `ctest` existente + `DJMIXER_AUTOTEST=<wav>` (exit 0) +
`DJMIXER_SCREENSHOT` del nuevo `MidiPanel/AudioPanel` (Constitución II).

**Target Platform**: macOS arm64, CoreMIDI + CoreAudio. `DEVICE_DEFAULT` rate
(como Serato), no forzar 48 kHz.

**Project Type**: desktop-app (Qt Quick, `MACOSX_BUNDLE`).

**Performance Goals**: MIDI→UI <50 ms observados; `render()` sin asignar ni
bloquear (cero `new`/mutex/I-O en callback); audio 4ch sin xruns añadidos.

**Constraints**: Constitución I (hilo audio), II (evidencia ejecutada), III
(clean-room: XML de Serato solo referencia), IV (una dependencia nueva,
justificada aquí), V (código inglés / docs español).

**Scale/Scope**: 1 aparato a fondo (MK2 decks 0/1 + global); decks 2/3 del XML
ignorados; EQ/FX reservados; HID/OSC fuera (documentados en roadmap).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Audio-Thread Safety**: PASS — MIDI nunca toca `render()`; audio usa
  doble buffer/buses con atómicos; device switch fuera del callback.
- **II. Verification by Execution**: PASS — autotests + screenshot paneles +
  ciclos conecta/desconecta + medición de buses en buffer.
- **III. Clean-Room**: PASS — JSON propio desde números observados + XML
  local; XML propietario fuera del repo.
- **IV. Simplicity**: PASS — un `MidiController` + extensión de `Mixer` a
  4ch; sin framework genérico prematuro más allá del struct `Binding`.
- **V. Bilingual Clarity**: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/011-vestax-vci100mk2-midi-audio/
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── midi-mapping.json      # schema del factory + ejemplos MK2
│   ├── audio-route.json       # schema de ruta Master/Cue
│   └── aci-lite.md            # subset de acciones soportadas
└── tasks.md             # Phase 2 output
```

### Source Code (repository root, SOLO cuando se autorice implementar)

```text
src/
├── midicontroller.h/.cpp   # NUEVO: RtMidiIn/Out + Binding engine + Q_INVOKABLE open/learn/testLeds
├── mixer.h/.cpp            # EXTENDER: listar devices, abrir por nombre, buses master/cue, PFL
├── audioformat.h           # EXTENDER: rate negociado (no solo kSampleRate=48000)
├── main.cpp                # wiring MidiController + context property "Midi"/"Audio"
├── MidiPanel.qml           # NUEVO: puerto, estado, monitor hex, learn, jog-gain, probar LEDs
└── AudioPanel.qml          # NUEVO: selector device, master/cue gains, PFL state
assets/midi/
└── vestax_vci100mk2.json   # NUEVO: factory (decks 0/1 + global)
tests/
└── midi_binding_test.cpp   # NUEVO: binding parse + delta relativo + fallback 2ch (offscreen)
```

**Structure Decision**: single project existente; sin nuevos top-levels salvo
`assets/midi/` para presets versionados.

## Phases

### Phase 0: Outline & Research → [research.md](./research.md)

RtMidi vs libremidi/Drumstick, mapa MK2 del XML, audio Master/Cue de las
Vestax, riesgos (canal=deck, jog relativo, DEVICE_DEFAULT, shifts).

### Phase 1: Design & Contracts → [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

Structs `Binding/DeviceDescriptor/AudioRoute/UserMap`, schemas JSON,
subset ACI-lite, validación (volcado MIDI Monitor + buffer 4ch + screenshots).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Nueva dep RtMidi | Qt6 no trae MIDI; CoreMIDI directo = ObjC++/CF manual | libremidi exige C++20 en todo `djcore`; Drumstick arrastra Qt-widgets/ALSA sin aporte en macOS |
| Mixer 2ch→4ch | La MK2 expone MasterOut+CueOut; sin bus cue el PFL no existe | Dos devices agregados en macOS = frágil; un device 4ch es lo que declara Serato |
