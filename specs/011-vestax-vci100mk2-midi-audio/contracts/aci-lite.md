# ACI-lite: subset soportado en el MVP MK2

Fuente de nombres: `midi_vestax_vci_100_mk2.xml` (referencia local) +
slots existentes `Deck/Mixer/SyncEngine/TrackListModel`.

## Activos (MVP)

| ACI-lite | Origen MK2 | Destino dj-mixer |
|---|---|---|
| `play` | Note 34 ch1/2 + output | `Deck::play/pause` (toggle) |
| `cue_play` | Note 66 ch1/2 + output | `cuePressed/cueReleased` |
| `previous_track` | Note 67 ch1/2 | `seek ∓5s` provisional |
| `platter_touch` | Note 59 ch1/2 | `scratchGrab/Release` |
| `platter_move` | CC16 ch1/2 relativo | `scratchTo` o bend |
| `sync` / `sync_off` | Note 36 / 68 + output | `SyncEngine::setSync` |
| `pitch_slider` | ch1-CC27 / ch2-CC17 (+shift CC30) | `userSetPitch` ±8% |
| `crossfader` | ch5-CC16 | `Mixer::setCrossfade` |
| `upfader` | ch1-CC28 / ch2-CC22 | `Deck::setVolume` |
| `master_volume` / `cue_gain` / `cue_mix_crossfader` | ch5-CC20/18/19 | bus master/cue (F-A2) |
| `pfl` | Note 54 + output | bus cue |
| `load_track` | Note 55 | `loadFile(selección)` |
| `library_scroll` | ch5-Note55/56 | `TrackListModel` select |
| `modifier_1/2`, `deck_activate` | ch5-Note36/52, Note52/53 | conditions (shifts) |

## Reservados (parseados, no actuados: sin DSP aún)

`keylock`, `pitch_range`, `trim`, `deck_eq_hi/mid/lo`,
`deck_filter_frequency`, `cue_point*`, `auto_loop_*`, `loop_length_*`,
`beat_jump`, `shift_loop`, `effect_*`, `tab_library`, `video_*`.
