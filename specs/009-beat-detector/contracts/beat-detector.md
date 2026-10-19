# Contracts: Beat Detector + PhaseMeter (C++ ⟷ QML)

## BeatDetector (por deck, hilo audio)

| Miembro | Forma | Descripción |
|---|---|---|
| `process(const float *samples, int n, double srcPos0)` | llamada en `render()` | alimenta el detector; O(1), sin `new`/mutex |
| `lastBeatPosition()` | `std::atomic<double>` | posición (seg) del último beat, leída por UI |

## Deck (extensión)

| Miembro | Uso |
|---|---|
| `Q_PROPERTY(double lastBeatPosition READ lastBeatPosition NOTIFY ...)` | expone el beat detectado a QML |

## PhaseMeter (hilo UI)

| Miembro | Forma | Descripción |
|---|---|---|
| `offsetMs()` | `double` | `wrap(beatB − beatA, período)` en ms; `NoBeat` → 0 |
| `state()` | `int` | `0=NoBeat 1=InSync 2=Zapateo` |
| `setDecks(Deck *a, Deck *b)` | slot | fuentes |

## Reglas de threading (contrato duro)

1. `BeatDetector::process()` corre SOLO en el hilo de audio.
2. `PhaseMeter` corre SOLO en el hilo UI (QTimer ~50 ms), leyendo atómicos.
3. El detector no depende de la beatgrid: mide la señal, no el análisis.
