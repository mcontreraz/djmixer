# Mixer: controles y respuesta de audio

Referencia de interacción: Pioneer DJM-900NXS2, modo Isolator. Esta es una
implementación propia; no reproduce coeficientes ni curvas medidas del equipo.
El [manual de Pioneer](https://www.magnum.fr/download/materiel_manuels/pioneer_djm-900nxs2_manual_EN.pdf)
describe EQ/Isolator, refuerzo máximo de +6 dB y filtro COLOR con LP hacia la
izquierda y HP hacia la derecha. No publica los cruces ni los coeficientes DSP.

- Isolator: cruces propios en 250 Hz y 2.5 kHz, Linkwitz–Riley de 24 dB/octava.
  Compensación de fase entre bandas: respuesta plana al centro, sin cambiar
  de ruta al mover una perilla. El estado neutro conserva la magnitud, pero
  aplica la fase del crossover; no es un bypass bit a bit.
- Rango: silencio por banda en el extremo izquierdo, 0 dB al centro y +6 dB
  a la derecha. En el tramo de corte, el recorrido controla ganancia lineal;
  el tooltip muestra los dB reales. El mínimo interno de −60 dB representa
  corte total (−∞). Las ganancias se suavizan durante 4 ms.
- Filtro: dos secciones por rama, 24 dB/octava, Q fijo de 0.85 por sección.
  Barrido logarítmico LP de 20 kHz a 20 Hz y HP de 20 Hz a 20 kHz.
  Centro neutro con zona de ±0.005. Cada rama mantiene su propio suavizado
  para no heredar el cutoff de la otra al cambiar de lado. Estos valores
  son ajustes propios, no especificaciones publicadas de Pioneer.
- Vúmetros de canal y master: umbrales de −54 a 0 dBFS; rojo solo en 0 dBFS.
  Los picos de canal incluyen trim y EQ/filtro. Se conserva la selección
  existente entre nivel post-fader y preescucha. La sensibilidad visual no
  aumenta la ganancia de audio.
- Faders: carril y tirador con los colores, marcas y dimensiones del pitch
  de la app. Se conserva el rango de volumen y la mezcla del crossfader.

Validación: `ctest --test-dir build --output-on-failure`. Las pruebas cubren
respuesta en frecuencia y cruces, corte de las tres bandas, barridos y cambios
de signo del filtro, medición post-trim, interacción QML y escala del vúmetro.
