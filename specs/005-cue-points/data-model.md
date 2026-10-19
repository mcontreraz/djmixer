# Data Model: Cue Points (CDJ)

## CuePoint (en memoria, por Deck)

| Campo | Tipo | Reglas |
|---|---|---|
| `position` | f64 segundos | `0 ≤ position ≤ duration` al guardar; se clampéa |
| `valid` | bool | `false` = sin cue (tema fresco o corrupto) |

Transiciones: `invalid --(set en pausa)--> valid` · `valid --(clear en nueva carga)--> invalid` ·
`valid --(nueva carga mismo archivo con sidecar)--> valid` (persistido).

## Persistencia (disco)

Archivo `<CacheLocation>/waveforms/v1/<clave>.cuepoint`: texto con un double
(segundos). Misma clave que `.wfcache` (ruta|tamaño|mtime) → invalidez gratis.
Escritura solo en `set` (no por frame, no en preview).

## HotCue[8] (por Deck)

| Campo | Tipo | Reglas |
|---|---|---|
| `slots[8]` | f64, `-1` = vacío | `0 ≤ valor ≤ duration` al guardar |
| fichero | `<clave>.hotcues` | líneas `índice segundos`; se reescribe entero en set/clear |

## Deck (extensión)

| Miembro | Rol |
|---|---|
| `cuePosition` (prop, f64) + `cueValid` (prop, bool) | estado leído por QML |
| `cuePressed()` / `cueReleased()` (slots) | semántica CDJ completa |
| `previewing` (interno) | distingue release-tras-preview de tap |
