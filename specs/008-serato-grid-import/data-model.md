# Data Model: Serato Grid Import

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

**Feature**: `008-serato-grid-import` | **Date**: 2026-10-13

## SeratoGridPayload (solo lectura, efímera)

```text
versionMajor: u8   // debe ser 1
versionMinor: u8   // debe ser 0
markers: Marker[N] // N incluye terminal
tail: bytes[0..2]  // opacos, se conservan
```

```text
Marker { timeSec: f32, beatsToNext: u32 | bpmFinal: f32 (solo terminal) }
```

Reglas (de `serializer-v1.md` + validador `1018f2294`):

- N como uint32 BE; si longitud no cuadra, reinterpretar syncsafe.
- Tiempos intermedios estrictamente crecientes; terminal > último.
- BPM final > 0 y finito; ≤128 marcadores.
- N=0 con len 6-8 → payload vacío reconocido ⇒ NO grid válida (fallback).

## BeatGrid (extensión, persiste en sidecar v8)

```text
beats: double[]    // existente: segundos de fuente
bpm: double        // existente
downbeat: double   // existente (= markers[0].timeSec al importar)
+ locked: bool     // NUEVO: no re-analizar ni sobrescribir
+ source: enum { detected, serato }  // NUEVO, default detected
```

Sidecar: magic `DJW1` v7 → v8 (append `locked:u8, source:u8`); lector acepta ambas.

## Conversión payload → BeatGrid

```text
para cada tramo i (no terminal):
    bpmLocal = beatsToNext[i] / (t[i+1] - t[i]) * 60
    emitir beats uniformes a bpmLocal entre t[i] y t[i+1]
tramo terminal: extender con bpmFinal (misma ventana que el detector: máx. duración archivo)
downbeat = t[0]; bpm global = bpmFinal (== bpm del catálogo Serato)
locked = lock encontrado en tags (si no: false)
```

## Relaciones

```text
WaveformAnalyzer ──usa──▶ SeratoGrid::parse(path) ──éxito──▶ BeatGrid{source=serato, ...}
        │──fallo──▶ detección actual ──▶ BeatGrid{source=detected, ...}
SyncEngine ──consume──▶ BeatGrid (sin cambios: beats/bpm/downbeat iguales)
Deck.gridSource ──expone──▶ QML (badge/debug)
```

## Estado

Sin máquina de estados nueva. `locked` es el único invariante: `locked ⇒
analyzer.writeCache` prohibido (salvo invalidación explícita futura).
