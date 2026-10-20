# El compromiso de DJMixer

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

Fecha: 2026-10-19 · Documento normativo del proyecto (no es código, no es
consejo legal).

Este documento fija el compromiso público del proyecto. Es la referencia
canónica: el `FUNDING.md`, los anuncios y el README deben decir lo mismo que
este texto. Si alguna vez se contradicen, manda este documento.

## 1. Lite: gratis para todo el mundo, para siempre

**La versión Lite de DJMixer se lanza gratis para todo el mundo y lo seguirá
siendo. No hay precio, no hay cuota, no hay suscripción, no hay trial que
vuelva, no hay "gratis hasta que crezcas".**

Esto no es una promoción de lanzamiento. Es la razón de existir del proyecto:
que cualquier DJ que quiera ser DJ pueda empezar su carrera sin pagar
mensualidades ni comprar software caro.

En la Lite, de forma permanente y sin condiciones:

- Cargar y reproducir pistas
- Dos decks y crossfader
- Pitch / tempo con pitch-bend (±8/16/32 %)
- Key lock y análisis de tonalidad
- Scratch continuo
- Loops y hot cues
- Detección de beats, beatgrid y sync
- Waveform y biblioteca
- Mapeo MIDI
- EQ y mixer strip

Es decir: **lo esencial de mezclar, siempre gratis.** Si una función básica
pudiera cobrarse, el proyecto habría fallado su objetivo.

Esta lista no es una aspiración: cada punto existe hoy en `src/` (no publicado) y está
cubierto por la suite de pruebas del repo (`ctest --test-dir build
--output-on-failure`). El número exacto de pruebas cambia con cada commit, y
por eso no vive en este documento (en el repositorio de código vive en el
README): aquí va la promesa, que no envejece.

### Garantías técnicas del compromiso

- El binario de la Lite se distribuye con su código fuente completo
  (GPL-2.0-or-later mientras qm-dsp y Rubber Band sigan en el árbol; los dos
  son GPL. Ver [`business-model.md`](business-model.md) para la ruta de
  des-GPL).
- "Gratis para siempre" no depende de que el proyecto sobreviva: en cuanto se
  distribuya el primer binario, el código fuente completo es público y cualquiera
  puede leer, compilar, bifurcar y redistribuir. Hasta ese momento, el
  repositorio es privado (decisión del dueño, 2026-10-19): el compromiso se
  cumple en la distribución, no antes.
- No hay ataduras de cuentas, licencias por dispositivo ni telemetría
  obligatoria.

## 2. Pro: de pago, y en un momento posterior

**Existirá una versión Pro de pago. Es una decisión tomada, no una posibilidad
abierta.**

El Pro se financiará con:

- Suscripción (el canal principal de la Lite → Pro)
- Servicios: análisis de librería en servidor, respaldo de grids y keys
- Soporte y servicios para DJs profesionales

### Qué NO es el Pro

El Pro **no** es "la versión que hay que pagar para usar el programa". El Pro
nunca_gatea las funciones básicas de la lista de la sección 1.

Queda explícito porque ya se ha confundido: el **key lock** (tempo sin cambiar
el tono) es esencial y va en la Lite, no en el Pro. Lo mismo el scratch
continuo y el análisis de tonalidad.

Los candidatos natural del Pro (aún por decidir con la comunidad) son
funciones de **crecimiento**, no de uso:

- Stems y separación
- Grabación de sets
- Análisis armónico avanzado y biblioteca de tonos
- DVS / control de vinilotimecode
- Mappings de hardware y packs de contenido
- Soporte prioritario

### Reglas de comunicación

1. Nunca se promete una fecha del Pro.
2. Nunca se insinúa que la Lite es un trial o una versión recortada.
3. Toda cifra de precio del Pro se anuncia junto a "Lite gratis para siempre".
4. Si un usuario pregunta cuánto cuesta usar el programa: la Lite no cuesta
   nada; el Pro es opcional y aún no tiene precio anunciado.

## 3. Financamiento

El proyecto se financia con donaciones y patrocinios (ver [`../FUNDING.md`](../FUNDING.md)),
no con la venta de la Lite. Las donaciones no son inversión: no hay token, ni
participación, ni promesa de retorno.

## 4. Qué pasa si el proyecto se acaba

El compromiso no depende de la continuidad del proyecto: la licencia GPL
obliga a que **el primer binario distribuido venga con el código fuente
completo**, y ese código, una vez publicado, sigue siendo libre y
reproducible aunque el proyecto deje de mantenerse. Quien quiera mantenerlo
puede hacerlo.

Mientras no se haya distribuido ningún binario, el repositorio es privado. Es
una decisión de calendario, no una retirada del compromiso: en cuanto salga
la Lite, el código fuente va con ella, completo.
