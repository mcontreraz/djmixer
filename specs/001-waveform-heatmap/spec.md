# Feature Specification: Waveform Heatmap

**Feature Branch**: `001-waveform-heatmap`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "F2: análisis de waveform con mapa de calor igual que Serato (picos reales + colores por bandas espectrales, overview y waveforms grandes con data real en vez de simulada)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Overview real del tema cargado (Priority: P1)

El DJ carga un tema al deck y la tira overview muestra la forma de onda real
del archivo (silencios, drops, breaks visibles), con el playhead avanzando
sobre data real en vez de la simulación actual.

**Why this priority**: Es el cambio visible más valioso: hoy el overview miente
(onda sintética idéntica para todos los temas). Sin esto nada más de F2 tiene
sentido.

**Independent Test**: Cargar el WAV de prueba al deck 1 y comparar visualmente:
el overview debe cambiar respecto al de otro tema y el playhead debe recorrerlo
de izquierda a derecha durante la reproducción.

**Acceptance Scenarios**:

1. **Given** un tema cargado en el deck, **When** se mira el overview, **Then** la forma refleja el audio real (partes fuertes anchas, silencios planos).
2. **Given** reproducción en curso, **When** pasan 10 segundos, **Then** el playhead avanzó proporcionalmente a posición/duración sobre la forma real.

---

### User Story 2 - Mapa de calor por bandas como Serato (Priority: P2)

Las waveforms grandes apiladas colorean cada instante según su contenido
espectral (graves, medios, agudos), igual que el heatmap de Serato, de modo
que kicks, hats y vocales se distinguen a golpe de vista.

**Why this priority**: Es la firma visual pedida ("igual que Serato") y la base
para mezclar por vista (ver dónde entra el bajo). Depende de US1 (picos reales).

**Independent Test**: Cargar un tema con intro suave + drop fuerte: la zona del
drop debe mostrar colores e intensidades distintas a la intro.

**Acceptance Scenarios**:

1. **Given** un tema con secciones contrastadas, **When** se miran las waveforms grandes, **Then** distintas secciones muestran distintos colores de forma estable (mismo tema = mismos colores siempre).
2. **Given** dos temas distintos, **When** se comparan sus waveforms, **Then** las formas y colores difieren.
3. **Given** reproducción en curso, **When** se mira la waveform grande de ese deck, **Then** la forma avanza bajo una línea central fija (scroll, no playhead móvil).
4. **Given** la waveform grande, **When** se pulsa +/− de zoom, **Then** la forma se agranda/achica (menos/más segundos visibles).

**Nota scratch**: arrastrar sobre la waveform para scratch/cue es F3 (requiere motor de seek en el hilo de audio); esta feature deja el vista lista (coordenada tiempo↔píxel + línea central).

---

### User Story 3 - Análisis en segundo plano con caché (Priority: P3)

Al cargar un tema se analizan sus picos y colores sin congelar la UI ni cortar
el audio en curso, y el resultado se guarda: la segunda vez que se abre el
mismo tema aparece al instante.

**Why this priority**: Sin esto, cada carga tarda (decodificar 45 MB en el hilo
UI congelaría la app) y el análisis se repetiría siempre.

**Independent Test**: Cargar el WAV de prueba midiendo tiempo hasta overview
real (aceptable: segundos, UI viva), cerrarlo, recargarlo y verificar que el
overview aparece de inmediato.

**Acceptance Scenarios**:

1. **Given** reproducción en curso en deck B, **When** se carga y analiza un tema en deck A, **Then** el audio de B no se corta ni hace clicks.
2. **Given** un tema ya analizado, **When** se vuelve a cargar, **Then** su overview es inmediato (caché válida por ruta + tamaño + fecha del archivo).

---

### Edge Cases

- ¿Qué pasa con un archivo corrupto o formato no soportado? → overview vacío + mensaje discreto, sin crashear ni bloquear el deck.
- ¿Cómo se comporta con temas muy largos (1h+)? → el análisis progresa y el overview se refina por partes; la reproducción no espera al análisis.
- ¿Qué pasa si se carga otro tema a mitad de un análisis? → el análisis anterior se cancela limpiamente.
- ¿Qué pasa si el archivo cambia en disco tras cachearse? → la caché se invalida (ruta + tamaño + fecha) y se re-analiza.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST calcular picos reales (mínimo/máximo por bucket) de cada tema cargado.
- **FR-002**: El sistema MUST asignar un color por bucket según energía en 3 bandas (graves/medios/agudos), determinista por archivo.
- **FR-003**: El overview de cada deck MUST dibujarse desde los picos/colores calculados, no simulados.
- **FR-004**: Las waveforms grandes MUST usar los mismos datos (mayor densidad) con números de beat y playhead encima.
- **FR-005**: El análisis MUST correr fuera del hilo de audio y fuera del hilo UI de render (hilo worker).
- **FR-006**: El sistema MUST cachear el análisis por archivo y reutilizarlo si el archivo no cambió.
- **FR-007**: El sistema MUST cancelar un análisis en curso si su deck carga otro tema.
- **FR-008**: Un fallo de análisis MUST degradar a overview vacío, nunca bloquear carga ni reproducción.

### Key Entities

- **WaveformCache**: buckets por tema (min, max, color RGB por bucket, resolución), clave = ruta + tamaño + fecha; vive en disco y memoria.
- **Track**: archivo de audio ya conocido (título, url, formato) + referencia a su WaveformCache cuando existe.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Dos temas distintos muestran overviews visiblemente distintos (verificación visual en captura).
- **SC-002**: La UI sigue respondiendo durante el análisis (el play/pausa reacciona en menos de 200 ms mientras se analiza otro tema).
- **SC-003**: Recargar un tema analizado muestra su overview en menos de 300 ms.
- **SC-004**: El mismo archivo siempre produce los mismos colores (dos análisis del WAV de prueba son idénticos píxel a píxel salvo el playhead).
- **SC-005**: Cargar un archivo corrupto no crashea la app y el deck sigue operativo.

## Assumptions

- El análisis se dispara al cargar al deck (lazy), no al listar la carpeta; la playlist no espera análisis.
- Resolución inicial: overview ~200 buckets + detalle denso para las grandes; el zoom con scroll queda fuera (F2b).
- El beatgrid/BPM real es otra feature (sync); aquí solo forma + color, sin detección de beats.
- Formatos: los que ya decodifica el motor (wav/mp3/flac/m4a); el resto degrada según FR-008.
