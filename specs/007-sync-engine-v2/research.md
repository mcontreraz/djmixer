# Research: Sync Engine v2

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

## Decisión 1: Bandas del corrector (entierra el umbral-sin-fuente)

- **Decision**: deadband 0.01, proporcional k=0.7 con tope ±5%, tope de delta
  por tick 0.02, train-wreck >0.2 a +5% fijo. Eliminar toda mención al umbral-sin-fuente
  (sin fuente en REA ni en Mixxx).
- **Rationale**: números de `calcSyncAdjustment` (Mixxx `bpmcontrol.cpp`),
  probados a escala. Reimplementación limpia, no copia.
- **Alternatives considered**: mantener kp=0.2 + umbral-sin-fuente (rechazado: sin origen).

## Decisión 2: Beat-match por seek al enganchar

- **Decision**: al pulsar SYNC, seek único a fase (regla 1/8 pasado/futuro con
  `BeatGrid`), luego PLL de mantenimiento.
- **Rationale**: igual que Mixxx `getNearestPositionInPhase`; evita rampas
  largas en errores grandes. Nuestra `BeatGrid` ya expone lo necesario.
- **Alternatives considered**: solo PLL (rechazado: convergencia lenta en
  desfases grandes).

## Decisión 3: Quantize como gate + user offset

- **Decision**: sin Q solo tempo (sin fase); con Q, fase. El bend manual se
  absorbe como offset en vez de pelear con el PLL.
- **Rationale**: ambos mundos lo exigen (`SetQuantizeEnabled` en REA;
  `calcSyncAdjustment` en Mixxx). El pill Q existente se cablea aquí.
- **Alternatives considered**: gate invertido o siempre-fase (rechazados).

## Decisión 4: Scratch fuera del sync

- **Decision**: mientras el deck está en grab/spin, sus datos no alimentan al
  seguidor (se congela su error o se pausa su corrección).
- **Rationale**: Mixxx excluye `instantaneousBpm` por jitter; mismo motivo.
- **Alternatives considered**: seguir corrigiendo durante scratch (rechazado:
  el jitter de la mano desestabiliza al otro deck).

## Decisión 5: Métricas, no porcentajes

- **Decision**: autotest reporta `lockMs` (hasta phaseErr <0.02 estable) y
  `phaseErr` final; umbrales 4000 ms / 0.02. Prohibido citar fidelidad en %.
- **Rationale**: cierra la puerta a afirmaciones sin medida (lección del umbral-sin-fuente).
