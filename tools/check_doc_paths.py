#!/usr/bin/env python3
"""Comprueba que ningun documento publico cite una ruta que no exista en el repo.

El repo es publico y la evidencia cruda de ingenieria inversa (REA) NO se
publica (ver docs/referencia-local.md). Un documento que cita una ruta
inexistente es una referencia muerta para quien lee el repo, salvo que lo diga
explicitamente ("referencia local no publicada").

Reglas:

  1. Una cita bajo `docs/` o `specs/` que no exista en el repo siempre esta
     mal: son rutas del arbol publicado y el lector las busca ahi. Tiene que
     estar marcada como referencia local no publicada.
  2. Una cita bajo `src/`, `tests/`, `tools/`, `third_party/` o `packaging/`
     que no exista esta mal, salvo en los ficheros de tareas (`tasks.md`),
     donde nombrar un fichero planificado es lo esperado.

Salida: codigo 1 si hay citas sin marcar, 0 si no hay ninguna.

Uso:
    python3 tools/check_doc_paths.py [RAIZ_DEL_REPO]
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

# Directorios y ficheros que ve el visitante del repo.
PUBLIC_TREES = ("docs/", "specs/", ".specify/")
PUBLIC_FILES = ("README.md", "FUNDING.md")

# Prefijos de ruta que un lector puede leer como "una ruta del repo".
PATH_ROOTS = (
    "docs/",
    "specs/",
    "src/",
    "tests/",
    "tools/",
    "third_party/",
    "packaging/",
    ".specify/",
)

# Arboles publicados: una ruta de aqui que no exista es siempre una
# referencia muerta (aunque el fichero sea un plan).
PUBLISHED_ROOTS = ("docs/", "specs/", ".specify/")

# Los ficheros de tareas nombran ficheros que aun no existen (planes).
TASK_FILES = ("tasks.md",)

# Una cita esta marcada si el documento dice, en la linea o en las tres lineas
# anteriores, que el material es local y no publicado.
MARKERS = (
    "referencia local",
    "referencia-local.md",
    "no publicada",
    "no publicado",
    "no se publica",
    "no estan en el repo",
    "no esta en el repo",
    "no esta en `main`",
    "no está en `main`",
    "fuera de `main`",
    "fuera de la rama trunk",
)

# `docs/...`, `src/...`, etc. dentro de backticks.
BACKTICK_RE = re.compile(r"`((?:%s)[^`\s]*)`" % "|".join(PATH_ROOTS))
# [texto](docs/...) — enlaces markdown.
LINK_RE = re.compile(r"\]\(((?:\.\./)*(?:%s)[^)\s]*)\)" % "|".join(PATH_ROOTS))
# [texto](cualquier.md) — cualquier enlace markdown relativo.
ANY_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
# Forma abreviada "src/deck.h/.cpp".
COMPOUND_RE = re.compile(r"[A-Za-z0-9_]/\.[A-Za-z0-9]+$")
# Referencia "src/deck.cpp:639" o "src/deck.cpp:1414-1445".
LINE_SUFFIX_RE = re.compile(r":[0-9][0-9\u2013\-, ]*$")


def tracked_paths(root: str) -> list[str]:
    out = subprocess.run(
        ["git", "-C", root, "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.splitlines()


def public_documents(tracked: list[str]) -> list[str]:
    docs = []
    for path in tracked:
        if path.startswith("docs/referencia-"):
            continue  # el material local, si existe, no se publica
        if path.startswith("docs/publico/"):
            continue  # fuentes del sitio: sus enlaces son relativos a la
            #            raiz del repo publico, no a su directorio
        if path.endswith((".md", ".markdown")) and path.startswith(PUBLIC_TREES):
            docs.append(path)
        elif path in PUBLIC_FILES:
            docs.append(path)
    return sorted(set(docs))


def build_exists(tracked: list[str]) -> set[str]:
    """Rutas que existen: ficheros versionados y directorios con contenido."""
    exists = set(tracked)
    for path in tracked:
        parts = path.split("/")
        for i in range(1, len(parts)):
            exists.add("/".join(parts[:i]))
    return exists


def submodule_roots(tracked: list[str]) -> list[str]:
    """Submodulos: su contenido vive en otro repositorio, no en el indice."""
    roots = []
    for path in tracked:
        if path.startswith("third_party/") and "/" not in path[len("third_party/"):]:
            roots.append(path + "/")
    return roots


def is_marked(lines: list[str], index: int) -> bool:
    """Una cita esta marcada si el documento lo dice.

    Dos formas validas: en la linea (o en las tres lineas alrededor), o en una
    declaracion al principio del documento, que es como se marca un fichero
    entero de una vez.
    """
    window = " ".join(lines[max(0, index - 3): index + 4]).lower()
    if any(marker in window for marker in MARKERS):
        return True
    return any(marker in "\n".join(lines[:40]).lower() for marker in MARKERS)


def broken_links(root: str, tracked: list[str]) -> list[tuple[str, int, str]]:
    """Enlaces markdown relativos que no apuntan a nada del repo."""
    broken: list[tuple[str, int, str]] = []
    for rel in public_documents(tracked):
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(lines, 1):
            for target in ANY_LINK_RE.findall(line):
                if target.startswith(("http://", "https://", "mailto:", "/", "#")):
                    continue  # enlaces externos o rutas de la app
                path = target.split("#")[0]
                if not path or any(ch in path for ch in "*?<>{"):
                    continue
                resolved = os.path.normpath(
                    os.path.join(root, os.path.dirname(rel), path))
                if not os.path.exists(resolved):
                    broken.append((rel, number, target))
    return broken


def main() -> int:
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    tracked = tracked_paths(root)
    exists = build_exists(tracked)
    submodules = submodule_roots(tracked)
    problems: list[tuple[str, int, str, str]] = []
    marked_count = 0

    for rel in public_documents(tracked):
        path = os.path.join(root, rel)
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        is_task_file = rel.endswith(TASK_FILES)

        for number, line in enumerate(lines, 1):
            for cited in BACKTICK_RE.findall(line) + LINK_RE.findall(line):
                cited = cited.rstrip("/.,;:)")
                if not cited or any(ch in cited for ch in "*?<>{"):
                    continue
                if COMPOUND_RE.search(cited):
                    continue
                path_part = LINE_SUFFIX_RE.sub("", cited)
                normalized = path_part.lstrip("./")
                # `../../docs/...` relativo al documento.
                tail = re.sub(r"^(\.\./)+", "", normalized)
                if normalized in exists or tail in exists:
                    continue
                if any(normalized.startswith(root) for root in submodules):
                    continue  # contenido de un submodulo: no esta en el indice
                if is_task_file and not cited.startswith("docs/referencia-"):
                    continue  # en un fichero de tareas, lo normal es un plan
                if is_marked(lines, number - 1):
                    marked_count += 1
                    continue
                problems.append((rel, number, cited, line.strip()))

    for rel, number, cited, context in problems:
        print(f"{rel}:{number}: ruta inexistente sin marcar -> {cited}")
        print(f"    {context[:160]}")

    broken = broken_links(root, tracked)
    for rel, number, target in broken:
        print(f"{rel}:{number}: enlace markdown roto -> {target}")

    print()
    print(f"{len(problems)} cita(s) sin marcar, {marked_count} marcadas como "
          f"referencia local no publicada.")
    print(f"{len(broken)} enlace(s) markdown rotos.")

    return 1 if (problems or broken) else 0


if __name__ == "__main__":
    sys.exit(main())
