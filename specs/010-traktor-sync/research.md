# Research: Traktor-parity Sync (010)

## R0. Qué se toma y qué no — DECIDIDO

De `docs/referencia-traktor/` se toman ARQUITECTURA y COMPORTAMIENTO:
MasterClock con dueño, SyncUnit con offset en beats, gates de phase-sync,
pipeline por etapas (transientes → histograma → coherencia → plantillas).
NO se toma código: los 11 `.c` decompilados son obra propietaria de NI;
reimplementación desde lo entendido, verificada contra benchmark propio.
`grep` de control en SC-003.

## R1. MasterClock — DECIDIDO

`SyncEngine` suma `masterDeck/auto`; `m_tempoRef` pasa a leerse del reloj.
Takeover actual = reasignación automática. Badge + botón por deck. El resto
(band occupancy, octavas, downbeat-snap, pitch relativo) no se toca.

## R2. Histograma + coherencia — DECIDIDO

Sobre el onset-envelope existente (flujo espectral ya lo tenemos en
`detectTempo`): histograma de intervalos entre picos → candidatos →
coherencia (fracción de onsets que caen en la grilla candidata) →
plantillas de patrón para octava (correlación contra boom-clap 4/4 y
mitad/doble). Entra como etapa ANTES del refinado al 4%, no como reemplazo:
la cadena queda Serato → BeatThis → QM → histograma+coherencia → propio.

## R3. Orden — DECIDIDO

MasterClock primero (es lo que duele en cabina), histograma después
(bench). Cada pieza con sync-test verde antes/después.
