# Feature Specification: Sync Engine v2 (síntesis Serato + Mixxx)

**Feature Branch**: `007-sync-engine-v2`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "tomar lo mejor de ambos mundos: comportamiento Serato (REA verificado) + matemática calibrada Mixxx (ideas, sin pegar código GPL), sobre el SyncEngine de la rama 004 ya mergeada"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Corrección calibrada (Priority: P1)

El seguidor converge al líder con las bandas validadas (deadband, proporcional
con topes, train-wreck) en vez de las ganancias sin fuente (kp=0.2, umbral
umbral-sin-fuente). Sin oscilaciones audibles.

**Why this priority**: Es el corazón del sync; los números actuales no tienen
origen y el umbral-sin-fuente no existe en ninguna evidencia.

**Independent Test**: Dos temas con BPM distintos + SYNC: el seguidor clava
tempo y fase sin bombear (error final <0.02 beats, lock en <4 s).

**Acceptance Scenarios**:

1. **Given** líder a 124 BPM y seguidor a 126 BPM, **When** se activa SYNC, **Then** el seguidor iguala tempo y alinea fase sin oscilar.
2. **Given** error inicial >0.2 beats ("train wreck"), **When** se activa SYNC, **Then** caza a máxima corrección acotada sin pasarse de forma inestable.

---

### User Story 2 - Enganche por seek al pulsar (Priority: P1)

Al pulsar SYNC, el seguidor salta de una vez a la posición en fase (regla
1/8 pasado/futuro) y después el PLL solo mantiene. Sin salto inicial, el
corrector tarda demasiado en errores grandes.

**Why this priority**: Sin enganche, el convergencia depende solo del PLL y es
lenta en errores grandes.

**Independent Test**: Con desfase de medio beat, pulsar SYNC → salto inmediato
a fase y luego mantenimiento fino.

**Acceptance Scenarios**:

1. **Given** desfase cualquiera, **When** SYNC, **Then** el primer ajuste es un seek a fase (no rampa larga).
2. **Given** pulsado tarde (cerca del beat siguiente), **When** SYNC, **Then** engancha al beat más cercano (regla 1/8), no al anterior.

---

### User Story 3 - Quantize como gate (Priority: P2)

La corrección de fase solo actúa con quantize activado (pill Q). Sin
quantize, el sync iguala tempo pero no toca la fase.

**Why this priority**: Lo exigen ambos mundos (handler `SetQuantizeEnabled`
en REA + `calcSyncAdjustment` en Mixxx) y le da función real al pill Q.

**Independent Test**: SYNC con Q apagado → tempos iguales, fases libres;
encender Q → las fases se alinean.

**Acceptance Scenarios**:

1. **Given** SYNC sin Q, **When** hay desfase, **Then** no hay corrección de fase.
2. **Given** se enciende Q con SYNC, **When** hay desfase, **Then** corrige.

---

### User Story 4 - Métricas de convergencia (Priority: P2)

El autotest mide y reporta: error de fase final (beats), tiempo de lock y
sobreoscilación. Nada de porcentajes sin métrica.

**Why this priority**: Convierte "funciona" en cifras auditables; es la
condición del merge.

**Independent Test**: Autotest imprime `lockMs`, `phaseErr` y pasa con umbrales.

**Acceptance Scenarios**:

1. **Given** escenario estándar, **When** corre el autotest, **Then** reporta lockMs <4000 y phaseErr <0.02.

---

### Edge Cases

- ¿Sin beatgrid en algún deck? → solo tempo (modo Tempo, como Serato), nunca fase.
- ¿Scratch/spin durante sync? → el seguidor ignora la velocidad de scratch (anti-jitter, como Mixxx).
- ¿Seek manual en seguidor? → re-engancha contra la nueva distancia del líder.
- ¿BPM a más de octava? → fold ×2/×0.5 (ya existe) antes de corregir.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El corrector MUST usar bandas 0.01 / 0.2 / ±5% / delta 0.02 con k=0.7 (origen: Mixxx `bpmcontrol.cpp`, reimplementado).
- **FR-002**: El sistema MUST eliminar el umbral umbral-sin-fuente sin fuente de todo el código y docs.
- **FR-003**: Pulsar SYNC MUST hacer beat-match por seek (regla 1/8) antes del PLL.
- **FR-004**: La fase MUST corregirse solo con quantize activado.
- **FR-005**: El bend manual MUST absorberse como offset (no pelear con el PLL).
- **FR-006**: Scratch/spin MUST excluirse del sync de seguidores.
- **FR-007**: El autotest MUST reportar lockMs/phaseErr con umbrales.

### Key Entities

- **SyncState**: por deck (Off/Armed/Tempo/Beat) + primario + modo (Off/Simple/Smart). Ya existe en `SyncEngine`; se recalibra, no se rediseña.
- **SyncMetrics**: lockMs, phaseErr final, overshoot (solo test).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Lock en <4 s con phaseErr <0.02 beats en escenario estándar.
- **SC-002**: Sin quantize no hay corrección de fase (verificable en test).
- **SC-003**: Cero menciones al umbral-sin-fuente en código/docs.
- **SC-004**: Autotest sync en verde con métricas impresas.

## Assumptions

- Se parte del `SyncEngine` mergeado (rama 004); es recalibración, no rewrite.
- Smart/downbeat real sigue futuro (heurística módulo 4 cuando toque).
- Licencia: ideas de Mixxx (GPL) reimplementadas en limpio, sin pegar código.
