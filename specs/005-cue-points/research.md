# Research: Cue Points (CDJ)

## Decisión 1: Semántica exacta del botón (estándar CDJ)

- **Decision**: tres casos. (a) Sonando + press → `seek(cue)` + `pause` (return).
  (b) Pausado + press → guarda `cue = position`, `play` (preview). (c) Release
  tras (b) → `seek(cue)` + `pause`. Un click rápido en pausa = set + micro-preview.
- **Rationale**: es el comportamiento documentado Pioneer (cue return / cue
  sampler / set). Todo con slots existentes.
- **Alternatives considered**: click = set sin preview (rechazado: no es CDJ).

## Decisión 2: Press vs click en QML

- **Decision**: el botón redondo CUE usa `onPressed`/`onReleased` (+`onCanceled`
  como release). Distinguir tap de hold no hace falta: la semántica de arriba
  cubre ambos (tap en pausa = set + preview brevísimo).
- **Rationale**: `onClicked` no distingue mantener; el release fuera del botón
  debe volver igual (grab del mouse de Qt lo garantiza mientras se mantiene).
- **Alternatives considered**: temporizador tap-vs-hold (rechazado: complejidad
  sin valor, el CDJ real tampoco distingue).

## Decisión 3: Dónde persiste el cue

- **Decision**: archivo texto `<clave>.cuepoint` junto a los `.wfcache`
  (misma clave sha1 → misma invalidez ante cambios del archivo).
- **Rationale**: sin migraciones ni formato binario; debuggeable con `cat`;
  se lee al cargar si existe, se escribe al guardar (throttle: solo en set,
  no por frame).
- **Alternatives considered**: columna en el `.wfcache` (acopla dato de usuario
  con caché regenerable; bump de versión innecesario); QSettings global
  (pierde la invalidez por mtime).

## Decisión 4: Marca visual

- **Decision**: `WaveformView.cueTime` (segundos, −1 = sin cue): línea + etiqueta
  en overview (fracción) y en scroll (tiempo absoluto). El cuadradito orbital
  NO vuelve como giratorio: la marca es fija en la posición del cue.
- **Rationale**: cumple la promesa del square como marca de cue.
- **Alternatives considered**: marcador arrastrable (es edición de cue con
  drag = scratch-ish; fuera, F3/M4).

## Decisión 5: Preview y el hilo de audio

- **Decision**: preview = `play()` normal; no hay ruta de pre-escucha separada
  (bus cue-mix = F3). El estado `previewing` solo evita re-sets accidentales.
- **Rationale**: constitución I y IV (cero cambios en `render()`).
