# Tareas: EQ de 3 bandas (HI/MID/LOW)

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

**Spec**: `specs/013-eq-3-bandas/spec.md` · **Plan**: `specs/013-eq-3-bandas/plan.md`

## Fase 1 — DSP (C++)

- [x] T001 `Biquad::lowShelf/peakingEq/highShelf` (RBJ) en `audioformat.h` + `waveformanalyzer.cpp`; identidad exacta con 0 dB
- [x] T002 `eq_dsp_test.cpp` (no publicado): respuesta de las 3 bandas ±12 dB a 50 Hz / 1 kHz / 16 kHz (SC-001) + identidad (SC-002)
- [x] T003 `Deck`: props `eqLow/eqMid/eqHigh` (atomic, −12..+12) + notify; setters desde UI
- [x] T004 `Deck::render`: aplicación LOW→MID→HIGH post-resample, pre-pico; bypass cuando plano
- [x] T005 Suavizado ~30 ms (τ=4 ms + lerp de coeficientes por muestra); test de saltos de muestra (SC-003)

## Fase 2 — UI

- [ ] T006 `Knob.qml` funcional: drag vertical, doble clic = 0 dB, ToolTip dB, teclado, pintado dependiente de `value`
- [ ] T007 `MixerStrip.qml`: fila HI/MID/LOW por canal arriba del fader, binding a `deck.eq*`
- [ ] T008 Verificación manual: giro audible en vivo, reset, vúmetro post-EQ

## Fase 3 — Opcional (P3)

- [ ] T009 Kill/ISO al tope izquierdo por banda (decidir curva y umbral)

## Cierre

- [ ] T010 `ctest` completo: nuevos tests verdes; `waveform_scratch_test` sin empeorar (falla de píxeles preexistente)
- [ ] T011 Quickstart de la spec + actualizar docs si aplica
- [ ] T012 Merge de `013-eq-3-bandas` a `main` cuando esté verde
