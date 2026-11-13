// Unit tests for extension config logic. Run: node test/test-config.mjs
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {
    buildConfig, resolveEvent, effectiveState, parsePet, spriteFor, frameIndex, fill,
} from '../extension/claude-pet@tmurphy-credibly.github.io/config.js';

const ext = fileURLToPath(new URL('../extension/claude-pet@tmurphy-credibly.github.io/', import.meta.url));
let failed = 0;
function test(name, fn) {
    try {
        fn();
        console.log(`ok   ${name}`);
    } catch (e) {
        failed++;
        console.log(`FAIL ${name}: ${e.message}`);
    }
}

const ev = (event, extra = {}) => ({event, tool: '', type: '', message: '', detail: '', project: 'credibly-dev', ts: 1000, ...extra});
const {config} = buildConfig({});

test('defaults map the standard events', () => {
    assert.equal(resolveEvent(config, ev('UserPromptSubmit'), null).mood, 'thinking');
    const s = resolveEvent(config, ev('PreToolUse', {tool: 'Bash', detail: 'uv run pytest'}), null);
    assert.deepEqual([s.mood, s.text, s.detail], ['working', 'Running Bash', 'uv run pytest']);
    assert.equal(resolveEvent(config, ev('PermissionRequest', {tool: 'Edit'}), null).text, 'Can I run Edit?');
    assert.equal(resolveEvent(config, ev('Stop'), null).mood, 'done');
});

test('ignored events keep the previous state', () => {
    const prev = {mood: 'needs', text: 'Can I run Bash?', detail: 'rm x', ts: 900};
    assert.equal(resolveEvent(config, ev('Notification', {type: 'permission_prompt'}), prev), prev);
    assert.equal(resolveEvent(config, ev('Notification', {type: 'idle_prompt'}), prev), prev);
    assert.equal(resolveEvent(config, ev('SubagentStop'), prev), prev);
});

test('other notifications become needs with the message', () => {
    const s = resolveEvent(config, ev('Notification', {type: 'elicitation_dialog', message: 'Pick one'}), null);
    assert.deepEqual([s.mood, s.text], ['needs', 'Pick one']);
});

test('unknown first event falls back to the default mood', () => {
    assert.equal(resolveEvent(config, ev('SubagentStop'), null).mood, 'idle');
});

test('decay chain done -> idle -> sleeping', () => {
    const s = {mood: 'done', text: 'All done. Your turn.', detail: '', ts: 1000};
    assert.equal(effectiveState(config, s, 1100).mood, 'done');
    const idle = effectiveState(config, s, 1200);
    assert.deepEqual([idle.mood, idle.text], ['idle', 'Ready when you are.']);
    assert.equal(effectiveState(config, s, 1700).mood, 'sleeping');
});

test('empty rule text falls back to the mood text', () => {
    assert.equal(effectiveState(config, resolveEvent(config, ev('Stop'), null), 1000).text, 'All done. Your turn.');
});

test('user rules win, custom moods work, templates fill', () => {
    const {config: c} = buildConfig({
        moods: {testing: {label: 'Testing', color: '#00AAFF', priority: 45, text: 'Testing…', sprite: 'working', bubble: true}},
        rules: [{event: 'PreToolUse', tool: '^Bash$', match: 'pytest', mood: 'testing', text: 'Testing {project}'}],
    });
    const s = resolveEvent(c, ev('PreToolUse', {tool: 'Bash', detail: 'uv run pytest -x'}), null);
    assert.deepEqual([s.mood, s.text], ['testing', 'Testing credibly-dev']);
    assert.equal(resolveEvent(c, ev('PreToolUse', {tool: 'Bash', detail: 'ls'}), null).mood, 'working');
    assert.equal(c.rules.length, config.rules.length + 1);
});

test('mood overrides deep-merge', () => {
    const {config: c} = buildConfig({moods: {done: {text: 'Yay!'}}, look: {pixelSize: 6}});
    assert.equal(c.moods.done.text, 'Yay!');
    assert.equal(c.moods.done.color, '#6BCB7A');
    assert.equal(c.look.pixelSize, 6);
    assert.equal(c.look.margin, 20);
});

test('replaceRules replaces the defaults', () => {
    const {config: c} = buildConfig({replaceRules: true, rules: [{event: 'Stop', mood: 'done'}]});
    assert.equal(c.rules.length, 1);
});

test('bad configs are rejected with a clear message', () => {
    assert.throws(() => buildConfig({rules: [{event: 'Stop', mood: 'party'}]}), /unknown mood "party"/);
    assert.throws(() => buildConfig({rules: [{mood: 'done'}]}), /needs an "event"/);
    assert.throws(() => buildConfig({rules: [{event: 'Stop', mood: 'done', tool: '('}]}), /bad tool regex/);
    assert.throws(() => buildConfig({defaultMood: 'nope'}), /defaultMood/);
    assert.throws(() => buildConfig([]), /JSON object/);
});

test('fill leaves unknown placeholders empty', () => {
    assert.equal(fill('{tool}:{nope}', {tool: 'Bash'}), 'Bash:');
});

for (const name of ['crab', 'robot', 'cat', 'turtle', 'dog', 'penguin', 'duck', 'frog', 'owl', 'fox', 'bunny']) {
    test(`built-in pet "${name}" parses with every default mood`, () => {
        const pet = parsePet(JSON.parse(readFileSync(`${ext}pets/${name}.json`, 'utf8')));
        assert.equal(pet.width, 22);
        assert.equal(pet.height, 16);
        for (const mood of Object.keys(config.moods))
            assert.ok(pet.moods[mood], `missing ${mood}`);
    });
}

test('pet parsing: runs, palette, * color, errors', () => {
    const pet = parsePet({palette: {B: '#111111'}, moods: {idle: {frames: [['.BB*', 'B..']]}}});
    assert.deepEqual(pet.moods.idle.frames[0], [
        {x: 1, y: 0, w: 2, color: '#111111'}, {x: 3, y: 0, w: 1, color: '*'}, {x: 0, y: 1, w: 1, color: '#111111'},
    ]);
    assert.throws(() => parsePet({moods: {idle: {frames: [['X']]}}}), /not in the palette/);
    assert.throws(() => parsePet({moods: {working: {frames: [['.']]}}}), /"idle"/);
});

test('sprite fallback and frame timing', () => {
    const pet = parsePet({palette: {B: '#111111'}, moods: {
        idle: {frames: [['B']]}, working: {fps: 2, frames: [['B'], ['.B']]},
    }});
    const {config: c} = buildConfig({moods: {testing: {color: '#000000', priority: 1, sprite: 'working'}}});
    assert.equal(spriteFor(pet, c, 'testing'), pet.moods.working);
    assert.equal(spriteFor(pet, c, 'needs'), pet.moods.idle);
    assert.equal(frameIndex(pet.moods.working, 0), 0);
    assert.equal(frameIndex(pet.moods.working, 600), 1);
});

process.exit(failed ? 1 : 0);
