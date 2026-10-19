# Contracts: Waveform Heatmap (QML ⟷ C++)

Interfaz pública que el motor expone a la UI. Todo acceso desde QML respeta
constitución I (solo lectura de propiedades + señales; ningún slot bloqueante).

## WaveformCache (QObject, instanciado por Deck)

| Miembro | Forma | Descripción |
|---|---|---|
| `ready` | `Q_PROPERTY bool READY NOTIFY readyChanged` | `true` cuando hay buckets válidos |
| `bucketCount` | `Q_PROPERTY int` | nº de buckets overview (256) |
| `detailCount` | `Q_PROPERTY int` | nº de buckets detalle (4096, 0 en cachés viejas) |
| `bucketAt(i)` | `Q_INVOKABLE: {min,max,r,g,b}` | lectura puntual overview |
| `detailAt(i)` | `Q_INVOKABLE: {min,max,r,g,b}` | lectura puntual detalle (US2) |
| `readyChanged()` | señal | se emite en hilo UI al completar/cancelar |

## Deck (extensión)

| Miembro | Forma | Descripción |
|---|---|---|
| `waveform` | `Q_PROPERTY WaveformCache* READY NOTIFY waveformChanged` | caché del tema cargado o nulo |
| `waveformChanged()` | señal | nueva carga o caché lista |

## WaveformView (QML)

- Propiedad nueva `cache: WaveformCache` (puede ser nula → dibuja fondo vacío,
  nunca la simulación vieja).
- Mantiene `playhead`, `beatStart`, `overview` existentes; elige nivel
  (overview/detalle) por ancho disponible.

## Reglas de threading (contrato duro)

1. El worker nunca emite directo a QML: entrega por `queued connection`.
2. `bucketAt()` solo se llama con `ready == true`.
3. Cancelar = bump de `analysisGeneration`; el worker aborta y destruye su
   resultado parcial sin señalar.
