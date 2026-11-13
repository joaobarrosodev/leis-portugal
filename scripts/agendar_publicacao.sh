#!/usr/bin/env bash
# Agenda no Mac (launchd) a publicação semanal do índice: scripts/publicar_indice.sh, ao domingo às 04:00.
# Se o Mac estiver a dormir ou desligado a essa hora, corre quando acordar.
#
#   scripts/agendar_publicacao.sh            # agendar (ou voltar a agendar)
#   scripts/agendar_publicacao.sh --tirar    # deixar de agendar
#
# Usa sempre a pasta principal do repositório, mesmo que corras isto a partir de uma worktree.
set -euo pipefail

ROTULO=pt.leis-portugal.publicar-indice
PLIST="$HOME/Library/LaunchAgents/$ROTULO.plist"

if [[ "${1:-}" == "--tirar" ]]; then
  launchctl bootout "gui/$(id -u)/$ROTULO" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Publicação semanal tirada."
  exit 0
fi

RAIZ="$(dirname "$(git -C "$(dirname "$0")" rev-parse --path-format=absolute --git-common-dir)")"
if [[ ! -x "$RAIZ/.venv/bin/python" ]]; then
  echo "Não encontro $RAIZ/.venv: corre primeiro ./perguntar na pasta principal."
  exit 1
fi
if [[ ! -f "$RAIZ/scripts/publicar_indice.sh" ]]; then
  echo "A pasta principal ainda não tem scripts/publicar_indice.sh: faz git pull em $RAIZ."
  exit 1
fi
if ! "$RAIZ/.venv/bin/hf" auth whoami >/dev/null 2>&1; then
  echo "Sem sessão no Hugging Face: corre \"$RAIZ/.venv/bin/hf\" auth login"
  exit 1
fi

mkdir -p "$(dirname "$PLIST")"
cat >"$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$ROTULO</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$RAIZ/scripts/publicar_indice.sh</string></array>
  <key>StartCalendarInterval</key>
  <dict><key>Weekday</key><integer>0</integer><key>Hour</key><integer>4</integer><key>Minute</key><integer>0</integer></dict>
  <key>WorkingDirectory</key><string>$RAIZ</string>
  <key>LowPriorityIO</key><true/>
  <key>Nice</key><integer>10</integer>
</dict>
</plist>
EOF
launchctl bootout "gui/$(id -u)/$ROTULO" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Agendado: domingo às 04:00, em $RAIZ."
echo "Registo: $RAIZ/rag/resultados/privado/publicacao.log"
echo "Para correr já: launchctl kickstart gui/$(id -u)/$ROTULO"
