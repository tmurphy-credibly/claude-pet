# Records one Claude Code hook event (stdin JSON) as raw facts for the pet.
# Mood mapping lives in the extension's config, not here.

def short($n): (. // "" | tostring | gsub("\\s+"; " ") | if length > $n then .[0:($n - 1)] + "…" else . end);

def tooldetail:
  (.tool_input // {}) as $i
  | if .tool_name == "Bash" then $i.command | short(80)
    elif ($i.file_path // $i.notebook_path // $i.path) then (($i.file_path // $i.notebook_path // $i.path) | tostring | split("/") | last)
    elif $i.pattern then $i.pattern | short(40)
    elif $i.url then $i.url | short(60)
    elif $i.description then $i.description | short(60)
    else "" end;

(.cwd // "") as $cwd
| {
    session_id: .session_id,
    event: (.hook_event_name // ""),
    tool: (.tool_name // ""),
    type: (.notification_type // ""),
    message: (.message | short(120)),
    detail: tooldetail,
    cwd: $cwd,
    project: ($cwd | split("/") | map(select(. != "")) | last // "claude"),
    ts: $ts
  }
| select(.event != "")
