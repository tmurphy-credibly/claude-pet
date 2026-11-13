// Claude Pet: a pixel pet in a screen corner that mirrors Claude Code's state.
//
// Inputs:
//   ~/.cache/claude-pet/sessions/*.json  latest hook event per session (hooks/claude-pet-hook.sh)
//   ~/.config/claude-pet/config.json     optional overrides of config.js DEFAULTS (live reload)
//   ~/.config/claude-pet/pets/*.json     optional custom pets (override built-in ./pets/*.json)
//   ~/.config/claude-pet/state.json      runtime toggles (hidden, side), written by the extension

import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import St from 'gi://St';
import Clutter from 'gi://Clutter';
import Meta from 'gi://Meta';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

import {buildConfig, resolveEvent, effectiveState, parsePet, spriteFor, frameIndex} from './config.js';

const STATE_DIR = GLib.build_filenamev([GLib.get_user_cache_dir(), 'claude-pet', 'sessions']);
const CONFIG_DIR = GLib.build_filenamev([GLib.get_user_config_dir(), 'claude-pet']);
const CONFIG_FILE = GLib.build_filenamev([CONFIG_DIR, 'config.json']);
const USER_PETS_DIR = GLib.build_filenamev([CONFIG_DIR, 'pets']);
const TOGGLES_FILE = GLib.build_filenamev([CONFIG_DIR, 'state.json']);

const TERMINAL_RE = /ptyxis|terminal|kitty|alacritty|wezterm|konsole|ghostty|tilix|foot/i;
const decoder = new TextDecoder();
const encoder = new TextEncoder();

function readJson(path) {
    const [, bytes] = GLib.file_get_contents(path);
    return JSON.parse(decoder.decode(bytes));
}

function hexToRgb(hex) {
    const n = parseInt(String(hex).replace('#', ''), 16) || 0;
    return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
}

export default class ClaudePetExtension extends Extension {
    enable() {
        this._toggles = this._loadToggles();
        this._sessions = [];
        this._memory = new Map(); // session file -> {eventKey, state}
        this._mood = 'sleeping';
        this._startMs = Date.now();
        this._hover = false;
        this._lastConfigError = null;

        GLib.mkdir_with_parents(STATE_DIR, 0o700);
        GLib.mkdir_with_parents(USER_PETS_DIR, 0o700);

        this._loadConfig();
        this._buildUi();
        this._buildIndicator();

        this._monitors = [
            this._watch(STATE_DIR, () => this._schedule('_refreshId', 150, () => this._refresh())),
            this._watch(CONFIG_DIR, (_m, file) => {
                if (file?.get_basename() === 'config.json')
                    this._schedule('_reloadId', 300, () => this._reload());
            }),
            this._watch(USER_PETS_DIR, () => this._schedule('_reloadId', 300, () => this._reload())),
        ];

        this._startTimers();
        this._monitorsChangedId = Main.layoutManager.connect('monitors-changed', () => this._place());
        this._refresh();
    }

    disable() {
        this._stopTimers();
        for (const [monitor, id] of this._monitors ?? []) {
            monitor.disconnect(id);
            monitor.cancel();
        }
        this._monitors = [];
        if (this._monitorsChangedId) {
            Main.layoutManager.disconnect(this._monitorsChangedId);
            this._monitorsChangedId = 0;
        }
        if (this._box) {
            Main.layoutManager.removeChrome(this._box);
            this._box.destroy();
        }
        this._indicator?.destroy();
        this._indicator = this._panelPet = this._statusItem = null;
        this._box = this._crab = null;
        this._sessions = [];
        this._memory = null;
        this._config = this._pet = null;
    }

    // ---------- timers & watching ----------

    _watch(path, onChange) {
        const monitor = Gio.File.new_for_path(path).monitor_directory(Gio.FileMonitorFlags.NONE, null);
        return [monitor, monitor.connect('changed', onChange)];
    }

    _schedule(key, ms, fn) {
        if (this[key])
            return;
        this[key] = GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => {
            this[key] = 0;
            fn();
            return GLib.SOURCE_REMOVE;
        });
    }

    _startTimers() {
        this._stopTimers();
        this._tickId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, this._config.look.tickMs, () => {
            this._crab?.queue_repaint();
            this._panelPet?.queue_repaint();
            return GLib.SOURCE_CONTINUE;
        });
        this._decayId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 5, () => {
            this._refresh();
            return GLib.SOURCE_CONTINUE;
        });
    }

    _stopTimers() {
        for (const key of ['_tickId', '_decayId', '_refreshId', '_reloadId']) {
            if (this[key])
                GLib.source_remove(this[key]);
            this[key] = 0;
        }
    }

    // ---------- config & pets ----------

    // Loads config.json + the chosen pet. On error keeps the last good setup
    // (or the defaults on first load) and says why in a notification.
    _loadConfig() {
        try {
            const user = GLib.file_test(CONFIG_FILE, GLib.FileTest.EXISTS) ? readJson(CONFIG_FILE) : {};
            const {config, warnings} = buildConfig(user);
            const pet = this._loadPet(config.pet);
            this._config = config;
            this._pet = pet;
            this._lastConfigError = null;
            for (const w of warnings)
                console.warn(`claude-pet: ${w}`);
        } catch (e) {
            this._reportConfigError(e.message);
            if (!this._config) {
                this._config = buildConfig({}).config;
                this._pet = this._loadPet(this._config.pet);
            }
        }
    }

    _loadPet(name) {
        if (!/^[\w-]+$/.test(String(name)))
            throw new Error(`pet name "${name}" may only use letters, digits, - and _`);
        const candidates = [
            GLib.build_filenamev([USER_PETS_DIR, `${name}.json`]),
            GLib.build_filenamev([this.path, 'pets', `${name}.json`]),
        ];
        const path = candidates.find(p => GLib.file_test(p, GLib.FileTest.EXISTS));
        if (!path)
            throw new Error(`no pet named "${name}" in ${USER_PETS_DIR} or the built-in pets`);
        try {
            return parsePet(readJson(path));
        } catch (e) {
            throw new Error(`${path}: ${e.message}`);
        }
    }

    _reportConfigError(message) {
        console.warn(`claude-pet: ${message}`);
        if (message === this._lastConfigError)
            return;
        this._lastConfigError = message;
        try {
            Main.notify('Claude Pet config error', `${message}\nKeeping the previous settings.`);
        } catch (e) {
            // Notifications unavailable; the journal has it.
        }
    }

    _reload() {
        this._loadConfig();
        this._memory.clear(); // re-map every session with the new rules
        this._startTimers();
        this._applyLook();
        this._refresh();
    }

    // ---------- UI ----------

    _buildUi() {
        this._box = new St.BoxLayout({
            orientation: Clutter.Orientation.VERTICAL,
            style_class: 'claude-pet',
            reactive: true,
            track_hover: true,
        });
        // The shell can destroy chrome on exit before disable() runs.
        this._box.connect('destroy', () => {
            this._stopTimers();
            this._box = this._crab = null;
        });
        this._box.connect('notify::hover', () => {
            this._hover = this._box.hover;
            this._updateUi();
        });

        this._toolbar = new St.BoxLayout({style_class: 'claude-pet-toolbar'});
        this._toolbar.add_child(this._toolButton('view-conceal-symbolic', 'Hide pet', () => this._setToggle('hidden', true)));
        this._toolbar.add_child(this._toolButton('object-flip-horizontal-symbolic', 'Switch corner', () =>
            this._setToggle('side', this._toggles.side === 'left' ? 'right' : 'left')));
        this._box.add_child(this._toolbar);

        this._bubble = new St.BoxLayout({
            orientation: Clutter.Orientation.VERTICAL,
            style_class: 'claude-pet-bubble',
        });
        const titleRow = new St.BoxLayout({style_class: 'claude-pet-title-row'});
        this._dot = new St.Widget({style_class: 'claude-pet-dot', y_align: Clutter.ActorAlign.CENTER});
        this._title = new St.Label({style_class: 'claude-pet-title'});
        titleRow.add_child(this._dot);
        titleRow.add_child(this._title);
        this._text = this._wrappedLabel('claude-pet-text');
        this._detail = this._wrappedLabel('claude-pet-detail');
        this._others = this._wrappedLabel('claude-pet-sessions');
        this._hint = new St.Label({style_class: 'claude-pet-hint', text: 'Click me to open the terminal'});
        for (const child of [titleRow, this._text, this._detail, this._others, this._hint])
            this._bubble.add_child(child);

        this._bubbleButton = new St.Button({
            style_class: 'claude-pet-bubble-button',
            child: this._bubble,
            accessible_name: 'Open the terminal',
        });
        this._bubbleButton.connect('clicked', () => this._raiseTerminal());
        this._box.add_child(this._bubbleButton);

        this._crab = new St.DrawingArea();
        this._crab.connect('repaint', area => this._paint(area, true));
        this._crabButton = new St.Button({
            style_class: 'claude-pet-crab',
            child: this._crab,
            accessible_name: 'Claude pet',
        });
        this._crabButton.connect('clicked', () => {
            if (this._toggles.hidden)
                this._setToggle('hidden', false);
            else
                this._raiseTerminal();
        });
        this._box.add_child(this._crabButton);

        Main.layoutManager.addChrome(this._box, {trackFullscreen: true});
    }

    // Top-bar menu: a tiny live pet that opens the controls.
    _buildIndicator() {
        this._indicator = new PanelMenu.Button(0.0, 'Claude Pet', false);
        this._panelPet = new St.DrawingArea({y_align: Clutter.ActorAlign.CENTER});
        this._panelPet.connect('repaint', area => this._paint(area, false));
        this._indicator.add_child(this._panelPet);

        const menu = this._indicator.menu;
        this._statusItem = new PopupMenu.PopupMenuItem('', {reactive: false});
        menu.addMenuItem(this._statusItem);
        menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        this._showItem = new PopupMenu.PopupSwitchMenuItem('Show pet on desktop', this._toggles.shown);
        this._showItem.connect('toggled', (_item, state) => this._setToggle('shown', state));
        menu.addMenuItem(this._showItem);

        this._tuckItem = new PopupMenu.PopupSwitchMenuItem('Tuck at screen edge', this._toggles.hidden);
        this._tuckItem.connect('toggled', (_item, state) => this._setToggle('hidden', state));
        menu.addMenuItem(this._tuckItem);

        this._cornerItem = new PopupMenu.PopupMenuItem('');
        this._cornerItem.connect('activate', () =>
            this._setToggle('side', this._toggles.side === 'left' ? 'right' : 'left'));
        menu.addMenuItem(this._cornerItem);

        this._petMenu = new PopupMenu.PopupSubMenuMenuItem('Pet');
        menu.addMenuItem(this._petMenu);

        menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        menu.addAction('Edit config…', () => this._openConfig());
        menu.addAction('Open pets folder', () => this._openPath(USER_PETS_DIR));
        menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        menu.addAction('Turn off Claude Pet', () => {
            // Defer: disabling destroys this menu while it is still handling the click.
            GLib.idle_add(GLib.PRIORITY_DEFAULT, () => {
                Main.extensionManager.disableExtension(this.uuid);
                return GLib.SOURCE_REMOVE;
            });
        });

        menu.connect('open-state-changed', (_menu, open) => {
            if (open)
                this._syncMenu();
        });
        Main.panel.addToStatusArea(this.uuid, this._indicator);
        this._applyLook();
    }

    _syncMenu() {
        if (!this._indicator)
            return;
        const top = this._sessions[0];
        const label = this._config.moods[this._mood].label ?? this._mood;
        const others = this._sessions.length > 1 ? ` (+${this._sessions.length - 1} more)` : '';
        this._statusItem.label.text = top ? `${label} · ${top.project}${others}` : 'No Claude sessions running';
        this._showItem.setToggleState(this._toggles.shown);
        this._tuckItem.setToggleState(this._toggles.hidden);
        this._cornerItem.label.text = this._toggles.side === 'left'
            ? 'Move to bottom-right corner' : 'Move to bottom-left corner';

        this._petMenu.menu.removeAll();
        for (const name of this._listPets()) {
            const item = new PopupMenu.PopupMenuItem(name);
            item.setOrnament(name === this._config.pet ? PopupMenu.Ornament.DOT : PopupMenu.Ornament.NONE);
            item.connect('activate', () => this._choosePet(name));
            this._petMenu.menu.addMenuItem(item);
        }
    }

    _listPets() {
        const names = new Set();
        for (const dir of [GLib.build_filenamev([this.path, 'pets']), USER_PETS_DIR]) {
            try {
                const e = Gio.File.new_for_path(dir).enumerate_children('standard::name', Gio.FileQueryInfoFlags.NONE, null);
                let info;
                while ((info = e.next_file(null))) {
                    const name = info.get_name();
                    if (name.endsWith('.json'))
                        names.add(name.slice(0, -5));
                }
                e.close(null);
            } catch (e) {
                // Missing folder: nothing to list.
            }
        }
        return [...names].sort();
    }

    // Writes the choice into config.json; the file monitor then reloads it.
    _choosePet(name) {
        try {
            const user = GLib.file_test(CONFIG_FILE, GLib.FileTest.EXISTS) ? readJson(CONFIG_FILE) : {};
            user.pet = name;
            GLib.file_set_contents(CONFIG_FILE, encoder.encode(`${JSON.stringify(user, null, 2)}\n`));
        } catch (e) {
            this._reportConfigError(`could not update ${CONFIG_FILE}: ${e.message}`);
        }
    }

    _openConfig() {
        if (!GLib.file_test(CONFIG_FILE, GLib.FileTest.EXISTS))
            GLib.file_set_contents(CONFIG_FILE, encoder.encode(`${JSON.stringify({pet: this._config.pet}, null, 2)}\n`));
        this._openPath(CONFIG_FILE);
    }

    _openPath(path) {
        try {
            Gio.AppInfo.launch_default_for_uri(GLib.filename_to_uri(path, null), null);
        } catch (e) {
            Main.notify('Claude Pet', `Could not open ${path}: ${e.message}`);
        }
    }

    _applyLook() {
        if (!this._box)
            return;
        const {pixelSize, bubbleWidth, glow} = this._config.look;
        this._crab.set_size(this._pet.width * pixelSize, (this._pet.height + (glow ? 2 : 0)) * pixelSize);
        this._panelPet?.set_size(Math.round((16 * this._pet.width) / this._pet.height), 16);
        this._bubble.style = `width: ${bubbleWidth}px;`;
        this._updateUi();
    }

    _toolButton(iconName, label, onClick) {
        const button = new St.Button({
            style_class: 'claude-pet-tool',
            accessible_name: label,
            child: new St.Icon({icon_name: iconName, icon_size: 16}),
        });
        button.connect('clicked', onClick);
        return button;
    }

    _wrappedLabel(styleClass) {
        const label = new St.Label({style_class: styleClass});
        label.clutter_text.line_wrap = true;
        label.clutter_text.ellipsize = 0; // Pango.EllipsizeMode.NONE
        return label;
    }

    _updateUi() {
        if (!this._box)
            return;

        const moods = this._config.moods;
        const top = this._sessions[0];
        const mood = this._mood;
        const moodCfg = moods[mood];
        const hidden = this._toggles.hidden;
        const shown = this._toggles.shown;
        const align = this._toggles.side === 'left' ? Clutter.ActorAlign.START : Clutter.ActorAlign.END;

        // Hide the children, not the box: trackFullscreen manages the box's own visibility.
        this._crabButton.visible = shown;
        this._toolbar.visible = shown && !hidden && this._hover;
        this._bubbleButton.visible = shown && !hidden && (this._hover || Boolean(top && moodCfg.bubble));
        for (const actor of [this._toolbar, this._bubbleButton, this._crabButton])
            actor.x_align = align;

        this._dot.style = `background-color: ${moodCfg.color};`;
        this._title.text = top ? `${moodCfg.label ?? mood} · ${top.project}` : (moodCfg.label ?? mood);
        this._text.text = top ? top.text : 'No Claude sessions running.';
        this._detail.text = top?.detail || '';
        this._detail.visible = Boolean(top?.detail);

        const others = this._sessions.slice(1).map(s => `${s.project} · ${moods[s.mood].label ?? s.mood}`);
        this._others.text = others.join('\n');
        this._others.visible = others.length > 0;
        this._hint.visible = Boolean(top) && this._config.look.showHint;

        this._crab.queue_repaint();
        this._panelPet?.queue_repaint();
        if (this._indicator?.menu.isOpen)
            this._syncMenu();
        this._place();
    }

    _place() {
        if (!this._box || !Main.layoutManager.primaryMonitor)
            return;

        const {margin} = this._config.look;
        const monitor = Main.layoutManager.primaryMonitor;
        const workArea = Main.layoutManager.getWorkAreaForMonitor(Main.layoutManager.primaryIndex);
        const [, width] = this._box.get_preferred_width(-1);
        const [, height] = this._box.get_preferred_height(width);

        const x = this._toggles.side === 'left'
            ? workArea.x + margin
            : workArea.x + workArea.width - width - margin;

        let y;
        if (this._toggles.hidden) {
            // Peek over the bottom edge; rise higher for the most urgent moods.
            const urgent = this._config.moods[this._mood].priority >= this._config.moods.needs?.priority;
            y = monitor.y + monitor.height - Math.round(this._crab.height * (urgent ? 0.65 : 0.45));
        } else {
            y = workArea.y + workArea.height - height - margin;
        }
        this._box.set_position(Math.round(x), Math.round(y));
    }

    // desktop = the big pet (glow + bob); false = the small top-bar pet.
    _paint(area, desktop) {
        const cr = area.get_context();
        const [w, h] = area.get_surface_size();
        const glow = desktop && this._config.look.glow;
        const gridH = this._pet.height + (glow ? 2 : 0);
        const scale = Math.min(w / this._pet.width, h / gridH);
        cr.scale(scale, scale);

        const mood = this._mood;
        const moodCfg = this._config.moods[mood];
        const ms = Date.now() - this._startMs;
        const bob = desktop && moodCfg.bob && Math.floor(ms / 1200) % 2 ? -0.5 : 0;
        const dim = moodCfg.blink && Math.floor(ms / 300) % 3 === 0;
        const [mr, mg, mb] = hexToRgb(moodCfg.color);

        if (glow) {
            cr.setSourceRGBA(mr, mg, mb, dim ? 0.25 : 0.9);
            cr.rectangle(1, this._pet.height + 1, this._pet.width - 2, 1);
            cr.fill();
        }

        const sprite = spriteFor(this._pet, this._config, mood);
        for (const run of sprite.frames[frameIndex(sprite, ms)]) {
            if (run.color === '*')
                cr.setSourceRGBA(mr, mg, mb, dim ? 0.3 : 1);
            else
                cr.setSourceRGBA(...hexToRgb(run.color), 1);
            cr.rectangle(run.x, run.y + bob, run.w, 1);
            cr.fill();
        }
        cr.$dispose();
    }

    // ---------- sessions ----------

    _refresh() {
        if (!this._config)
            return;
        const now = Math.floor(Date.now() / 1000);
        const staleS = this._config.timing.staleAfterHours * 3600;
        const sessions = [];
        const seen = new Set();

        let enumerator = null;
        try {
            enumerator = Gio.File.new_for_path(STATE_DIR)
                .enumerate_children('standard::name', Gio.FileQueryInfoFlags.NONE, null);
        } catch (e) {
            enumerator = null;
        }

        if (enumerator) {
            let info;
            while ((info = enumerator.next_file(null))) {
                const name = info.get_name();
                if (!name.endsWith('.json'))
                    continue;
                const path = GLib.build_filenamev([STATE_DIR, name]);
                try {
                    const ev = readJson(path);
                    ev.ts = Number(ev.ts) || 0;
                    if (now - ev.ts > 2 * staleS) {
                        Gio.File.new_for_path(path).delete(null);
                        continue;
                    }
                    seen.add(name);

                    // Map each new event once; ignored events keep the previous state.
                    const eventKey = `${ev.ts}:${ev.event}:${ev.tool}:${ev.type}`;
                    let entry = this._memory.get(name);
                    if (!entry || entry.eventKey !== eventKey) {
                        entry = {eventKey, state: resolveEvent(this._config, ev, entry?.state ?? null)};
                        this._memory.set(name, entry);
                    }
                    if (now - entry.state.ts > staleS)
                        continue;
                    sessions.push({project: ev.project || 'claude', ...effectiveState(this._config, entry.state, now)});
                } catch (e) {
                    // Half-written or unreadable file: skip until the next change.
                }
            }
            enumerator.close(null);
        }

        for (const key of [...this._memory.keys()]) {
            if (!seen.has(key))
                this._memory.delete(key);
        }

        const moods = this._config.moods;
        sessions.sort((a, b) => moods[b.mood].priority - moods[a.mood].priority || a.age - b.age);
        this._sessions = sessions;
        this._mood = sessions[0]?.mood ?? (moods.sleeping ? 'sleeping' : this._config.defaultMood);
        this._updateUi();
    }

    // ---------- actions ----------

    _raiseTerminal() {
        const windows = global.display.get_tab_list(Meta.TabList.NORMAL_ALL, null)
            .filter(w => TERMINAL_RE.test(`${w.get_wm_class() ?? ''} ${w.get_gtk_application_id?.() ?? ''}`));
        if (windows.length === 0)
            return;

        const project = this._sessions[0]?.project;
        const match = project && windows.find(w => (w.get_title() ?? '').includes(project));
        Main.activateWindow(match || windows[0]);
    }

    // ---------- runtime toggles ----------

    _setToggle(key, value) {
        this._toggles[key] = value;
        try {
            GLib.file_set_contents(TOGGLES_FILE, encoder.encode(JSON.stringify(this._toggles)));
        } catch (e) {
            console.warn(`claude-pet: could not save ${TOGGLES_FILE}: ${e.message}`);
        }
        this._updateUi();
    }

    _loadToggles() {
        const defaults = {shown: true, hidden: false, side: 'right'};
        try {
            return {...defaults, ...readJson(TOGGLES_FILE)};
        } catch (e) {
            return defaults;
        }
    }
}
