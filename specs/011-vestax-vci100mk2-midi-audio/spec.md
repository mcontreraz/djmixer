# Feature Specification: Vestax VCI-100MK2 — MIDI + Audio

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Feature Branch**: `011-vestax-vci100mk2-midi-audio`

**Created**: 2026-10-15

**Status**: Draft (SDD preparado; sin código. Modo yolo desactivado por pedido explícito)

**Input**: User description: "conectar controlador midi Vestax VCI-100 MK2 (Serato la reconocía altiro); compatible con todo lo que es compatible Serato; cómo lo hace Serato (REA en docs); soundcards de Vestax"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Tocar con la MK2 por MIDI-IN (Priority: P1)

El usuario conecta la VCI-100MK2 por USB, abre la app, elige el puerto
`VCI-100MKII DJ-Controller` y controla play/cue/sync/pitch/vol/cross/browse/load
sin tocar el mouse. La app sigue sonando por el dispositivo actual.

**Why this priority**: Es el valor inmediato: la controladora que el usuario
ya tiene pasa de pisapapeles a instrumento.

**Independent Test**: Con la MK2 conectada: pulsar Play A → `DeckA.playing==true`;
mover cross → `Mixer.crossfade` sigue 0-127; mover pitch → `userPitch` ±8%.
Todo verificable sin audio externo (observando QML + monitor hex).

**Acceptance Scenarios**:

1. **Given** MK2 conectada y puerto seleccionado, **When** pulso Play A (Note 34 ch1), **Then** DeckA alterna play/pause y el LED espeja el estado.
2. **Given** MK2 conectada, **When** muevo crossfader (ch5 CC16), **Then** `Mixer.crossfade` = valor/127 con curva equal-power intacta.
3. **Given** puerto ausente (MK2 apagada), **When** arranco la app, **Then** no hay crash: panel MIDI muestra "desconectado" y la app sigue usable con mouse.

---

### User Story 2 — Sonar por la tarjeta de la MK2 con cue en cascos (Priority: P1)

El usuario selecciona `VCI-100MKII DJ-Controller` como salida de audio:
parlantes por MasterOut (ch0-1) y preescucha PFL por CueOut (ch2-3),
como hace Serato. PFL por canal, `cue_gain/mix`, master independientes.

**Why this priority**: Sin esto los botones PFL y knobs de cue de la MK2
son decoración. El usuario lo pidió en paralelo al MIDI-IN.

**Independent Test**: Con tarjeta MK2 elegida (o dispositivo virtual de 4ch):
activar PFL A → solo CueOut lleva A; MasterOut lleva la mezcla cross.
Con dispositivo de 2ch (Mac interno) → fallback: todo a master, sin crash.

**Acceptance Scenarios**:

1. **Given** salida MK2 4ch, **When** activo PFL A y cue_mix=cue, **Then** CueOut contiene A pre-cross y MasterOut la mezcla post-cross.
2. **Given** solo salida 2ch, **When** selecciono audio, **Then** la app suena igual que hoy (mezcla única) y el panel lo indica.
3. **Given** desconecto la MK2 a mitad de sesión, **When** el device desaparece, **Then** la app cae a default sin crash ni cuelgue del hilo de audio.

---

### User Story 3 — Jog scratch vinílico desde la MK2 (Priority: P2)

Girar el jog con la mano encima hace scratch (`platter_touch` Note 59 +
`platter_move` CC16 relativo); sin mano encima hace nudge/pitch-bend.

**Why this priority**: Es el gesto DJ central; depende de US1 pero se prueba aparte.

**Independent Test**: `touch on + CC16 ±` → `Deck.scratching==true` y
`waveformPosition` sigue la mano; `touch off + giro` → nudge sin scratch.

**Acceptance Scenarios**:

1. **Given** touch A activo, **When** giro CW (val>0x40), **Then** la posición avanza proporcional a `delta*gain`.
2. **Given** touch suelto, **When** giro, **Then** no entra en scratch (bend momentáneo).

---

### User Story 4 — LEDs + Learn (Priority: P2)

Play/cue/sync/PFL encienden su LED en la MK2; cualquier acción se puede
re-aprender a otro control; botón "probar LEDs" hace barrido.

**Why this priority**: Feedback + compatibilidad larga cola (cubre variantes
de firmware sin hardcodear).

**Independent Test**: toggle Play → LED misma nota on/off; Learn de Sync a
otra nota → la nueva dispara sync y persiste tras reinicio (`QSettings`).

**Acceptance Scenarios**:

1. **Given** DeckA sonando, **When** miro la MK2, **Then** LED Play A encendido (127), apagado en pausa (0).
2. **Given** modo Learn en Sync B, **When** pulso un botón libre, **Then** queda asignado y el factory JSON no se modifica.

---

### User Story 5 — Ruta a "todo Serato" documentada (Priority: P3)

Queda documentado (no implementado) el salto de 1 a 208 MIDI + 14 HID:
motor `UserIoEngine`, importador XML local, matriz gold/silver/unmapped.

**Why this priority**: Evita reescribir el MVP cuando se añadan FLX4/DDJ/etc.

**Independent Test**: Añadir un segundo JSON de otro aparato sin tocar C++
(siguiendo `contracts/midi-mapping.json`) → el motor lo lista.

**Acceptance Scenarios**:

1. **Given** dos JSON en `assets/midi/`, **When** arranco, **Then** ambos aparecen como presets elegibles.

---

### Edge Cases

- MK2 encendida después que la app → re-scan la encuentra sin reiniciar.
- Firmware con CCs desplazados → Learn lo resuelve; factory intacto.
- Canal MIDI inesperado (MKI manda todo ch1) → el matcher acepta por nota/CC + canal documentado, no solo por canal.
- Jog a ráfagas (mensajes múltiples por tick) → se acumulan deltas, no un seek por mensaje.
- Device audio con rate != 48000 → se sigue `DEVICE_DEFAULT` (como Serato), sin forzar 48 kHz.
- Desconexión USB a mitad de scratch/audio → release seguro + fallback, nunca `render()` bloqueado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST listar puertos MIDI y auto-seleccionar `*VCI*`/`*Vestax*`; re-scan sin reiniciar.
- **FR-002**: El sistema MUST mapear el subset MK2 decks 0/1 + global según `midi_vestax_vci_100_mk2.xml` (play Note34, cue_play Note66, touch Note59, move CC16, sync Note36/68, pitch ch1-CC27/ch2-CC17, upfader ch1-CC28/ch2-CC22, cross ch5-CC16, master/cue ch5-CC20/18/19, PFL Note54, load Note55, browse ch5-Note55/56, modifiers ch5-Note36/52).
- **FR-003**: Los callbacks MIDI MUST NOT llamar a `Deck/Mixer` directo: solo `emit → QueuedConnection` al hilo UI (Constitución I).
- **FR-004**: El sistema MUST listar dispositivos de audio (miniaudio) y abrir por nombre (`VCI-100MKII DJ-Controller` o default), siguiendo el rate del device.
- **FR-005**: Con salida ≥4ch el sistema MUST separar buses MasterOut (0-1, post-cross) y CueOut (2-3, PFL pre-cross + cue_gain/mix); con 2ch MUST mezclar a master (fallback actual).
- **FR-006**: Jog relativo MUST interpretarse como `delta = value - 0x40` acumulado, con `gain` ajustable e `invert` opcional.
- **FR-007**: El sistema MUST espejar estado a LEDs (misma nota, 127/0) para play/cue_play/sync/pfl.
- **FR-008**: El sistema MUST ofrecer Learn por acción + persistencia usuario (`QSettings`) sin modificar el factory JSON.
- **FR-009**: El factory MK2 MUST vivir en `assets/midi/vestax_vci100mk2.json` (formato propio `contracts/midi-mapping.json`, clean-room: sin copiar el XML de Serato al repo).
- **FR-010**: La caída de MIDI o audio USB MUST degradar a mouse/default sin crash ni bloqueo del hilo de audio.

### Key Entities

- **MidiBinding**: `{ channel, control, eventType (Note On/CC), action (ACI-lite), deckId/deckSet, translation (range/alias/deadzone/reversed), output }`.
- **DeviceDescriptor**: `{ vendorId 0x1AA1, productId 0x0220, midiName, audioName, numDecks 4 (usamos 0-1), initSysEx, midiMappable }`.
- **AudioRoute**: `{ deviceName, api (CoreAudio/WDMKS), outs [MasterOut, CueOut], ins [Aux1In], cueType PER_CHANNEL_CUE }`.
- **UserMap**: overrides del usuario sobre el factory (persistidos, versionados).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con MK2 conectada, 100% de US1 verificable: play/cue/sync/pitch/vol/cross/load/browse responden <50 ms observados en UI.
- **SC-002**: Con salida 4ch, PFL A aislado en CueOut (medido en buffer, no "se oye bien"): master intacto post-cross.
- **SC-003**: Scratch sigue la mano sin saltos (delta acumulado) y suelta sin quedarse "pegado" (10/10 intentos).
- **SC-004**: Desconectar MIDI o audio USB en cualquier momento → 0 crashes en 10 ciclos conecta/desconecta.
- **SC-005**: `ctest` + `DJMIXER_AUTOTEST` + `DJMIXER_SCREENSHOT` siguen verdes (Constitución II).

## Assumptions

- MK2 concreta del usuario: USB class-compliant en macOS (MIDI + audio CoreAudio sin driver), como declara el XML.
- Stack fijo: C++17, Qt 6.5, miniaudio existente, RtMidi como única dependencia nueva (MIT, justificada en plan).
- XMLs de Serato son referencia local (`<tmp local>`, `referencia-serato/` (no publicado)) y nunca se commitean (Constitución III).
- EQ/FX/sampler/stems de la MK2 quedan en reserva (no hay DSP aún): se parsean, no se actúan.
- Solo lectura de archivos del usuario; mappings de usuario en `QSettings`, no en el repo.
