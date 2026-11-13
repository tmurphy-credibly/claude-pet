#!/usr/bin/env bash
# Claude Code hook for Claude Pet: records each session's latest event in
# ~/.cache/claude-pet/sessions/<session_id>.json for the GNOME extension.
# Prints nothing and always exits 0, so it can never block or alter Claude.

dir="${XDG_CACHE_HOME:-$HOME/.cache}/claude-pet/sessions"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$dir" 2>/dev/null || exit 0

input="$(cat)"
event="$(jq -r '.hook_event_name // ""' <<<"$input" 2>/dev/null)" || exit 0
sid="$(jq -r '.session_id // ""' <<<"$input" 2>/dev/null)" || exit 0
sid="${sid//[^A-Za-z0-9_-]/}"
[ -n "$sid" ] || exit 0
file="$dir/$sid.json"

if [ "$event" = "SessionEnd" ]; then
  rm -f "$file"
  exit 0
fi

tmp="$file.$$.tmp"
if jq -c --argjson ts "$(date +%s)" -f "$here/pet-state.jq" <<<"$input" >"$tmp" 2>/dev/null && [ -s "$tmp" ]; then
  mv -f "$tmp" "$file"
fi
rm -f "$tmp"
exit 0
