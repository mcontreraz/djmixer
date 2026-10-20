# Tareas: Franja MIXER completa (EQ + Filtro + Gain)

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Spec**: `specs/014-mixer-strip/spec.md` · **Plan**: `specs/014-mixer-strip/plan.md`

## Fase 0 — EQ propio (referencia: DSP del otro agente)

- [ ] T001 Biquad RBJ lowShelf/peakingEq/highShelf reimplementados
      (identidad exacta en 0 dB)
- [ ] T002 `Deck`: `eqLow/eqMid/eqHigh` + `applyEq` post-resample con
      suavizado y bypass bit-exacto
- [ ] T003 `eq_dsp_test.cpp` (no publicado) reimplementado (respuesta, identidad,
      barrido sin clicks)

## Fase 1 — DSP (filtro + gain)

- [ ] T004 `Deck`: `filterAmount` (−1..+1) y `channelGain` (0..2) — Q_PROPERTY,
      setters atómicos + notify (`deck.h/.cpp` (no publicado))
- [ ] T005 `Deck::applyFilter`: LP+HP suavizado post-EQ (cutoff log por signo,
      Q 1.0, bypass |amount|<0.5%, ramp de coeficientes por muestra)
- [ ] T006 `Deck::render`: cadena EQ → filtro → meter → gain (ramp corto del
      gain por bloque)
- [ ] T007 `filter_dsp_test.cpp` (no publicado) (ctest `filter_dsp`): respuesta LP/HP,
      bypass bit-exacto, barrido sin clicks, gain 0/2×
- [ ] T008 `ctest` verde (suite completa) antes de tocar UI

## Fase 2 — UI (Knob + MixerStrip)

- [ ] T009 `components/Knob.qml` funcional: drag vertical, doble clic = default,
      ToolTip, teclado, pintado dependiente de `value`
- [ ] T010 `MixerStrip.qml`: fila HI/MID/LOW + fila GAIN/FILTRO por canal,
      bindings a `deck.eq*` / `filterAmount` / `channelGain`
- [ ] T011 Ajuste de altura de la franja y orden de filas según captura del
      mockup (confirmar con el usuario)
- [ ] T012 Verificación manual: giro audible de EQ/filtro, gain recorta,
      doble clic resetea, vúmetro post-EQ

## Fase 3 — Cierre

- [ ] T013 `ctest` completo verde + `waveform_scratch_test` sin empeorar
- [ ] T014 Captura de la franja MIXER (`DJMIXER_SCREENSHOT`) como evidencia
- [ ] T015 Merge de `014-mixer-strip` a `main` cuando esté verde

## Dependencias

T001 → T002 → T003 (EQ propio); T004 → T005 → T006 → T007/T008 (filtro+gain);
T009 → T010 → T011/T012 (UI tras T008); T013–T015 al final.
