# Plan de lanzamiento público

> Las rutas al arbol de codigo —las marcadas como *(no publicado)*— no se
> pueden abrir aqui: el repositorio de codigo se publica completo junto
> con el primer binario (obligacion de GPL-2.0-or-later).

Fecha: 2026-10-19 · Checklist ejecutable, en orden. Nada de esto toca el código.

## Orden real (decisión del dueño, 2026-10-19)

**Donaciones → release sin firmar → firma cuando entre la primera propina.**

El dueño no tiene la cuenta de Apple Developer (99 USD/año) y el equipo no la
puede comprar. La partida que faltaba (firma y notarización) se pide con las
donaciones, no al revés: se publica la Lite **sin firmar** con instrucciones
explícitas para abrirla, se pide el_capacity de modelos en la campaña, y la
firma entra en la release siguiente en cuanto el dinero esté.

Esto no contradice la regla de announcement de la Fase A: el `.dmg` sin
firmar se anuncia **diciendo explícitamente que va sin firmar y cómo abrirlo**,
y el tarball de fuentes se publica siempre (obligación de GPL, no un gate).

## Narrativa (el activo principal)

**"Un DJ que construyó un Serato/Traktor-like con IA en 1 semana — open
source, gratis para siempre."** Transparencia total sobre el proceso
(qué hizo la IA, qué se verificó a mano, qué falló). La honestidad es el
gancho de confianza.

## Fase A — Preparar el repo (semana 1)

- [x] README reescrito para visitantes nuevos: qué es, build rápido, hoja de
      ruta y a quién se le agradece el trabajo.
- [x] Capturas reales de la app en `media/` (main con pista cargada,
      biblioteca con BPM y tonalidad, SyncLab con el demo sintético) +
      [`devlog.md`](devlog.md) con las notas de desarrollo. Generadas con
      `capture-app.sh` (no publicado); el audio de las capturas es sintético.
- [ ] Demo en video (2-3 min): cargar → mezclar → loop → sync → scratch.
      Sin narración técnica larga; que el producto hable.
- [x] LICENSE visible (ya GPL-2.0-or-later + COPYING) y claridad sobre qm-dsp.
- [ ] Releases con binarios para macOS (firmados/notarizados) — el primer
      binario oficial.
      **Regla de anuncio (decisión del CTO, ver
      `firma-macos.md` (no publicado)):** el único binario que se anuncia
      como descarga es el `.dmg` notarizado. Si la notarización todavía no
      está disponible, no se anuncia ninguna build de macOS como descarga (o
      se dice explícitamente que va sin firmar y cómo abrirla). El
      `.app.zip` sin firmar es material de CI, no una descarga para el
      usuario. El tarball de fuentes se publica siempre: es una obligación de
      GPL, no un gate.
- [ ] Etiquetas de issues: good-first-issue, help-wanted, feature-request.

## Fase B — Lanzamiento (semana 2)

- [x] **Moltbook**: `builds` y `introductions` publicados por el agente
      `56kbpsmodem`, con las URLs en
      `announcement/channel-log.md` (no publicado). Sin cripto:
      la dirección USDC va en `FUNDING.md` y en la página de descarga.
- [ ] **Show HN** (Hacker News): título con la historia — p. ej.
      "Show HN: Open-source DJ software (Serato-like) built with AI in a week".
      Copy listo en `announcement/show-hn-reddit-en.md` §1; falta la cuenta.
- [ ] **Reddit**: r/DJs (el post de producto), r/opensource (el post técnico),
      r/programming (el post de arquitectura RT). Los tres textos son
      distintos, en `announcement/show-hn-reddit-en.md` §2-§4; falta la cuenta.
- [ ] **Hilo en X/Twitter**: build-in-public con capturas de antes/después,
      decisiones de motor (el key lock usa Rubber Band, GPL, con el prototipo de
      WSOLA en el historial) y bugs graciosos. Copy en
      `announcement/anuncio-es.md`; falta la cuenta.
- [ ] Responder TODO en las primeras 48 h — el hilo del fundador construye
      comunidad.

## Fase C — Comunidad (en paralelo)

- [ ] Discord con canales: novedades, ayuda, feature-requests (con votos).
- [ ] Roadmap público votable (GitHub Discussions o feature board).
- [ ] Betatesters: acceso anticipado al Pro cuando exista (lista de espera).

## Fase D — Contenido técnico (continuo, 1 post/2 semanas)

Material exclusivo que YA existe en el repo — cada uno es un post:

1. Cómo hice el scratch sin granulado (motor DVS, continuidad entre
   callbacks, sinc AA por tasa).
2. Loops exactos por beatgrid sin saltos ni silencios (el resize diferido).
3. Key lock: por qué el motor es Rubber Band (GPL) y qué se aprendió del
   prototipo de WSOLA que se descartó (benchmarks de timepitch-bench).
4. Arquitectura RT: el camino de loop no asigna memoria (cache de PCM en
   worker, seqlock, SPSC de capacidad fija) y qué es lo que sí reasigna.
5. REA de Serato/Traktor como método de diseño (clean-room, solo
   comportamiento observable).

## Métricas de éxito (objetivos mínimos)

- GitHub: 300+ estrellas el primer mes.
- Demo video: 1.000+ vistas.
- Discord: 100+ miembros.
- 10+ reportes de bugs/features reales (señal de uso genuino).

## Fase E — Pro (cuando la comunidad lo pida)

- [ ] Redactar y ejecutar la spec 017 (des-GPL) → núcleo propio.
- [ ] Elegir las 2-3 features Pro del primer release según votos.
- [ ] Precio/empaquetado del Pro (ver docs/business-model.md).

## Reglas de comunicación

- Nunca prometer fechas del Pro.
- Siempre responder qué es Lite-gratis-forever y qué será de pago.
- Crédito al stack open source usado (miniaudio, BeatThis, qm-dsp mientras
  esté): da autoridad y reciprocidad con la comunidad.
- **Toda feature que se anuncie se verifica contra el repo antes de
  publicarla**, y el libro de campana es
  `announcement/channel-log.md` (no publicado): un post no
  existe hasta que su URL está anotada ahí.
