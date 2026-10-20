# Implementation Plan: Key Lock + Key Analysis

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Feature**: `016-key-lock` · **Fecha**: 2026-10-19 · [Spec](spec.md)
**Estado**: Implementado en `main` (motor Rubber Band). Fases F0–F3 cerradas;
F4 (métricas, capturas y escucha) pendiente.

> **Reconciliado con el código (2026-10-19).** Este plan describía la
> implementación de un motor WSOLA propio, que se descartó. El motor que
> despacha hoy es **Rubber Band** (GPL-2.0-or-later). La comparación de
> técnicas y el motivo del cambio están en [research.md](research.md); el
> commit que hizo el swap es `04e8de0`.

## Contexto técnico y constitución

C++17, Qt 6, miniaudio, PCM interno float estéreo a 48 kHz. Plataforma principal:
macOS arm64. **Dependencia nueva**: Rubber Band (GPL-2.0-or-later), enlazada
por pkg-config (`pkg_check_modules(RUBBERBAND REQUIRED ...)`) **sin versión
fijada** — el repo no fija la versión de la librería. La detección de key
reutiliza `qm-dsp` (GPL, ya vendido y licenciado en `third_party/` (no publicado)).

- **RT**: el motor de stretch no asigna memoria, no bloquea y no hace I/O en el
  callback; todos sus buffers son arrays miembro preasignados de `Deck` y el
  motor se construye una vez, en el constructor. El decoder/refill actual tiene
  deuda RT heredada (ver 015); esta feature la enumera pero no la exacerba en el
  path adoptado.
- **Verificación**: tests de DSP/transporte antes de habilitar el botón KEY;
  fixtures de key antes de tocar la UI.
- **Simplicidad**: un motor de stretch (Rubber Band), un toggle por deck, una
  notación de display (Camelot), una fuente de detección (GetKeyMode). Sin key
  shift, sin phase vocoder propio, sin toggle de análisis en UI en v1.
- **Claridad**: código en inglés, documentos en español, unidades explícitas.

## 1. Matemática del time-stretch

El motor es una caja negra con un contrato de dos llamadas: se le da entrada y
un ratio, devuelve salida con el pitch fijo. Lo que la app tiene que cumplir:

```text
timeRatio = 1 / rate          # duración salida / duración entrada
latencia  = getLatency()      # del motor, medida al construir el deck
                             # 1024 muestras ≈ 21.3 ms a 48 kHz
```

`timeRatio` va invertido a propósito: para reproducir **más** rápido
(`rate > 1`) la salida dura menos, luego `1/rate`. Invertirlo hacía que subir el
pitch expandiera el tiempo.

**Alimentación sin drift**: el motor consume a `timeRatio`, así que la entrada
que hay que darle depende de la salida pedida. Se lleva un acumulador doble
(`m_klInNeeded` / `m_klInFed`): en cada bloque se calcula

```text
m_klInNeeded += frameCount * rate
feedN = m_klInNeeded - m_klInFed   # frames de fuente que hay que darle
```

y se alimenta exactamente esa cantidad. El promedio converge a
salida × tasa, sin deriva acumulativa de posición (tolerancia de un hop).

**Extracción sin dropouts**: el motor devuelve 0 si se pide más de lo que hay.
Antes de `retrieve` se consulta `available()` y se pide como máximo lo
disponible; si aun así no hay suficiente, el resto del bloque se llena de
silencio (nunca se repite audio viejo).

**Sin conmutación de camino**: con KEY **ON** el motor queda **siempre** en el
camino, incluso a `rate == 1.0`. Cruzar el 0 del pitch es solo el ratio
pasando por 1.0 dentro del motor. Una banda de conmutación alrededor de rate 1
se probó y se descartó: producía dos cambios de camino con sus artefactos de
latencia. Con KEY **OFF** la salida es el remuestreo lineal de siempre, bit a
bit.

**Crossfade de toggle**: 1024 frames (≈ 21.3 ms a 48 kHz) de rampa propia,
simétrica, al entrar y al salir. El motor queda "siempre caliente": se sigue
alimentando aunque esté apagado y su salida se descarta, para que encender KEY
(o cruzar el 0 del pitch) no produzca un hueco.

**Compensación de fase**: el motor entrega el contenido `latencia` por detrás
del cursor de fuente. La fase que se publica para sync es la **audible**
(`cursor − rate × latencia`), para que un deck con KEY y otro sin KEY se
comparen en la misma moneda.

El beat detector en vivo (`m_beatDetector`) sigue alimentándose con el buffer
de salida en tiempo de fuente (igual que hoy), sin cambios de contrato.

## 2. Pipeline de key analysis

Al finalizar el decode en `WaveformAnalyzer::analyze` (ya tiene `monoBuf` mono
f32 y `sampleRate`):

```text
monoBuf (mono f32, ≤ 2^26) --(GetKeyMode, A=440)--> índice 0..24
índice --(tabla Camelot propia)--> "1A".."12B"  +  confianza (max correlación)
confianza < 0.5  -->  analyzedKey = ""  (sin key)
```

El detector vive en `keyanalyzer.cpp` (no publicado) (envuelve `qm-dsp GetKeyMode`) y la
tabla Camelot en `keynotation.h` (no publicado). Corre en el hilo del analyzer, nunca en el
callback de audio.

Precedencia de display (FR-014): `meta.key = tagKey ? tagKey : analyzedKey`,
y `meta.keySource ∈ {Tag, Analysis, None}`. `TrackMeta` se extiende con
`analyzedKey` y `keySource`; `WaveformCache::save/load` persisten la extensión
con revisión de meta versionada (las revisiones viejas de grid sobreviven a la
regeneración visual, igual que en 015).

Mapeo Camelot (referencia de teoría musical, tabla propia): 1=B♭ mayor, 2=F,
3=C, 4=G, 5=D, 6=A, 7=E, 8=B, 9=F♯, 10=D♭, 11=A♭, 12=E♭; los menores son la
relativa (p. ej. `8A` = A menor, relativa de C mayor = `8B`). La tabla exacta
índice→Camelot está en `keynotation.h` (no publicado) con su test de biyección (SC-005).

## 3. Integración en `Deck::render` (path normal)

El bloque actual del path normal (remuestreo lineal frame a frame) se bifurca
según el flag atómico `m_keyLock`:

```text
if (!m_keyLock)  -> path lineal actual (bit a bit)
else             -> motor de stretch: process() + retrieve()
```

`Deck` mantiene el estado del camino de key lock: acumuladores de entrada,
contador de crossfade, buffers preasignados (`m_klInL/R`, `m_klOutL/R`,
`m_klFadeBuf`, `m_klLoopIn`) y la latencia medida (`m_klLatencyOut`).
`m_playedFrames` avanza igual que en el path directo (el tiempo fuente no
cambia); solo cambia cómo se interpola. `discardConsumed` y el beat detector se
mantienen. Scratch usa su propio camino (`renderScratchRange`), sin tocar el
motor.

El path de loop (`m_loopTransport.render`) tiene su propia rama de key lock: la
ventana del loop se lee a `rate=1.0` (raw) y se alimenta al motor, que produce
el bloque audible.

## 4. Estado y UI

`Deck` expone `Q_PROPERTY(bool keyLock ...)` + slot `setKeyLock(bool)`. El flag
viaja UI→audio por atómico; la señal `keyLockChanged` se emite en el hilo de UI
al conmutar (no hay un snapshot desde el hilo de audio: el motor no puede
fallar en un toggle). El botón KEY de `DeckPanel.qml` (ya stubbed como
`property bool keyLock`) está cableado al slot. El badge de key y `keyColorFor`
ya existen; solo se alimentan con el key analizado.

## 5. Verificación

1. Oráculos de pitch (seno 480 Hz), bypass y latencia del motor.
2. Motor de stretch preasignado + integración en render + toggle con crossfade.
3. Botón KEY/estado + display Camelot (deck y biblioteca).
4. Detección GetKeyMode + mapeo + caché + fixtures.
5. Regresión completa, métricas, capturas y escucha.

## Decisiones de diseño

1. **Rubber Band** (GPL) como motor de stretch, en modo real-time con
   transientes mixtos: es el motor probado en mezcla real y el que usa Mixxx.
   El WSOLA propio se prototipó y se descartó por su comportamiento en
   transientes (`04e8de0`).
2. **Motor siempre en el camino** con KEY ON: sin banda de conmutación, sin
   artefactos de latencia al cruzar el 0 del pitch.
3. **Crossfade propio de 1024 frames** simétrico al entrar y al salir.
4. **Detección sobre `monoBuf`** con GetKeyMode, sin segundo decode.
5. **Precedencia tag > análisis**; `keySource` explícito y cacheado.
6. **Fuera de v1**: key shift y key lock en scratch.

## Registro de preguntas

| Pregunta | Criterio propuesto (a confirmar) |
|---|---|
| Latencia máxima | ≤ 40 ms; medido 21.3 ms (1024 muestras @48 kHz) |
| Calidad objetivo | Transparente a rate≈1; artefactos tolerables a 0.5–1.5 en música de mezcla |
| Crossfade de toggle | 1024 frames (≈21.3 ms); ¿confirmar duración/curva? |
| Umbral de confianza de key | 0.5 (implementado); ¿confirmar? |
| Key lock × loop | Resuelto en v1: el motor aplica dentro del loop |
| Key shift (±12 semitonos) | ¿Parte de esta feature o de una posterior (MixerStrip `KEY`)? |

Cada fase depende de los tests anteriores. Un gate fallido no se resuelve
bajando la tolerancia ni deshabilitando el detector de beats.
