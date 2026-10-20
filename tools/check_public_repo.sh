#!/usr/bin/env bash
# check_public_repo.sh — gate de exposicion del repositorio publico.
#
# El repositorio publico (mcontreraz/djmixer) es el SITIO: landing, paginas de
# funding, capturas y el QR. NO es el codigo, ni las specs, ni las notas de
# desarrollo.
#
# Decidido por el dueno del proyecto el 2026-10-20: "dejar solo publica la
# pagina de funding y landing, capturas y specs no; no quiero exponer diseno ni
# codigo". Este gate es el mecanismo para que no se revierta por descuido: sin
# el, cualquier `git add` al repo publico puede volver a publicar el arbol de
# documentacion, que es donde vive el diseno del motor.
#
# Uso:  ./tools/check_public_repo.sh [ruta_del_repo_publico]
# Salida: 0 = solo se publica lo permitido · 1 = hay material que no debe salir
set -uo pipefail

REPO="${1:-.}"
cd "$REPO" || { echo "no existe el repo: $REPO" >&2; exit 1; }

fail=0
ok()  { printf '  ok    %s\n' "$1"; }
bad() { printf '  FALLA %s\n' "$1"; fail=1; }

printf 'Repo publico: %s\n' "$REPO"

# 1) Lo que SI puede estar -------------------------------------------------
ALLOWED_TOP="^(index(\.(en|pt))?\.html|funding(\.(en|pt))?\.html|README\.md|FUNDING\.md|COPYING|LICENSE|donate-qr(-address)?\.png|\.gitignore|robots\.txt|media/.*|\.github/.*|tools/.*)$"
# Lo que NUNCA puede estar (codigo, diseno, evidencia)
FORBIDDEN='^((src|third_party|tests|specs|docs|build|dist|prototype-web|assets/icons/resources)/|(.*\.(cpp|c|h|hpp|qml|icns|mov|mp4|wav|onnx|pxm|frag|vert|qsb|db|rep|gbf|pyc)$))'

printf '\n[1] ficheros prohibidos\n'
prohibidos="$(git ls-files | grep -E "$FORBIDDEN" || true)"
if [ -n "$prohibidos" ]; then
  bad "hay material que no debe salir en el repo publico:"
  printf '        %s\n' $prohibidos
  bad "  (codigo, specs, docs, notas de desarrollo, evidencia del fabricante)"
else
  ok "ningun fichero de codigo, specs, docs ni evidencia del fabricante"
fi

printf '\n[2] lo permitido esta ahi\n'
for f in index.html index.en.html index.pt.html funding.html funding.en.html \
         funding.pt.html README.md FUNDING.md donate-qr.png media/03-decks.png; do
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    ok "$f"
  else
    bad "falta $f (el sitio publico lo necesita)"
  fi
done

printf '\n[3] citas a material que no existe en el repo publico\n'
# Una cita a material privado vale en cualquier forma: un enlace, un atributo
# href/src, una mencion en <code> o un nombre entre acentos graves. Con solo
# mirar los atributos href/src se dejaba pasar lo que mas duele: el texto que
# promete una especificacion o un documento que ya no se publica, que es
# exactamente el fallo que tenia el repo publico (la pagina viva prometia una
# `specs/` que devolvia 404).
PRIVADO_RE='^(docs|specs|src|tests|third_party|build|dist|prototype-web|assets)/'
citas_muertos=0
for f in $(git ls-files '*.html' '*.md'); do
  # enlaces markdown, atributos html, contenido de <code> y texto entre
  # acentos graves, todo en una sola pasada.
  for ref in $(grep -oE '\]\([^)]+\)|(href|src)="[^"#]+"|<code>[^<]*</code>|`[^`]+`' "$f" 2>/dev/null |
               sed -E 's/^\]\(//; s/^(href|src)="//; s/^<code>//; s/<\/code>$//; s/^`//; s/`$//; s/"$//; s/)$//' |
               grep -vE '^(https?:|mailto:|/|#)'); do
    ref_limpio="${ref#./}"
    ref_limpio="${ref_limpio#../}"
    if [[ "$ref_limpio" =~ $PRIVADO_RE ]]; then
      bad "$f cita '$ref', que no existe en el repo publico"
      citas_muertos=1
    fi
  done
done
[ "$citas_muertos" -eq 0 ] && ok "ninguna cita a material privado"

printf '\n[4] el metodo de analisis y los simbolos del fabricante no se nombran\n'
# Decision del board (2026-10-20): el material publicable dice "evidencia local
# no publicada" / "comportamiento observado" / "referencia local". Nombrar el
# metodo o los simbolos internos debilita la posicion clean-room del proyecto
# ("solo comportamiento, nunca codigo copiado") y no aporta nada al lector.
for term in 'decompil' 'Ghidra' 'desensambl' 'volcado de strings' 'string dump' \
            'SyncUnit' 'canPhaseSync' 'setSyncMaster' 'FUN_[0-9a-f]'; do
  if git ls-files '*.html' '*.md' | xargs grep -l -i -E "$term" 2>/dev/null | head -1 | grep -q .; then
    bad "el arbol publico nombra '$term' (metodo de analisis o simbolo del fabricante)"
    citas_muertos=1
  fi
done
[ "$citas_muertos" -eq 0 ] && ok "ni el metodo de analisis ni los simbolos del fabricante"

printf '\n[5] la direccion de donacion y el memo viven en la hoja de funding\n'
if grep -q "GATED25" FUNDING.md 2>/dev/null; then
  ok "FUNDING.md tiene la direccion y el memo (la hoja de deposito)"
else
  bad "FUNDING.md no tiene la direccion: la hoja de deposito debe estar aqui"
fi
for f in index.html index.en.html index.pt.html funding.html funding.en.html funding.pt.html; do
  if grep -q "GATED25" "$f" 2>/dev/null; then
    ok "$f muestra la direccion y el memo"
  else
    bad "$f no muestra la direccion ni el memo (la pagina viva debe poder donarse)"
  fi
done

printf '\n'
if [ "$fail" -eq 0 ]; then
  printf 'RESULTADO: el repo publico solo contiene landing, funding, capturas y el QR.\n'
  exit 0
fi
printf 'RESULTADO: el repo publico tiene material que no debe salir. Arreglalo antes de publicar.\n'
exit 1
