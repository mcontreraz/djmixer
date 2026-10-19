#!/usr/bin/env bash
# check-funding.sh — gate de publicación para FUNDING.md
#
# Comprueba que la página de apoyo esté lista para anunciarse:
#   1. que no queden placeholders,
#   2. que la dirección USDC sea válida (Stellar strkey con checksum CRC16 o
#      EVM 0x + 40 hex, según la red publicada),
#   3. que el bloque de cumplimiento (donación no es inversión, posible
#      impuesto para quien dona, no es consejo fiscal) siga intacto,
#   4. que las vías sin cripto estén presentes,
#   5. que el texto de la promesa no se contradiga ni prometa fecha del Pro.
#
# Uso:  ./tools/check-funding.sh
# Salida: 0 = listo para publicar · 1 = falta algo (lista qué falta)

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FILE="${1:-$ROOT/FUNDING.md}"
PROMISE="$ROOT/docs/promise.md"

fail=0

ok()   { printf '  ok    %s\n' "$1"; }
bad()  { printf '  FALLA %s\n' "$1"; fail=1; }

if [ ! -f "$FILE" ]; then
  printf 'no existe: %s\n' "$FILE" >&2
  exit 1
fi

printf 'FUNDING.md: %s\n' "$FILE"

# Texto normalizado (espacios colapsados) para que las frases partidas entre
# líneas se comprueben igual.
flat="$(tr '\n' ' ' <"$FILE" | tr -s '[:space:]' ' ')"
has() { printf '%s' "$flat" | grep -qi -- "$1"; }

# 1. Placeholders ----------------------------------------------------------------
printf '\n[1] placeholders\n'
while IFS= read -r pat; do
  [ -z "$pat" ] && continue
  if grep -qE "$pat" "$FILE"; then
    bad "queda un placeholder ($pat) — la página no se puede publicar"
  else
    ok "sin placeholder ($pat)"
  fi
done <<'EOF'
0x<<<
REEMPLAZAR
PLACEHOLDER
FIXME
TU_DIRECCION
EOF

# 2. Dirección USDC --------------------------------------------------------------
printf '\n[2] dirección USDC\n'

# Stellar: G + 55 caracteres base32 (56 en total). EVM: 0x + 40 hex.
# Solo se mira el bloque de direcciones (primer bloque de código tras el
# encabezado "**Address"), para no contar otras direcciones mentioned en el
# texto (p. ej. el issuer del USDC en Stellar).
addr_block="$(awk '/^\*\*Address/{f=1} f && /^```/{c++; next} c==1{print} c>=2{exit}' "$FILE")"
stellar_addrs="$(printf '%s\n' "$addr_block" | grep -oE '\bG[A-Z2-7]{55}\b' | sort -u || true)"
evm_addrs="$(printf '%s\n' "$addr_block" | grep -oE '\b0x[0-9a-fA-F]{40}\b' | sort -u || true)"

stellar_count="$(printf '%s\n' "$stellar_addrs" | grep -c '[A-Z2-7]' || true)"
evm_count="$(printf '%s\n' "$evm_addrs" | grep -c '0x' || true)"
total_count=$(( ${stellar_count:-0} + ${evm_count:-0} ))

if [ "${total_count:-0}" -eq 0 ]; then
  bad "no hay ninguna dirección (Stellar G… ni EVM 0x…) — el dueño del proyecto debe insertar la suya"
else
  ok "direcciones encontradas: ${stellar_count} Stellar, ${evm_count} EVM"
fi

if [ "${stellar_count:-0}" -gt 1 ]; then
  bad "hay $stellar_count direcciones Stellar — debe haber exactamente una por red publicada"
fi
if [ "${evm_count:-0}" -gt 1 ]; then
  bad "hay $evm_count direcciones 0x… — debe haber exactamente una por red publicada"
fi

# Valida el checksum CRC16-XModem de Stellar (strkey) con el SDK oficial.
if [ "${stellar_count:-0}" -ge 1 ]; then
  addr="$(printf '%s\n' "$stellar_addrs" | head -1)"
  if python3 - "$addr" <<'PY'
import base64, binascii, struct, sys
a = sys.argv[1]
try:
    e = a.encode("ascii"); e = e + b"=" * ((8 - len(e) % 8) % 8)
    d = base64.b32decode(e)
    ok = base64.b32encode(d) == e and struct.pack("<H", binascii.crc_hqx(d[0:-2], 0)) == d[-2:]
except Exception:
    ok = False
sys.exit(0 if ok else 1)
PY
  then
    ok "dirección Stellar con checksum strkey válido: ${addr:0:6}…${addr: -6}"
  else
    bad "dirección Stellar con checksum strkey INVÁLIDO: $addr (cópiala otra vez; no la escribas a mano)"
  fi
fi

if [ "${evm_count:-0}" -ge 1 ]; then
  addr="$(printf '%s\n' "$evm_addrs" | head -1)"
  ok "dirección EVM con formato válido: ${addr:0:6}…${addr: -6}"
fi

if grep -q "First 6 characters" "$FILE" && grep -q "Last 6 characters" "$FILE"; then
  ok "la lista de verificación de la dirección está presente"
else
  bad "falta la lista de verificación (primeros/últimos 6 caracteres)"
fi

# 3. Cumplimiento ----------------------------------------------------------------
printf '\n[3] bloque de cumplimiento\n'
for needle in \
  "not investments" \
  "no token" \
  "taxable income" \
  "SUNAT" \
  "not giving tax advice"
do
  if has "$needle"; then
    ok "presente: \"$needle\""
  else
    bad "falta: \"$needle\""
  fi
done

# 4. Vías sin cripto -------------------------------------------------------------
printf '\n[4] vías sin cripto\n'
for needle in "GitHub Sponsors" "Patreon"; do
  if has "$needle"; then
    ok "presente: $needle"
  else
    bad "falta la vía sin cripto: $needle"
  fi
done

# 5. Promesa --------------------------------------------------------------------
printf '\n[5] promesa\n'
for needle in \
  "free for everyone" \
  "stays free forever" \
  "no subscription" \
  "no trial that expires" \
  "paid Pro version will exist"
do
  if has "$needle"; then
    ok "presente: \"$needle\""
  else
    bad "falta: \"$needle\""
  fi
done

if printf '%s' "$flat" | grep -qiE 'free trial|trial version|trial period|Pro (launch|release)[^.]{0,20}(on|in) [0-9]|Pro release date|coming in 20[0-9][0-9]'; then
  bad "el texto insinúa trial o promete fecha del Pro"
else
  ok "sin trial y sin fecha para el Pro"
fi

if [ -f "$PROMISE" ]; then
  if grep -qi "para siempre" "$PROMISE" && grep -qi "No hay precio, no hay cuota, no hay suscripción" "$PROMISE"; then
    ok "docs/promise.md existe y fija el compromiso de la Lite"
  else
    bad "docs/promise.md cambió o no está donde se espera"
  fi
else
  bad "falta docs/promise.md (fuente canónica del compromiso)"
fi

printf '\n'
if [ "$fail" -eq 0 ]; then
  printf 'RESULTADO: FUNDING.md listo para publicar.\n'
  exit 0
fi
printf 'RESULTADO: FUNDING.md NO está listo. Arregla lo de arriba y repite.\n'
exit 1
