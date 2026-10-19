# Tasks: VCI-100MK2 MIDI + Audio

**Feature**: `011-vestax-vci100mk2-midi-audio` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

> SDD preparado. Implementación NO iniciada (modo yolo desactivado por pedido).
> Ninguna tarea marcada: al autorizar, ejecutar en orden P1 → P2 → P3.

## Phase 1: Setup (infraestructura compartida)

- [ ] T001 Añadir RtMidi (`third_party/rtmidi` submódulo + fallback `brew`) y link `CoreMIDI/CoreAudio/CoreFoundation` en `CMakeLists.txt`; compilar `midiprobe/midiin` como smoke test
- [ ] T002 [P] Crear `assets/midi/vestax_vci100mk2.json` factory (decks 0/1 + global) según `contracts/midi-mapping.json`, convertido del XML local (sin commitear XML)
- [ ] T003 [P] Crear `tests/midi_binding_test.cpp` (parse JSON, delta relativo `v-0x40` acumulado, fallback 2ch) en modo offscreen

## Phase 2: Foundational (bloquea US1–US4)

- [ ] T004 Implementar `src/midicontroller.h/.cpp` (RtMidiIn/Out, `Binding` engine, `open/learn/testLeds`, `emit → QueuedConnection`, re-scan QTimer) + wiring en `main.cpp` (`Midi` context property)
- [ ] T005 Extender `Mixer` a selector por nombre (`ma_context_get_devices`), rate `DEVICE_DEFAULT`, fallback default; exponer lista a QML
- [ ] T006 Crear `MidiPanel.qml` + `AudioPanel.qml` (puerto/estado/monitor hex; device/master/cue/PFL) + captura `DJMIXER_SCREENSHOT` de verificación

## Phase 3: US1 — MIDI-IN básico (P1) 🎯 MVP

- [ ] T007 [US1] Mapear play Note34 / cue_play Note66 / prev Note67 / sync Note36-68 / load Note55 / browse ch5-Note55-56 a slots `Deck/SyncEngine/TrackListModel`
- [ ] T008 [US1] Mapear faders absolutos: pitch ch1-CC27/ch2-CC17 (`userSetPitch` ±8% + invert/deadzone), upfader ch1-CC28/ch2-CC22, cross ch5-CC16, master/cue ch5-CC20/18/19 (reservas donde no hay DSP)
- [ ] T009 [US1] Validar: volcado MIDI Monitor del usuario vs factory + `ctest` + autotest verdes

## Phase 4: US2 — Audio 4ch Master/Cue (P1)

- [ ] T010 [US2] Separar `Mixer::process` en buses master (0-1 post-cross) / cue (2-3 PFL pre-cross + cue_gain/mix); fallback 2ch = mezcla única actual
- [ ] T011 [US2] Mapear PFL Note54 + cue_gain/mix CC18-19 al bus cue; medir en buffer (cue aislado, master intacto)
- [ ] T012 [US2] Caída de device USB → fallback a default sin crash (10 ciclos conecta/desconecta)

## Phase 5: US3 — Jog scratch (P2)

- [ ] T013 [US3] `touch Note59 + move CC16`: tocado → `scratchGrab/scratchTo(pos+Σdelta*gain)/Release`; suelto → bend/nudge
- [ ] T014 [US3] Validar 10/10 agarres sin "pegado" + spin-down intacto (autotest scratch T-scratch verde)

## Phase 6: US4 — LEDs + Learn (P2)

- [ ] T015 [US4] Feedback OUT `Note→127/0` suscrito a `playingChanged/cueChanged/sync/pfl`
- [ ] T016 [US4] Learn por acción + `QSettings` (factory intacto) + "probar LEDs" (barrido)

## Phase 7: US5 — Roadmap genérico (P3, solo docs + seed)

- [ ] T017 [US5] Escribir `docs/midi-generic-roadmap.md` (UserIoEngine, importador XML local, matriz gold/silver/unmapped, HID/OSC fases)
- [ ] T018 [US5] Validar que un 2º JSON dummy aparece como preset sin tocar C++

## Phase 8: Polish

- [ ] T019 Limpiar debug, `checklists/` al día, commit en español, screenshots finales
- [ ] T020 Actualizar `README.md` hitos (MIDI MK2) solo si el usuario lo pide

## Dependencies

T001→T004; T002→T007; T003∥; T004→T007→T008; T005→T010→T011; T006 tras T004/T005;
T013 tras T007; T015 tras T007; T016 tras T015; T017 independiente (docs).
