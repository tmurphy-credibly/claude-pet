// Pure config / rules / pet logic for Claude Pet. No GNOME imports, so it can be
// unit-tested with Node (see test/test-config.mjs).

export const DEFAULTS = {
    pet: 'crab',
    look: {
        pixelSize: 4,        // screen px per pet pixel
        margin: 20,          // px from the screen edge
        bubbleWidth: 280,
        glow: true,          // status-colored bar under the pet
        showHint: true,      // "Click me to open the terminal"
        tickMs: 150,         // animation tick
    },
    timing: {
        staleAfterHours: 12, // ignore sessions with no events for this long
    },
    defaultMood: 'idle',
    // priority: higher wins when several sessions are running.
    // after: switch to another mood once the event is this old.
    // sprite: which pet sprite to use if the pet has none for this mood.
    moods: {
        needs: {label: 'Needs you', color: '#FFC233', priority: 60, text: 'Needs your attention.', bubble: true, bob: true, blink: true},
        error: {label: 'Oops', color: '#FF6B5E', priority: 50, text: 'Something failed. Take a peek?', bubble: true, bob: false},
        working: {label: 'Working', color: '#FF9A6B', priority: 40, text: 'Working…', bubble: true, bob: true},
        thinking: {label: 'Thinking', color: '#6FA3FF', priority: 30, text: 'Hmm, let me think…', bubble: true, bob: true},
        done: {label: 'Done', color: '#6BCB7A', priority: 20, text: 'All done. Your turn.', bubble: true, bob: true,
            after: {seconds: 120, mood: 'idle'}},
        idle: {label: 'Idle', color: '#B9B7AE', priority: 10, text: 'Ready when you are.', bubble: false, bob: true,
            after: {seconds: 600, mood: 'sleeping'}},
        sleeping: {label: 'Sleeping', color: '#9C8FE0', priority: 0, text: 'zz…', bubble: false, bob: false},
    },
    // First matching rule wins. Match fields: event (exact), tool / type / project /
    // match (regex on detail). A rule sets a mood, or "ignore": true keeps the
    // previous mood. text / detail are templates: {tool} {detail} {message} {project} {type} {event}.
    rules: [
        {event: 'SessionStart', mood: 'idle'},
        {event: 'UserPromptSubmit', mood: 'thinking'},
        {event: 'PreToolUse', mood: 'working', text: 'Running {tool}'},
        {event: 'PostToolUse', mood: 'thinking'},
        {event: 'PostToolUseFailure', mood: 'error', text: '{tool} failed. Take a peek?'},
        {event: 'PermissionRequest', mood: 'needs', text: 'Can I run {tool}?'},
        {event: 'Notification', type: '^(idle_prompt|permission_prompt)$', ignore: true},
        {event: 'Notification', mood: 'needs', text: '{message}', detail: ''},
        {event: 'PreCompact', mood: 'thinking', text: 'Compacting memory…'},
        {event: 'Stop', mood: 'done'},
        {event: 'StopFailure', mood: 'error', text: 'That turn failed. Take a peek?'},
    ],
};

const isObject = v => v !== null && typeof v === 'object' && !Array.isArray(v);

export function deepMerge(base, over) {
    if (!isObject(base) || !isObject(over))
        return over === undefined ? base : over;
    const out = {...base};
    for (const [k, v] of Object.entries(over))
        out[k] = isObject(v) && isObject(base[k]) ? deepMerge(base[k], v) : v;
    return out;
}

// User rules go in front of the defaults (so they win), unless replaceRules is set.
// Returns {config, warnings}; throws on a config that cannot work.
export function buildConfig(user = {}) {
    if (!isObject(user))
        throw new Error('config.json must be a JSON object');
    const {rules: userRules, replaceRules, ...rest} = user;
    const config = deepMerge(DEFAULTS, rest);
    if (userRules !== undefined && !Array.isArray(userRules))
        throw new Error('"rules" must be a list');
    config.rules = replaceRules ? [...(userRules ?? [])] : [...(userRules ?? []), ...DEFAULTS.rules];

    const warnings = [];
    for (const [name, mood] of Object.entries(config.moods)) {
        if (!isObject(mood))
            throw new Error(`mood "${name}" must be an object`);
        mood.priority = Number(mood.priority ?? 0);
        if (mood.after && !config.moods[mood.after.mood])
            warnings.push(`mood "${name}" decays to unknown mood "${mood.after.mood}"`);
    }
    if (!config.moods[config.defaultMood])
        throw new Error(`defaultMood "${config.defaultMood}" is not a defined mood`);

    config.rules = config.rules.map((rule, i) => {
        if (!isObject(rule) || typeof rule.event !== 'string')
            throw new Error(`rule ${i + 1} needs an "event"`);
        if (!rule.ignore && !config.moods[rule.mood])
            throw new Error(`rule ${i + 1} (${rule.event}) uses unknown mood "${rule.mood}"`);
        const compiled = {...rule, _re: {}};
        for (const field of ['tool', 'type', 'project', 'match']) {
            if (rule[field] === undefined)
                continue;
            try {
                compiled._re[field] = new RegExp(rule[field]);
            } catch (e) {
                throw new Error(`rule ${i + 1} (${rule.event}): bad ${field} regex: ${e.message}`);
            }
        }
        return compiled;
    });
    return {config, warnings};
}

export function fill(template, ev) {
    return String(template ?? '').replace(/\{(\w+)\}/g, (_, key) => (ev[key] ?? '').toString());
}

export function matchRule(rules, ev) {
    const fields = {tool: ev.tool, type: ev.type, project: ev.project, match: ev.detail};
    return rules.find(rule => rule.event === ev.event &&
        Object.entries(rule._re).every(([field, re]) => re.test(fields[field] ?? ''))) ?? null;
}

// Maps one raw hook event to a session state, given the previous state (or null).
export function resolveEvent(config, ev, prev) {
    const rule = matchRule(config.rules, ev);
    if (!rule || rule.ignore)
        return prev ?? {mood: config.defaultMood, text: '', detail: '', ts: ev.ts};
    return {
        mood: rule.mood,
        text: rule.text !== undefined ? fill(rule.text, ev) : '',
        detail: fill(rule.detail ?? '{detail}', ev),
        ts: ev.ts,
    };
}

// Applies "after" decay chains, then fills in the mood's default text.
export function effectiveState(config, state, now) {
    let {mood, text, detail} = state;
    const age = now - state.ts;
    for (let hops = 0; hops < 10; hops++) {
        const after = config.moods[mood]?.after;
        if (!after || !config.moods[after.mood] || age <= after.seconds)
            break;
        mood = after.mood;
        text = '';
        detail = '';
    }
    if (!config.moods[mood])
        mood = config.defaultMood;
    return {mood, text: text || config.moods[mood].text || '', detail, age};
}

// ---------- pets ----------

// Used only when no pet file can be loaded at all, so the extension still starts.
export const FALLBACK_PET = {
    name: 'Fallback',
    palette: {B: '#D97757', E: '#141413'},
    moods: {idle: {frames: [[
        '..BBBBBB..',
        '.BBBBBBBB.',
        '.BBEBBEBB.',
        '.BBBBBBBB.',
        '..B.BB.B..',
    ]]}},
};

// Pet JSON: {name, palette: {char: "#hex"}, moods: {mood: {frames: [[row, ...], ...], fps}}}.
// '.' and ' ' are transparent; '*' is the current mood's color.
export function parsePet(json) {
    if (!isObject(json) || !isObject(json.moods))
        throw new Error('pet needs a "moods" object');
    const palette = json.palette ?? {};
    let width = 0;
    let height = 0;
    const moods = {};
    for (const [mood, spec] of Object.entries(json.moods)) {
        const frames = spec?.frames;
        if (!Array.isArray(frames) || frames.length === 0)
            throw new Error(`pet mood "${mood}" needs at least one frame`);
        moods[mood] = {
            fps: Number(spec.fps ?? 2),
            frames: frames.map((rows, f) => {
                if (!Array.isArray(rows))
                    throw new Error(`pet mood "${mood}" frame ${f + 1} must be a list of rows`);
                height = Math.max(height, rows.length);
                const runs = [];
                rows.forEach((row, y) => {
                    width = Math.max(width, row.length);
                    let x = 0;
                    while (x < row.length) {
                        const ch = row[x];
                        let end = x + 1;
                        while (end < row.length && row[end] === ch)
                            end++;
                        if (ch !== '.' && ch !== ' ') {
                            if (ch !== '*' && !palette[ch])
                                throw new Error(`pet mood "${mood}": "${ch}" is not in the palette`);
                            runs.push({x, y, w: end - x, color: ch === '*' ? '*' : palette[ch]});
                        }
                        x = end;
                    }
                });
                return runs;
            }),
        };
    }
    if (!moods.idle)
        throw new Error('pet needs at least an "idle" mood');
    return {name: json.name ?? 'pet', width, height, moods};
}

export function spriteFor(pet, config, mood) {
    return pet.moods[mood] ?? pet.moods[config.moods[mood]?.sprite] ?? pet.moods.idle;
}

export function frameIndex(sprite, ms) {
    return Math.floor((ms * sprite.fps) / 1000) % sprite.frames.length;
}
