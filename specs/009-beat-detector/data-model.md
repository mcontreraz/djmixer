# Data Model: Real-time Beat Detector + Zapateo

## BeatDetector (por deck, estado volátil)

| Miembro | Tipo | Rol |
|---|---|---|
| `m_lowpass` | Biquad/1-pole | aísla graves (~250 Hz) |
| `m_hopEnergy` | float | energía acumulada del hop actual |
| `m_hopCount` | int | muestras del hop actual |
| `m_prevEnergy` | float | energía del hop anterior (para el flujo) |
| `m_recent[]` | ring fijo (N) | flujos recientes para el umbral |
| `m_lastBeatPos` | `std::atomic<double>` | posición (seg de fuente) del último beat |
| `m_lastBeatHop` | uint64 | hop del último beat (refractory) |
| `m_hopPos` | double | posición fuente del hop actual |

Métodos: `process(float *samples, int n, double srcPos0)` (hilo audio),
`double lastBeatPosition() const` (UI).

## PhaseMeter (comparador, hilo UI)

| Miembro | Tipo | Rol |
|---|---|---|
| `m_detA`, `m_detB` | `BeatDetector*` | fuentes |
| `offsetMs()` | double | `wrap(beatB − beatA, período)` en ms |
| `state()` | enum | `{NoBeat, InSync, Zapateo}` |

## Invariantes

- `BeatDetector` solo lo escribe el hilo de audio; `lastBeatPosition` es atómico
  y lo lee la UI sin locks.
- Sin `new`/mutex/I-O dentro de `process()` (Constitución I).
- `PhaseMeter` corre en el hilo UI (QTimer), leyendo atómicos.
- El período de referencia para envolver es el del deck A (maestro); si no hay
  beats en A, `NoBeat`.
