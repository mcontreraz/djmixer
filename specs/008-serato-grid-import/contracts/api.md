# Contracts: Serato Grid Import

**Feature**: `008-serato-grid-import`

## C1. `SeratoGrid::parse(path) → Parsed` + `toBeatGrid` (C++, worker)

```cpp
struct SeratoGridParsed {
    bool ok = false;            // payload válido y convertible
    SeratoGridPayload payload;  // markers + terminal (sin wrapper)
    bool locked = false;        // lock en tags (hoy: false, T015)
};
SeratoGridParsed SeratoGrid::parse(const QString &path);
BeatGrid SeratoGrid::toBeatGrid(const SeratoGridPayload &p, double durationSec);
int SeratoGrid::selfTest();     // 12/12 oráculo, exigido en autotest
```

- Pre: archivo existe, legible. Post: `ok=false` ⇒ sin efectos (fallback).
- Nunca lanza; nunca toca audio; <50 ms (solo cabeceras).

## C2. `WaveformAnalyzer` — orden de intentos

```text
1. parse(path) → ok? usar grid importada (source=serato), escribir caché v8, FIN.
2. si no: detección actual (source=detected), como hoy.
3. re-análisis con caché v8 locked → conservar sin tocar.
```

## C3. Sidecar v8

```text
magic "DJW1" + version u8: 7 → 8
v8 append: locked u8 + source u8
lector: acepta 7 (defaults locked=0, source=detected) y 8; otra versión → re-analizar.
```

## C4. `Deck.gridSource` (Q_PROPERTY, solo lectura)

```qml
text: deckA.gridSource === "serato" ? "Serato" : "Auto"
```

- Solo display/debug; el sync no la consulta.
