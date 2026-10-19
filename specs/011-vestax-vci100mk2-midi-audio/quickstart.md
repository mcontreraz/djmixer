# Quickstart: VCI-100MK2 MIDI + Audio

**Feature**: `011-vestax-vci100mk2-midi-audio`

## 1. Confirmar la MK2 en el sistema (sin compilar)

```sh
# MIDI: nombre exacto del puerto
python3 -c "import subprocess; print('revisar Audio MIDI Setup > Ventana MIDI: VCI-100MKII DJ-Controller')"
# Audio: el device debe aparecer con 4 outs
system_profiler SPAudioDataType | grep -A3 -i "VCI-100"
# Volcado crudo 2 min con Snoize MIDI Monitor moviendo:
# jog L/R (tocado/sin tocar), pitch, vol, cross, play, cue, sync, browse
```

## 2. Tras implementar F1 (MIDI-IN)

```sh
cmake -S . -B build -DCMAKE_PREFIX_PATH="$(brew --prefix qt)" && cmake --build build -j
./build/djmixer 2>&1 | grep -i "midi.*VCI\|port"
# Panel MIDI: auto-selecciona *VCI*, monitor hex muestra Note34/CC16 al tocar
# Play A alterna DeckA; cross ch5-CC16 mueve Mixer.crossfade 0..1
DJMIXER_SCREENSHOT=/tmp/midi.png DJMIXER_SCREENSHOT_SIZE=1580x900 ./build/djmixer
```

## 3. Tras F-A2 (audio 4ch)

```sh
# Con MK2 elegida: PFL A → CueOut lleva A, MasterOut mezcla post-cross
# Con salida Mac 2ch: todo a master (fallback), panel lo indica
ctest --test-dir build --output-on-failure
DJMIXER_AUTOTEST=/ruta/tema.wav ./build/djmixer 2>&1 | grep -i "autotest\[[12]\]"
```

## 4. Casos manuales

1. Apagar MK2 con app abierta → panel "desconectado", mouse sigue; encender → reconecta sin reiniciar.
2. Learn Sync B a botón libre → persiste tras reinicio; factory intacto.
3. "Probar LEDs" → barrido enciende/apaga Play/Cue/Sync/PFL.
4. Desconectar USB a mitad de scratch → suelta segura, 0 crashes en 10 ciclos.
