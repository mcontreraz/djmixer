# Implementation Plan: Key Lock + Key Analysis

**Feature**: `016-key-lock` · **Fecha**: 2026-10-19 · [Spec](spec.md)
**Estado**: Plan preparado; ninguna fase de implementación ejecutada.

## Contexto técnico y constitución

C++17, Qt 6, miniaudio, PCM interno float estéreo a 48 kHz. Plataforma principal:
macOS arm64. Sin dependencias nuevas: WSOLA se implementa en casa (header-only,
como `looptransport`); la detección reutiliza `qm-dsp` (GPL, ya vendido y
licenciado en `third_party/`).

- **RT**: el stage de stretch no asigna memoria, no bloquea y no hace I/O en el
  callback; todos los buffers se reservan al cargar la pista. El decoder/refill
  actual tiene deuda RT heredada (ver 015); esta feature la enumera pero no la
  exacerba en el path adoptado.
- **Verificación**: tests de DSP/transporte antes de habilitar el botón KEY;
  fixtures de key antes de tocar la UI. Esta entrega es documentación.
- **Simplicidad**: un modo de stretch (WSOLA), un toggle por deck, una notación
  de display (Camelot), una fuente de detección (GetKeyMode). Sin key shift, sin
  phase vocoder, sin toggle de análisis en UI en v1.
- **Claridad**: código en inglés, documentos en español, unidades explícitas.

## 1. Matemática del time-stretch

Sea `Fs=48000`, `rate ∈ [0.4, 1.6]` (clamp del motor), hop de análisis `Ha`
(frames fuente) y ventana de búsqueda `±Δ` (frames fuente):

```text
Hs = Ha * rate                    # hop de síntesis (frames de salida)
latencia ≈ (Ha + Δ + L_xfade) / Fs  # ≤ 40 ms por FR-004
```

El stage consume frames fuente del anillo `m_src` (ya existente en `Deck`) y
produce `frameCount` frames de salida con pitch fijo:

1. Extraer el siguiente grano de análisis de longitud `N` (múltiplo de `Ha`) en
   la posición fuente actual.
2. Buscar en `[−Δ,+Δ]` el offset `k*` que maximiza la correlación cruzada
   normalizada con el grano anterior (en su zona de solape).
3. Crossfadear el solape con ventana equal-power (raíz de Hann) y escribir en
   la salida.
4. Avanzar el cursor fuente `Ha` por grano; el cursor de salida avanza `Hs`.

**Bypass**: si `rate == 1.0`, se salta el stage y se usa el remuestreo lineal
actual (identidad bit a bit). **Banda ε**: si `|rate−1| < ε`, el offset `k*` es
~0 y el solape es mínimo; opcionalmente se conmuta a interpolación lineal con
rampa corta para evitar todo flanger.

El beat detector en vivo (`m_beatDetector`) sigue alimentándose con el buffer de
salida en tiempo de fuente (igual que hoy), sin cambios de contrato.

## 2. Pipeline de key analysis

Al finalizar el decode en `WaveformAnalyzer::analyze` (ya tiene `monoBuf` mono
f32 y `sampleRate`):

```text
monoBuf (mono f32, ≤ 2^26) --(GetKeyMode, A=440)--> índice 0..24
índice --(tabla Camelot propia)--> "1A".."12B"  +  confianza (max correlación)
confianza < umbral  -->  analyzedKey = ""  (sin key)
```

Precedencia de display (FR-014): `meta.key = tagKey ? tagKey : analyzedKey`,
y `meta.keySource ∈ {Tag, Analysis, None}`. `TrackMeta` se extiende con
`analyzedKey` y `keySource`; `WaveformCache::save/load` persisten la extensión
con revisión de meta versionada (las revisiones viejas de grid sobreviven a la
regeneración visual, igual que en 015).

Mapeo Camelot (referencia de teoría musical, tabla propia): 1=B♭ mayor, 2=F,
3=C, 4=G, 5=D, 6=A, 7=E, 8=B, 9=F♯, 10=D♭, 11=A♭, 12=E♭; los menores son la
relativa (p. ej. `8A` = A menor, relativa de C mayor = `8B`). La tabla exacta
índice→Camelot se fija en F3 con su test de biyección (SC-005).

## 3. Integración en `Deck::render` (path normal)

El bloque actual del path normal (remuestreo lineal, `src/deck.cpp:1414–1445`)
se bifurca:

```text
if (!keyLock || rate == 1.0)  -> path lineal actual (bit-exact)
else                          -> KeylockStage::process(m_src, rate, out, frameCount)
```

`KeylockStage` mantiene: anillo de entrada (vista sobre `m_src` + historial),
grano anterior, buffer de correlación y tabla de ventana — todo preasignado.
`m_playedFrames` avanza `rate` por frame exactamente igual (el tiempo fuente no
cambia); solo cambia cómo se interpola. `discardConsumed` y el beat detector se
mantienen. Scratch usa su propio camino (`renderScratchRange`), sin tocar el
stage.

## 4. Estado y UI

`Deck` expone `Q_PROPERTY(bool keyLock ...)` + slot `setKeyLock(bool)`. El flag
viaja UI→audio por atómico y se confirma audio→UI por snapshot (mailbox/seqlock,
como `loopSnapshot`). El botón KEY de `DeckPanel.qml` (ya stubbed como
`property bool keyLock`) se cablea al slot; el LED solo se enciende con
confirmación del motor. El badge de key y `keyColorFor` ya existen; solo se
alimentan con el key analizado.

## 5. Verificación

1. Oráculos de pitch (seno 440 Hz + patrón rítmico), bypass bit-exacto y
   latencia; instrumentación RT.
2. Stage WSOLA preasignado + integración en render + toggle con crossfade.
3. Botón KEY/estado + display Camelot (deck y biblioteca).
4. Detección GetKeyMode + mapeo + caché + fixtures.
5. Regresión completa, métricas, capturas y escucha.

## Decisiones de diseño

1. **WSOLA** (correlación + equal-power) sobre phase vocoder: RT y latencia.
2. **Bypass exacto** a `rate==1` y banda ε anti-flanger cerca de rate 1.
3. **Crossfade de toggle** ≤ ~10 ms entre bypass y stretch.
4. **Detección sobre `monoBuf`** con GetKeyMode, sin segundo decode.
5. **Precedencia tag > análisis**; `keySource` explícito y cacheado.
6. **Fuera de v1**: key shift, key lock en loop y en scratch.

## Registro de preguntas

| Pregunta | Criterio propuesto (a confirmar) |
|---|---|
| Latencia máxima | ≤ 40 ms (FR-004); ¿aceptable 20–30 ms con `Ha=10ms, Δ=10ms`? |
| Calidad objetivo | Transparente a rate≈1; artefactos tolerables a 0.5–1.5 en música de mezcla |
| Crossfade de toggle | ≤ ~10 ms; ¿confirmar duración/curva? |
| Umbral de confianza de key | Rechazar "sin key" bajo umbral; ¿valor concreto (p. ej. correlación < 0.5)? |
| Key lock × loop (fase futura) | ¿Prioridad de key lock dentro de loops activos? |
| Key shift (±12 semitonos) | ¿Parte de esta feature o de una posterior (MixerStrip `KEY`)? |

Cada fase depende de los tests anteriores. Un gate fallido no se resuelve
bajando la tolerancia ni deshabilitando el detector de beats.
