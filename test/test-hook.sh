#!/usr/bin/env bash
# Feeds sample hook payloads to the hook and checks the recorded raw event.
set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
hook="$root/hooks/claude-pet-hook.sh"
export XDG_CACHE_HOME="$(mktemp -d)"
trap 'rm -rf "$XDG_CACHE_HOME"' EXIT
state="$XDG_CACHE_HOME/claude-pet/sessions/abc-123.json"
fail=0

send() { bash "$hook" <<<"$1"; }
expect() { # field expected label
  local got
  got="$(jq -r ".$1" "$state" 2>/dev/null)"
  if [ "$got" == "$2" ]; then echo "ok   $3"; else echo "FAIL $3: .$1 = '$got', want '$2'"; fail=1; fi
}

base='"session_id":"abc-123","cwd":"/home/me/code/credibly-dev"'

out="$(send "{$base,\"hook_event_name\":\"SessionStart\"}")"
[ -z "$out" ] && echo "ok   hook prints nothing" || { echo "FAIL hook printed: $out"; fail=1; }
expect event SessionStart "event recorded"
expect project credibly-dev "project from cwd"
expect session_id abc-123 "session id recorded"

send "{$base,\"hook_event_name\":\"PreToolUse\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"uv run --all-groups pytest\"}}"
expect tool Bash "tool recorded"
expect detail "uv run --all-groups pytest" "Bash detail is the command"

send "{$base,\"hook_event_name\":\"PreToolUse\",\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"/a/b/extension.js\"}}"
expect detail "extension.js" "file tool detail is the basename"

send "{$base,\"hook_event_name\":\"Notification\",\"notification_type\":\"permission_prompt\",\"message\":\"Claude needs your permission to use Bash\"}"
expect type permission_prompt "notification type recorded"
expect message "Claude needs your permission to use Bash" "notification message recorded"

send 'not json'
expect event Notification "garbage input is ignored"

send "{$base,\"hook_event_name\":\"SessionEnd\"}"
if [ ! -e "$state" ]; then echo "ok   SessionEnd removes the file"; else echo "FAIL SessionEnd left the file"; fail=1; fi

send '{"session_id":"../../evil","hook_event_name":"Stop","cwd":"/x"}'
if [ -e "$XDG_CACHE_HOME/claude-pet/sessions/evil.json" ] && [ ! -e "$XDG_CACHE_HOME/evil.json" ]; then
  echo "ok   session id is sanitized"
else
  echo "FAIL session id sanitizing"; fail=1
fi

exit $fail
