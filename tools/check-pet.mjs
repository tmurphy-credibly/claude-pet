#!/usr/bin/env node
// Validates a pet file and previews it in the terminal.
// Usage: node tools/check-pet.mjs path/to/pet.json [mood]
import {readFileSync} from 'node:fs';
import {buildConfig, parsePet} from '../extension/claude-pet@tmurphy-credibly.github.io/config.js';

const [path, onlyMood] = process.argv.slice(2);
if (!path) {
    console.error('Usage: node tools/check-pet.mjs path/to/pet.json [mood]');
    process.exit(2);
}

let raw;
let pet;
try {
    raw = JSON.parse(readFileSync(path, 'utf8'));
    pet = parsePet(raw);
} catch (e) {
    console.error(`✗ ${path}: ${e.message}`);
    process.exit(1);
}

const {config} = buildConfig({});
const defaults = Object.keys(config.moods);
const missing = defaults.filter(m => !pet.moods[m]);
const extra = Object.keys(pet.moods).filter(m => !defaults.includes(m));

console.log(`✓ ${pet.name}: ${pet.width}×${pet.height} pixels`);
console.log(`  moods: ${Object.keys(pet.moods).map(m => `${m} (${pet.moods[m].frames.length})`).join(', ')}`);
if (missing.length)
    console.log(`  missing (will fall back to idle): ${missing.join(', ')}`);
if (extra.length)
    console.log(`  custom moods (need a matching "moods" entry in config.json): ${extra.join(', ')}`);

// Terminal preview: two half-height pixels per character cell, true color.
const rgb = hex => [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16));
function grid(runs, w, h, star) {
    const g = Array.from({length: h}, () => Array(w).fill(null));
    for (const r of runs) {
        for (let x = r.x; x < r.x + r.w; x++)
            g[r.y][x] = r.color === '*' ? star : r.color;
    }
    return g;
}
function show(name, frame) {
    const g = grid(frame, pet.width, pet.height, config.moods[name]?.color ?? '#888888');
    console.log(`\n  ${name}`);
    for (let y = 0; y < pet.height; y += 2) {
        let line = '  ';
        for (let x = 0; x < pet.width; x++) {
            const top = g[y][x];
            const bottom = y + 1 < pet.height ? g[y + 1][x] : null;
            if (!top && !bottom) {
                line += ' ';
            } else if (top && bottom) {
                line += `\x1b[38;2;${rgb(top).join(';')}m\x1b[48;2;${rgb(bottom).join(';')}m▀\x1b[0m`;
            } else {
                line += `\x1b[38;2;${rgb(top ?? bottom).join(';')}m${top ? '▀' : '▄'}\x1b[0m`;
            }
        }
        console.log(line);
    }
}
for (const [name, sprite] of Object.entries(pet.moods)) {
    if (!onlyMood || onlyMood === name)
        sprite.frames.forEach((f, i) => show(sprite.frames.length > 1 ? `${name} · frame ${i + 1}` : name, f));
}
