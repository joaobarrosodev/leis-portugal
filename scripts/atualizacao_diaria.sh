#!/usr/bin/env bash
# Atualização diária do acervo: DRE (1.ª Série) e EUR-Lex (Jornal Oficial) de um
# intervalo de datas, ligação Portugal–UE, validação e relatórios.
#
# Uso: scripts/atualizacao_diaria.sh [DE] [ATÉ]
#   DE/ATÉ em AAAA-MM-DD; por omissão, o dia anterior em Lisboa.
#
# Códigos de saída:
#   0  tudo correu bem
#   1  alguma recolha falhou, mas o acervo é válido (pode ser publicado)
#   2  a validação falhou (não publicar)
set -uo pipefail

yesterday() {
  TZ=Europe/Lisbon date -d yesterday +%F 2>/dev/null || TZ=Europe/Lisbon date -v-1d +%F
}

FROM="${1:-$(yesterday)}"
TO="${2:-$FROM}"
for value in "$FROM" "$TO"; do
  if [[ ! "$value" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "Data inválida: $value (esperado AAAA-MM-DD)" >&2
    exit 2
  fi
done

output() {
  # Valores para os passos seguintes do GitHub Actions (ignorado fora do Actions).
  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    echo "$1=$2" >> "$GITHUB_OUTPUT"
  fi
}

output from "$FROM"
output to "$TO"
output valid false

status=0
run() {
  echo "::group::$*"
  "$@"
  local code=$?
  echo "::endgroup::"
  if [[ $code -ne 0 ]]; then
    echo "::error::Falhou (código $code): $*"
    status=1
  fi
}

echo "Atualização de $FROM a $TO"
run leis-portugal collect dre --from "$FROM" --to "$TO"
run leis-portugal collect eurlex --from "$FROM" --to "$TO" --workers 4
run leis-portugal link

echo "::group::leis-portugal validate"
if ! leis-portugal validate; then
  echo "::endgroup::"
  echo "::error::A validação do acervo falhou; os dados não devem ser publicados."
  exit 2
fi
echo "::endgroup::"
output valid true

run leis-portugal reports
exit $status
