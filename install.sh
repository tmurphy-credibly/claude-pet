#!/usr/bin/env bash
# Installs Claude Pet: links the GNOME extension, enables it, and registers
# the Claude Code hooks in ~/.claude/settings.json (backup kept). Idempotent.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
uuid="claude-pet@tmurphy-credibly.github.io"
hook="$root/hooks/claude-pet-hook.sh"
settings="$HOME/.claude/settings.json"
events='["SessionStart","UserPromptSubmit","PreToolUse","PostToolUse","PostToolUseFailure","PermissionRequest","Notification","PreCompact","Stop","StopFailure","SessionEnd"]'

for tool in jq gsettings gnome-extensions; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 1; }
done
shell_major="$(gnome-shell --version 2>/dev/null | grep -oE '[0-9]+' | head -1 || true)"
supported="$(jq -r '."shell-version" | join(", ")' "$root/extension/$uuid/metadata.json")"
if [[ ",$(jq -r '."shell-version" | join(",")' "$root/extension/$uuid/metadata.json")," != *",$shell_major,"* ]]; then
  echo "Warning: GNOME Shell ${shell_major:-unknown} detected; this extension is tested on GNOME $supported." >&2
  echo "         GNOME will refuse to load it until shell-version in metadata.json includes your version." >&2
fi

chmod +x "$hook"

# 1. GNOME extension
ext_dir="$HOME/.local/share/gnome-shell/extensions"
mkdir -p "$ext_dir"
ln -sfn "$root/extension/$uuid" "$ext_dir/$uuid"

# Clean up the pre-release ID (claude-pet@tmurphy) if present.
legacy="claude-pet@tmurphy"
if [ -L "$ext_dir/$legacy" ] || [ -d "$ext_dir/$legacy" ]; then
  gnome-extensions disable "$legacy" 2>/dev/null || true
  rm -rf "$ext_dir/$legacy"
fi

original="$(gsettings get org.gnome.shell enabled-extensions)"
current="$(sed -E "s/, '$legacy'//; s/'$legacy', //; s/'$legacy'//" <<<"$original")"
if [[ "$current" != *"'$uuid'"* ]]; then
  if [[ "$current" == "@as []" || "$current" == "[]" ]]; then
    current="['$uuid']"
  else
    current="${current%]}, '$uuid']"
  fi
fi
[ "$current" != "$original" ] && gsettings set org.gnome.shell enabled-extensions "$current"

# 2. Claude Code hooks
[ -f "$settings" ] || echo '{}' >"$settings"
cp "$settings" "$settings.bak-claude-pet"
jq --arg cmd "$hook" --argjson events "$events" '
  .hooks //= {}
  | reduce $events[] as $e (.;
      .hooks[$e] = (
        (.hooks[$e] // [])
        | map(select(any(.hooks[]?; .command == $cmd) | not))
        | . + [{hooks: [{type: "command", command: $cmd, timeout: 5}]}]
      ))
' "$settings" >"$settings.tmp"
mv "$settings.tmp" "$settings"

echo "Installed. Hooks are live for new Claude Code sessions."
echo "Log out and back in once so GNOME Shell loads the extension."
echo "Settings backup: $settings.bak-claude-pet"
