# Modelo de negocio: Lite gratis forever + Pro de pago

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

Fecha: 2026-10-19 · Documento de estrategia (no es código, no es consejo legal).

## Visión

- **Lite**: gratis para siempre, robusta y completa en lo esencial — el punto de
  entrada de cualquier DJ principiante. Es el canal de distribución, no el
  producto.
- **Pro**: de pago, con las features que un DJ pide cuando crece (stems,
  grabación, análisis armónico avanzado, DVS, mapeos de hardware, soporte
  prioritario). Emerge del mismo núcleo.
- **Comunidad y fama como dev**: el repo abierto, la historia "hecho con IA en
  1 semana" y el contenido técnico construyen la audiencia que alimenta el Pro.

Lo esencial **no** se vende: key lock, scratch continuo, análisis de
tonalidad, loops, hot cues y beatgrid son de la Lite. La lista exacta está en
[`promise.md`](promise.md), que es canónica; este documento no la cambia.

## Estado de licencia actual (hechos del repo)

- El binario actual incorpora **qm-dsp (GPL-2.0-or-later)** — detección de
  beats (DetectionFunction, DownBeat, TempoTrackV2) **y también la detección de
  tonalidad**: el análisis de key con notación Camelot usa el módulo
  `dsp/keydetection/GetKeyMode` de qm-dsp, no código propio. Se compila entero
  (`CMakeLists.txt`: `qm-dsp/**` (no publicado)) y está en uso activo en
  `qmbeatgrid.cpp` (no publicado), `waveformanalyzer.cpp` (no publicado) y `keyanalyzer.cpp` (no publicado).
- El binario actual incorpora **Rubber Band (GPL-2.0-or-later)** — es el motor
  del key lock y **el único** que se despacha hoy (`CMakeLists.txt`:
  `PkgConfig::RUBBERBAND`; `deck.h` (no publicado): `RubberBandStretcher`; `deck.cpp` (no publicado):
  construcción, `setTimeRatio` y proceso). El repo no fija versión de librería
  (la API `RubberBandStretcher` es la misma en 3.x y 4.x), así que aquí se
  nombra el motor, no un número de release.
- qm-vamp-plugins NO se compila (solo ocupa carpeta en third_party). El módulo
  de key detection que sí se usa viene de qm-dsp, no de qm-vamp-plugins.
- El resto del núcleo es propio o permisivo (miniaudio MIT-0, BeatThis MIT,
  ONNX Runtime MIT, r8brain MIT).
- Consecuencia: mientras qm-dsp o Rubber Band estén en el binario, **toda
  distribución es GPL**. Esto aplica a la Lite y a cualquier Pro derivado del
  mismo árbol.

## Fase 1 — Hoy (Lite GPL, sin tocar licencia)

La Lite se publica GPL con su código fuente. El GPL aquí **ayuda**: confianza
open source, adopción, comunidad. Vías de ingreso que no comprometen nada:

1. **SaaS de análisis de librería** (la vía principal): servidor propio que
   analiza/sincroniza la colección del usuario (grids, keys, backup). GPL-2 no
   tiene cláusula de red → ejecutar en servidor propio no es distribución →
   sin obligación de liberar. Modelo de suscripción.
2. **Contenido y hardware**: packs de loops/samples/mappings, skins, o un
   controlador MIDI configurado (modelo Serato: el software desbloquea valor,
   el contenido/hardware es el negocio).
3. **Soporte y servicios**: instalación, configuración, training para DJs pro.
4. **Donaciones/patrocinio**: GitHub Sponsors, Patreon.

## Fase 2 — Pro cerrado (requiere des-GPL)

Requisito innegociable: **el árbol del Pro debe estar 100% libre de GPL**.

- Reemplazar qm-dsp por código propio o librerías permisivas (spec 017 — la
  ruta está escrita aquí; **la spec todavía no está redactada**):
  - BPM/downbeat: BeatThis (MIT) + downbeat-tracker propio.
  - Key analysis: chroma propio + perfil Krumhansl, porque hoy el motor es el
    módulo de key detection de qm-dsp (`GetKeyMode`), no código propio.
  - Time-stretch: sustituir el motor actual **Rubber Band (GPL)** por uno
    permisivo. Hay un prototipo en la rama `004-beat-sync` (spec
    `specs/013-keylock/`, motor en `signalsmith-stretch` (no publicado), MIT),
    **fuera de `main`**: ninguna de esas rutas existe en la rama trunk, así
    que no se encuentran en el repo público. La alternativa probada es
    **Signalsmith Stretch (MIT)**;
    SoundTouch (LGPL, linkeado dinámicamente) queda como plan B.
- El key lock **no se des-GPL comprando una licencia comercial de Rubber
  Band**: la ruta del Pro *sustituye* el motor, no lo licencia. Con licencia
  comercial el árbol Pro seguiría siendo GPL por el resto de qm-dsp, y
  además cada binario del Pro tendría que traerse el código de Rubber Band.
- El núcleo queda 100% del autor → **doble licencia**:
  - **Lite** = núcleo bajo GPL (o MIT), gratis forever.
  - **Pro** = núcleo (licencia comercial propia) + features propietarias.
- El Pro NO puede derivarse del árbol Lite-GPL (ni contener modificaciones de
  archivos de qm-dsp o de Rubber Band). Se construye desde un árbol separado
  sin GPL.
- Las features Pro viven aparte: binario propietario con su propia licencia.

## El funnel Lite → Pro

1. **Aha moment en < 2 min**: cargar track, mezclar, loop — la Lite debe
   impresionar al instante y no estar mutilada en lo esencial.
2. **Paywall en la necesidad real**: análisis armónico avanzado, stems,
   grabación, DVS — nunca lo básico. El momento exacto en que el DJ principiante
   crece. El key lock es esencial y va en la Lite: no es una puerta de pago.
3. **Comunidad como moat**: Discord + roadmap votable → features priorizadas
   por los propios usuarios y betatesters del Pro.

## Riesgos y notas

- La GPL no prohíbe cobrar por binarios; obliga a entregar el source de lo
  distribuido. Vender la Lite es legal pero el moat es blando (preferido: no
  cobrarla — es el canal).
- Documento informativo; para decisiones formales de distribución confirmar
  con un abogado.

## Decisiones pendientes

- [ ] ¿Lite bajo GPL o MIT tras el des-GPL? (MIT da más control, menos
      obligaciones para forks; GPL mantiene reciprocidad.)
- [ ] ¿SaaS de análisis como primera vía de ingreso? (requiere un server)
- [ ] Features Pro concretas del primer release (prioridad 1-2-3).
- [ ] Redactar la spec 017 (des-GPL) con el flujo speckit: hoy la ruta está
      solo en prosa, en este documento y en `docs/launch-plan.md`.
