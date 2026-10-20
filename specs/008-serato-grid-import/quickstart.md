# Quickstart: Serato Grid Import

> **Material de referencia local, no publicado.** Las rutas `referencia-*/` (no publicado)
> y los nombres de fichero sueltos de ese material que se citan aquí viven
> **solo en la máquina de desarrollo**: no están en el repo público. Lo que se
> publica es el método y la conclusión. Ver
> referencia local (../../docs/referencia-local.md, no publicado).

**Feature**: `008-serato-grid-import`

## 1. Verificar el oráculo (sin compilar nada)

Los scripts de esta sección son **material local, no publicado**: no están en
el repo público, así que en un clon limpio estos comandos no existen. Sirven
como registro del método; el oráculo que manda es el test del repo.

```sh
python3 docs/referencia-serato/replica/beatgrid-datos/verify_blob.py
# esperado: {"passed": 12}
```

## 2. Inspeccionar un payload real

```sh
# extraer GEOB crudo de un MP3 propio (solo lectura) y pasarlo al parser:
python3 docs/referencia-serato/replica/beatgrid-datos/beatgrid_blob.py /tmp/beatgrid-crudo.bin
```

## 3. Probar el import tras implementar

```sh
cmake --build build -j
DJMIXER_AUTOTEST=1 ./build/djmixer 2>&1 | grep -i "serato.*grid\|gridSource"
# MP3 tageado → bpm del tag; MP3 sin tag → detección (sin cambios)
```

## 4. Casos manuales

1. MP3 con BeatGrid → badge "Serato" en deck, BPM = tag ±0.01.
2. Mismo MP3 con tag corrupto (backup primero) → badge "Auto", suena igual.
3. Re-análisis con lock → conserva importada.
