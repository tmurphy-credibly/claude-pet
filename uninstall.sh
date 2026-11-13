#!/usr/bin/env bash
# Removes Claude Pet's hooks and GNOME extension.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
uuid="claude-pet@tmurphy-credibly.github.io"
hook="$root/hooks/claude-pet-hook.sh"
settings="$HOME/.claude/settings.json"

if [ -f "$settings" ]; then
  jq --arg cmd "$hook" '
    if .hooks then
      .hooks |= (with_entries(.value |= map(select(any(.hooks[]?; .command == $cmd) | not)))
                 | with_entries(select(.value | length > 0)))
    else . end
  ' "$settings" >"$settings.tmp"
  mv "$settings.tmp" "$settings"
fi

gnome-extensions disable "$uuid" 2>/dev/null || true
current="$(gsettings get org.gnome.shell enabled-extensions)"
updated="$(sed -E "s/, '$uuid'//; s/'$uuid', //; s/'$uuid'//" <<<"$current")"
gsettings set org.gnome.shell enabled-extensions "$updated"

rm -f "$HOME/.local/share/gnome-shell/extensions/$uuid"
rm -rf "${XDG_CACHE_HOME:-$HOME/.cache}/claude-pet"
echo "Claude Pet removed."
