# Quickstart: Waveform Heatmap

Valida F2 de punta a punta. Prerrequisito: build Release con
`DTOOLS`: ninguno (solo Qt + miniaudio vendorizado).

## 1. Análisis real al cargar

```bash
cmake --build build -j
DJMIXER_SCREENSHOT=/tmp/f2-wave.png ./build/djmixer.app/Contents/MacOS/djmixer
```

Carga el WAV de prueba (doble-click → deck 1, ▶). Esperado (SC-001/SC-002):
el overview del deck 1 muestra forma real (no la sintética anterior) y el
play/pausa responde al instante durante el análisis.

## 2. Heatmap estable

Compara `/tmp/f2-wave.png` con una captura previa del mismo tema:
misma forma y colores salvo el playhead (SC-004).

## 3. Caché instantánea (SC-003)

Recarga el mismo tema y cronometra: overview completo en <300 ms
(segunda carga no re-analiza; verifica el `.wfcache` en
`~/Library/Caches/<bundle>/waveforms/v1/`).

## 4. Degradación limpia (SC-005)

Carga un `.txt` renombrado a `.wav`: el deck sigue operativo con overview
vacío y hay mensaje en log, sin crash.

## 5. Autotest extendido

`DJMIXER_AUTOTEST=<wav>` debe seguir en exit 0 (posición/duración/nivel)
más aserción nueva: existe sidecar `.wfcache` tras la corrida.
