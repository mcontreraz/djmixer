# Data Model: VCI-100MK2 MIDI + Audio

**Feature**: `011-vestax-vci100mk2-midi-audio` | **Date**: 2026-10-15

## Binding (unidad del motor; genérica para los 208 MIDI futuros)

```text
Binding {
  channel: u4          // 1-4 decks, 5 global (MK2). Se conserva tal cual del XML
  control: u7          // nº CC o nota
  eventType: enum { NoteOn, ControlChange }
  action: AciLite      // p.ej. play, cue_play, platter_touch/move, pitch_slider,
                       // sync/sync_off, crossfader, upfader, pfl, load_track, library_scroll
  deckId: i8           // 0-3 (usamos 0-1); -1 = global
  deckSet: string      // "Default" | "DJ Effects" (solo documentado)
  conditions: ModifierRef[] // modifier_1/2, deck_activate (shift layers)
  translation: {
    kind: enum { toggle_on_down, explicit_range, relative_center_0x40 }
    range?: { inMin, inMax, outMin, outMax }  // faders, jog→library
    deadzone?: u7
    reversed?: bool
    jogGain?: float                            // solo platter_move
  }
  output: { feedback: bool, onValue: 127, offValue: 0 } // LED misma nota
}
```

Invariante: un `Binding` nunca pierde `conditions[]` ni `translation` al
convertir XML→JSON (no reducir a botón→función).

## DeviceDescriptor (identificación + capacidades)

```text
DeviceDescriptor {
  vendorId: 0x1AA1; productId: 0x0220
  midiName: "VCI-100MKII DJ-Controller"
  audioName: "VCI-100MKII DJ-Controller"  // mac CoreAudio
  numDecks: 4            // usamos decks 0,1
  initSysEx: F0 7E 00 06 01 F7
  midiMappable: true
}
```

## AudioRoute (buses; vale para toda Vestax: MasterOut+CueOut)

```text
AudioRoute {
  deviceName: string     // exacto miniaudio/CoreAudio
  outs: { master: ch[0,1], cue: ch[2,3] }   // 4ch; 2ch => cue=master (fallback)
  ins: { aux: ch? }                         // Aux1In reservado (grabación futura)
  cue: { type: PER_CHANNEL_CUE, pfl[deck]: bool, gain, mix }
}
```

`Mixer.process` futuro: `master = Σ deck*upfader*trim*cross(eq)`,
`cue = Σ pflDeck*cueGain (+ master*cueMix según mix)`.

## UserMap (overrides; lo único que Learn modifica)

```text
UserMap {
  base: "vestax_vci100mk2.json@1",
  overrides: Binding[],   // por (channel,control,eventType)
  lastPort: string, lastAudioDevice: string
}
```

Relaciones:

```text
RtMidiIn ──msg──▶ UserIoEngine.match(channel,control,ev,modifiers)
   ──hit──▶ emit ACI-lite ──Queued──▶ Deck/Mixer/SyncEngine/TrackListModel slots
   ◀──state── MidiOut.send(note,127/0) suscrito a playingChanged/cueChanged
miniaudio ──deviceName──▶ AudioRoute ──▶ Mixer buses master/cue
assets/midi/*.json ──carga──▶ presets (MK2 primero; N después sin tocar C++)
```
