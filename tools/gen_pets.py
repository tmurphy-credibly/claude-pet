"""Generates the built-in pixel-art pets. Usage: python3 tools/gen_pets.py extension/claude-pet@tmurphy-credibly.github.io/pets"""
import json
import sys

out_dir = sys.argv[1]


def render(w, h, rects):
    grid = [["." for _ in range(w)] for _ in range(h)]
    for x, y, rw, rh, ch in rects:
        for yy in range(y, y + rh):
            for xx in range(x, x + rw):
                if 0 <= xx < w and 0 <= yy < h:
                    grid[yy][xx] = ch
    return ["".join(r) for r in grid]


def pet(name, description, w, h, palette, base, moods):
    out = {"name": name, "description": description, "palette": palette, "moods": {}}
    for mood, spec in moods.items():
        frames = [render(w, h, base + f) for f in spec["frames"]]
        entry = {"frames": frames}
        if "fps" in spec:
            entry["fps"] = spec["fps"]
        out["moods"][mood] = entry
    return out


def shift_up(rects):
    return [(x, y - 1, rw, rh, c) for x, y, rw, rh, c in rects]


# ---------- crab ----------
cb = [(4, 5, 14, 8, "B"), (5, 13, 1, 3, "B"), (7, 13, 1, 3, "B"), (14, 13, 1, 3, "B"), (16, 13, 1, 3, "B")]
arms_idle = [(2, 8, 2, 2, "B"), (18, 8, 2, 2, "B")]
arms_work = [(1, 9, 3, 2, "B"), (18, 9, 3, 2, "B")]
arms_up = [(2, 2, 2, 6, "B"), (18, 2, 2, 6, "B")]
z = [(18, 1, 3, 1, "z"), (19, 2, 1, 1, "z"), (18, 3, 3, 1, "z")]
crab_moods = {
    "idle": {"frames": [arms_idle + [(7, 7, 1, 2, "E"), (14, 7, 1, 2, "E")]]},
    "thinking": {"frames": [[(2, 8, 2, 2, "B"), (18, 6, 2, 2, "B"), (8, 6, 1, 2, "E"), (15, 6, 1, 2, "E"),
                             (19, 3, 1, 1, "t"), (20, 0, 2, 2, "t")]]},
    "working": {"fps": 3, "frames": [
        arms_work + [(7, 8, 1, 2, "E"), (14, 8, 1, 2, "E")],
        shift_up(arms_work) + [(7, 8, 1, 2, "E"), (14, 8, 1, 2, "E")],
    ]},
    "needs": {"fps": 3, "frames": [
        arms_up + [(7, 7, 2, 2, "E"), (13, 7, 2, 2, "E"), (10, 0, 2, 2, "a"), (10, 3, 2, 1, "a")],
        shift_up(arms_up) + [(7, 7, 2, 2, "E"), (13, 7, 2, 2, "E"), (10, 0, 2, 2, "a"), (10, 3, 2, 1, "a")],
    ]},
    "done": {"frames": [[(2, 8, 2, 2, "B"), (18, 3, 2, 5, "B"),
                         (6, 8, 1, 1, "E"), (7, 7, 1, 1, "E"), (8, 8, 1, 1, "E"),
                         (13, 8, 1, 1, "E"), (14, 7, 1, 1, "E"), (15, 8, 1, 1, "E")]]},
    "error": {"frames": [[(2, 10, 2, 2, "B"), (18, 10, 2, 2, "B"),
                          (6, 7, 1, 1, "E"), (8, 7, 1, 1, "E"), (7, 8, 1, 1, "E"), (6, 9, 1, 1, "E"), (8, 9, 1, 1, "E"),
                          (13, 7, 1, 1, "E"), (15, 7, 1, 1, "E"), (14, 8, 1, 1, "E"), (13, 9, 1, 1, "E"), (15, 9, 1, 1, "E")]]},
    "sleeping": {"fps": 1, "frames": [
        [(2, 9, 2, 2, "B"), (18, 9, 2, 2, "B"), (6, 9, 3, 1, "E"), (13, 9, 3, 1, "E")] + z,
        [(2, 9, 2, 2, "B"), (18, 9, 2, 2, "B"), (6, 9, 3, 1, "E"), (13, 9, 3, 1, "E")],
    ]},
}
crab = pet("Crab", "Pixel crab in the Claude Code mascot style.", 22, 16,
           {"B": "#D97757", "E": "#141413", "t": "#2A5DB0", "a": "#8A5A00", "z": "#5B4B9A"}, cb, crab_moods)

# ---------- robot ----------
rb = [(10, 2, 2, 1, "V"), (4, 3, 14, 9, "B"), (2, 6, 2, 3, "D"), (18, 6, 2, 3, "D"),
      (6, 5, 10, 5, "V"), (7, 12, 8, 4, "D"), (10, 13, 2, 1, "*")]
antenna = [(10, 0, 2, 2, "*")]
robot_moods = {
    "idle": {"frames": [antenna + [(8, 6, 1, 3, "W"), (13, 6, 1, 3, "W")]]},
    "thinking": {"frames": [antenna + [(9, 5, 1, 2, "W"), (14, 5, 1, 2, "W"), (19, 2, 1, 1, "t"), (20, 0, 2, 2, "t")]]},
    "working": {"fps": 3, "frames": [
        antenna + [(7, 7, 3, 1, "W"), (12, 7, 3, 1, "W")],
        antenna + [(7, 8, 3, 1, "W"), (12, 8, 3, 1, "W")],
    ]},
    "needs": {"fps": 3, "frames": [
        antenna + [(8, 6, 2, 2, "W"), (12, 6, 2, 2, "W"), (20, 3, 1, 3, "a"), (20, 7, 1, 1, "a")],
        antenna + [(8, 6, 2, 2, "W"), (12, 6, 2, 2, "W")],
    ]},
    "done": {"frames": [antenna + [(7, 7, 1, 1, "W"), (8, 6, 1, 1, "W"), (9, 7, 1, 1, "W"),
                                   (12, 7, 1, 1, "W"), (13, 6, 1, 1, "W"), (14, 7, 1, 1, "W")]]},
    "error": {"frames": [antenna + [(7, 6, 1, 1, "W"), (9, 6, 1, 1, "W"), (8, 7, 1, 1, "W"), (7, 8, 1, 1, "W"), (9, 8, 1, 1, "W"),
                                    (12, 6, 1, 1, "W"), (14, 6, 1, 1, "W"), (13, 7, 1, 1, "W"), (12, 8, 1, 1, "W"), (14, 8, 1, 1, "W")]]},
    "sleeping": {"fps": 1, "frames": [
        antenna + [(7, 8, 3, 1, "W"), (12, 8, 3, 1, "W")] + z,
        antenna + [(7, 8, 3, 1, "W"), (12, 8, 3, 1, "W")],
    ]},
}
robot = pet("Robot", "Boxy robot; antenna and chest light show the status color.", 22, 16,
            {"B": "#D97757", "D": "#B85A38", "V": "#141413", "W": "#FAF9F5", "t": "#2A5DB0", "a": "#FFC233", "z": "#9C8FE0"},
            rb, robot_moods)

# ---------- cat ----------
# '.' rects clear pixels (used to lift a paw off the floor row).
cat_base = [
    (5, 2, 12, 7, "B"), (4, 4, 14, 4, "B"),                        # head + cheeks
    (6, 9, 10, 6, "B"), (5, 12, 12, 3, "B"),                       # body
    (9, 10, 4, 5, "L"),                                            # belly
    (8, 2, 1, 2, "S"), (10, 2, 2, 1, "S"), (13, 2, 1, 2, "S"),     # forehead "M"
    (4, 5, 2, 1, "S"), (16, 5, 2, 1, "S"),                         # cheek stripes
    (6, 10, 2, 1, "S"), (14, 10, 2, 1, "S"), (5, 13, 2, 1, "S"), (15, 13, 2, 1, "S"),  # side stripes
    (6, 15, 3, 1, "W"), (13, 15, 3, 1, "W"),                       # paws
    (10, 7, 2, 1, "p"),                                            # nose
    (2, 6, 2, 1, "w"), (2, 7, 2, 1, "w"), (18, 6, 2, 1, "w"), (18, 7, 2, 1, "w"),  # whiskers
]
ears = [(5, 0, 1, 1, "B"), (5, 1, 2, 1, "B"), (6, 1, 1, 1, "p"),
        (16, 0, 1, 1, "B"), (15, 1, 2, 1, "B"), (15, 1, 1, 1, "p")]
ears_flat = [(3, 2, 3, 1, "B"), (16, 2, 3, 1, "B")]
tail_rest = [(17, 14, 3, 1, "B"), (19, 11, 1, 3, "B"), (19, 12, 1, 1, "S"), (18, 14, 1, 1, "S")]
tail_up = [(17, 14, 2, 1, "B"), (18, 10, 1, 4, "B"), (19, 9, 1, 1, "B"), (18, 11, 1, 1, "S"), (18, 13, 1, 1, "S")]
eyes_open = [(7, 5, 2, 2, "Y"), (8, 5, 1, 2, "E"), (13, 5, 2, 2, "Y"), (14, 5, 1, 2, "E")]
eyes_up = [(7, 5, 2, 2, "Y"), (8, 5, 1, 1, "E"), (13, 5, 2, 2, "Y"), (14, 5, 1, 1, "E")]
eyes_narrow = [(7, 6, 2, 1, "Y"), (8, 6, 1, 1, "E"), (13, 6, 2, 1, "Y"), (14, 6, 1, 1, "E")]
eyes_big = [(6, 4, 3, 3, "Y"), (7, 4, 1, 3, "E"), (13, 4, 3, 3, "Y"), (14, 4, 1, 3, "E")]
eyes_happy = [(7, 6, 1, 1, "E"), (8, 5, 1, 1, "E"), (9, 6, 1, 1, "E"),
              (12, 6, 1, 1, "E"), (13, 5, 1, 1, "E"), (14, 6, 1, 1, "E")]
eyes_x = [(7, 4, 1, 1, "E"), (9, 4, 1, 1, "E"), (8, 5, 1, 1, "E"), (7, 6, 1, 1, "E"), (9, 6, 1, 1, "E"),
          (12, 4, 1, 1, "E"), (14, 4, 1, 1, "E"), (13, 5, 1, 1, "E"), (12, 6, 1, 1, "E"), (14, 6, 1, 1, "E")]
eyes_shut = [(7, 6, 2, 1, "E"), (13, 6, 2, 1, "E")]
knead_left = [(6, 15, 3, 1, "."), (6, 14, 3, 1, "W")]
knead_right = [(13, 15, 3, 1, "."), (13, 14, 3, 1, "W")]
heart = [(18, 1, 1, 1, "h"), (20, 1, 1, 1, "h"), (18, 2, 3, 1, "h"), (19, 3, 1, 1, "h")]
bang = [(20, 0, 1, 3, "a"), (20, 4, 1, 1, "a")]
cat_moods = {
    "idle": {"fps": 1, "frames": [ears + tail_rest + eyes_open, ears + tail_rest + eyes_open,
                                  ears + tail_rest + eyes_open, ears + tail_rest + eyes_shut]},  # slow blink
    "thinking": {"frames": [ears + tail_rest + eyes_up + [(19, 3, 1, 1, "t"), (20, 0, 2, 2, "t")]]},
    "working": {"fps": 3, "frames": [ears + tail_rest + eyes_narrow + knead_left,
                                      ears + tail_up + eyes_narrow + knead_right]},
    "needs": {"fps": 3, "frames": [ears + tail_up + eyes_big + bang, ears + tail_rest + eyes_big + bang]},
    "done": {"fps": 1, "frames": [ears + tail_up + eyes_happy + heart, ears + tail_up + eyes_happy]},
    "error": {"frames": [ears_flat + tail_rest + eyes_x]},
    "sleeping": {"fps": 1, "frames": [ears + tail_rest + eyes_shut + z, ears + tail_rest + eyes_shut]},
}
cat = pet("Cat", "Orange tabby: kneads while working, slow-blinks when idle.", 22, 16,
          {"B": "#E8913A", "S": "#B35E1C", "L": "#F6E3C8", "W": "#FBF8F2", "Y": "#6CC070", "E": "#141413",
           "p": "#D9607A", "w": "#FBF8F2", "t": "#2A5DB0", "a": "#8A5A00", "h": "#E0546B", "z": "#5B4B9A"},
          cat_base, cat_moods)

# ---------- turtle (side view, facing right) ----------
turtle_base = [
    (6, 3, 7, 1, "G"), (5, 4, 9, 1, "G"), (4, 5, 11, 1, "G"), (3, 6, 13, 4, "G"),   # shell dome
    (4, 7, 11, 1, "D"), (8, 4, 1, 3, "D"), (12, 4, 1, 3, "D"),                   # scutes
    (6, 8, 1, 2, "D"), (10, 8, 1, 2, "D"), (14, 8, 1, 2, "D"),
    (2, 10, 15, 1, "R"), (3, 11, 13, 1, "Y"),                                    # rim + belly
    (0, 10, 2, 1, "K"),                                                          # tail
]
legs_stand = [(6, 12, 2, 2, "k"), (14, 12, 2, 2, "k"), (4, 12, 2, 3, "K"), (12, 12, 2, 3, "K")]
legs_walk_a = [(5, 12, 2, 2, "k"), (15, 12, 2, 2, "k"), (3, 12, 2, 3, "K"), (13, 12, 2, 3, "K")]
legs_walk_b = [(7, 12, 2, 2, "k"), (13, 12, 2, 2, "k"), (5, 12, 2, 3, "K"), (11, 12, 2, 3, "K")]
legs_tucked = [(4, 12, 2, 1, "K"), (12, 12, 2, 1, "K")]
head_normal = [(16, 8, 2, 2, "K"), (17, 6, 4, 4, "K")]
head_up = [(16, 7, 2, 2, "K"), (17, 4, 4, 4, "K")]
head_out = [(16, 8, 3, 2, "K"), (18, 5, 4, 4, "K")]
head_down = [(16, 9, 2, 2, "K"), (17, 10, 4, 3, "K")]
t_eye = [(19, 7, 1, 1, "E")]
t_blink = [(18, 8, 2, 1, "E")]
turtle_moods = {
    "idle": {"fps": 1, "frames": [legs_stand + head_normal + t_eye, legs_stand + head_normal + t_eye,
                                  legs_stand + head_normal + t_eye, legs_stand + head_normal + t_blink]},
    "thinking": {"frames": [legs_stand + head_up + [(19, 5, 1, 1, "E"), (21, 2, 1, 1, "t"), (19, 0, 2, 2, "t")]]},
    "working": {"fps": 3, "frames": [legs_walk_a + head_normal + [(19, 8, 1, 1, "E")],
                                      legs_walk_b + head_normal + [(19, 8, 1, 1, "E")]]},
    "needs": {"fps": 3, "frames": [
        legs_stand + head_out + [(19, 6, 2, 2, "W"), (20, 6, 1, 2, "E"), (17, 0, 1, 3, "a"), (17, 4, 1, 1, "a")],
        legs_stand + head_out + [(19, 6, 2, 2, "W"), (20, 6, 1, 2, "E")],
    ]},
    "done": {"fps": 1, "frames": [
        legs_stand + head_normal + [(18, 8, 1, 1, "E"), (19, 7, 1, 1, "E"), (20, 8, 1, 1, "E"),
                                    (18, 1, 1, 1, "h"), (20, 1, 1, 1, "h"), (18, 2, 3, 1, "h"), (19, 3, 1, 1, "h")],
        legs_stand + head_normal + [(18, 8, 1, 1, "E"), (19, 7, 1, 1, "E"), (20, 8, 1, 1, "E")],
    ]},
    "error": {"frames": [legs_stand + head_down + [(18, 10, 1, 1, "E"), (20, 10, 1, 1, "E"), (19, 11, 1, 1, "E"),
                                                   (18, 12, 1, 1, "E"), (20, 12, 1, 1, "E")]]},
    "sleeping": {"fps": 1, "frames": [legs_tucked + [(16, 9, 1, 1, "K")] + [(17, 1, 3, 1, "z"), (18, 2, 1, 1, "z"), (17, 3, 3, 1, "z")],
                                      legs_tucked + [(16, 9, 1, 1, "K")]]},
}
turtle = pet("Turtle", "Green turtle: walks while working, hides in its shell to sleep.", 22, 16,
             {"G": "#5A9A4E", "D": "#2E5E2A", "R": "#C9A24B", "Y": "#E9DCA4", "K": "#A3CF6E", "k": "#7FAA52",
              "E": "#141413", "W": "#FBF8F2", "t": "#2A5DB0", "a": "#8A5A00", "h": "#E0546B", "z": "#5B4B9A"},
             turtle_base, turtle_moods)

# ---------- dog (front view, sitting) ----------
dog_base = [
    (5, 2, 12, 7, "B"),                                            # head
    (6, 9, 10, 6, "B"), (5, 12, 12, 3, "B"),                       # body
    (9, 9, 4, 4, "W"),                                             # chest blaze
    (8, 6, 6, 3, "M"),                                             # muzzle
    (10, 6, 2, 1, "E"),                                            # nose
    (6, 15, 3, 1, "W"), (13, 15, 3, 1, "W"),                       # paws
]
ears_flop = [(3, 2, 2, 6, "D"), (17, 2, 2, 6, "D")]
ears_perk = [(4, 0, 2, 3, "D"), (16, 0, 2, 3, "D")]
ears_droop = [(3, 4, 2, 7, "D"), (17, 4, 2, 7, "D")]
dog_tail_a = [(17, 13, 3, 1, "B"), (19, 11, 1, 2, "B")]
dog_tail_b = [(17, 13, 2, 1, "B"), (18, 10, 1, 3, "B")]
d_eyes = [(7, 4, 2, 2, "E"), (7, 4, 1, 1, "W"), (13, 4, 2, 2, "E"), (13, 4, 1, 1, "W")]
d_eyes_up = [(7, 3, 2, 2, "E"), (7, 3, 1, 1, "W"), (13, 3, 2, 2, "E"), (13, 3, 1, 1, "W")]
d_eyes_big = [(6, 3, 3, 3, "E"), (6, 3, 1, 1, "W"), (13, 3, 3, 3, "E"), (13, 3, 1, 1, "W")]
d_eyes_shut = [(7, 5, 2, 1, "E"), (13, 5, 2, 1, "E")]
d_eyes_happy = [(6, 5, 1, 1, "E"), (7, 4, 1, 1, "E"), (8, 5, 1, 1, "E"), (13, 5, 1, 1, "E"), (14, 4, 1, 1, "E"), (15, 5, 1, 1, "E")]
d_eyes_x = [(6, 3, 1, 1, "E"), (8, 3, 1, 1, "E"), (7, 4, 1, 1, "E"), (6, 5, 1, 1, "E"), (8, 5, 1, 1, "E"),
            (13, 3, 1, 1, "E"), (15, 3, 1, 1, "E"), (14, 4, 1, 1, "E"), (13, 5, 1, 1, "E"), (15, 5, 1, 1, "E")]
mouth = []
tongue = [(10, 7, 2, 1, "E"), (10, 8, 2, 2, "T")]
dog_moods = {
    "idle": {"fps": 1, "frames": [ears_flop + dog_tail_a + d_eyes + mouth, ears_flop + dog_tail_a + d_eyes + mouth,
                                  ears_flop + dog_tail_a + d_eyes + mouth, ears_flop + dog_tail_a + d_eyes_shut + mouth]},
    "thinking": {"frames": [ears_flop + dog_tail_a + d_eyes_up + mouth + [(20, 0, 2, 2, "t"), (20, 3, 1, 1, "t")]]},
    "working": {"fps": 4, "frames": [ears_flop + dog_tail_a + d_eyes + tongue, ears_flop + dog_tail_b + d_eyes + tongue]},
    "needs": {"fps": 4, "frames": [ears_perk + dog_tail_a + d_eyes_big + mouth + [(20, 0, 1, 3, "a"), (20, 4, 1, 1, "a")],
                                   ears_perk + dog_tail_b + d_eyes_big + mouth]},
    "done": {"fps": 2, "frames": [
        ears_flop + dog_tail_a + d_eyes_happy + tongue + [(19, 0, 1, 1, "h"), (21, 0, 1, 1, "h"), (19, 1, 3, 1, "h"), (20, 2, 1, 1, "h")],
        ears_flop + dog_tail_b + d_eyes_happy + tongue,
    ]},
    "error": {"frames": [ears_droop + dog_tail_a + d_eyes_x + mouth]},
    "sleeping": {"fps": 1, "frames": [ears_flop + dog_tail_a + d_eyes_shut + mouth + z, ears_flop + dog_tail_a + d_eyes_shut + mouth]},
}
dog = pet("Dog", "Tan puppy: pants and wags while working, perks its ears when it needs you.", 22, 16,
          {"B": "#D9A066", "D": "#8B5A2B", "M": "#F3E1C2", "W": "#FBF8F2", "E": "#141413", "T": "#E77A8A",
           "t": "#2A5DB0", "a": "#8A5A00", "h": "#E0546B", "z": "#5B4B9A"},
          dog_base, dog_moods)

# ---------- penguin (front view) ----------
peng_base = [
    (8, 1, 6, 1, "K"), (7, 2, 8, 1, "K"), (6, 3, 10, 11, "K"), (7, 14, 8, 1, "K"),   # body
    (8, 3, 6, 4, "W"), (10, 3, 2, 1, "K"),                                           # face
    (8, 7, 6, 6, "W"), (9, 13, 4, 1, "W"),                                           # belly
    (10, 6, 2, 1, "O"),                                                              # beak
]
p_feet = [(7, 15, 3, 1, "O"), (12, 15, 3, 1, "O")]
p_step_l = [(7, 14, 3, 1, "O"), (12, 15, 3, 1, "O")]
p_step_r = [(7, 15, 3, 1, "O"), (12, 14, 3, 1, "O")]
fl_down = [(4, 6, 2, 5, "K"), (16, 6, 2, 5, "K")]
fl_out = [(3, 6, 3, 2, "K"), (16, 6, 3, 2, "K")]
fl_up = [(4, 2, 2, 5, "K"), (16, 2, 2, 5, "K")]
p_eyes = [(9, 4, 1, 2, "E"), (12, 4, 1, 2, "E")]
p_eyes_up = [(9, 3, 1, 2, "E"), (12, 3, 1, 2, "E")]
p_eyes_big = [(8, 4, 2, 2, "E"), (8, 4, 1, 1, "W"), (12, 4, 2, 2, "E"), (12, 4, 1, 1, "W")]
p_eyes_shut = [(8, 5, 2, 1, "E"), (12, 5, 2, 1, "E")]
p_eyes_happy = [(8, 5, 1, 1, "E"), (9, 4, 1, 1, "E"), (12, 4, 1, 1, "E"), (13, 5, 1, 1, "E")]
p_eyes_x = [(8, 3, 1, 1, "E"), (10, 3, 1, 1, "E"), (9, 4, 1, 1, "E"), (8, 5, 1, 1, "E"), (10, 5, 1, 1, "E"),
            (11, 3, 1, 1, "E"), (13, 3, 1, 1, "E"), (12, 4, 1, 1, "E"), (11, 5, 1, 1, "E"), (13, 5, 1, 1, "E")]
penguin_moods = {
    "idle": {"fps": 1, "frames": [fl_down + p_feet + p_eyes, fl_down + p_feet + p_eyes,
                                  fl_down + p_feet + p_eyes, fl_down + p_feet + p_eyes_shut]},
    "thinking": {"frames": [fl_down + p_feet + p_eyes_up + [(19, 0, 2, 2, "t"), (18, 3, 1, 1, "t")]]},
    "working": {"fps": 3, "frames": [fl_out + p_step_l + p_eyes, fl_down + p_step_r + p_eyes]},
    "needs": {"fps": 4, "frames": [fl_up + p_feet + p_eyes_big + [(19, 0, 1, 3, "a"), (19, 4, 1, 1, "a")],
                                   fl_out + p_feet + p_eyes_big]},
    "done": {"fps": 2, "frames": [
        fl_up + p_feet + p_eyes_happy + [(18, 0, 1, 1, "h"), (20, 0, 1, 1, "h"), (18, 1, 3, 1, "h"), (19, 2, 1, 1, "h")],
        fl_up + p_feet + p_eyes_happy,
    ]},
    "error": {"frames": [fl_down + p_feet + p_eyes_x]},
    "sleeping": {"fps": 1, "frames": [fl_down + p_feet + p_eyes_shut + z, fl_down + p_feet + p_eyes_shut]},
}
penguin = pet("Penguin", "Penguin: waddles while working, flaps when it needs you.", 22, 16,
              {"K": "#262A33", "W": "#FBF8F2", "O": "#F29A2E", "E": "#141413",
               "t": "#2A5DB0", "a": "#8A5A00", "h": "#E0546B", "z": "#5B4B9A"},
              peng_base, penguin_moods)

# ---------- duck (side view, facing right) ----------
duck_base = [
    (4, 7, 10, 1, "Y"), (3, 8, 13, 5, "Y"), (5, 13, 9, 1, "Y"),     # body
    (2, 7, 2, 1, "Y"), (1, 6, 2, 1, "Y"),                            # tail
]
dk_head = [(12, 2, 4, 1, "Y"), (11, 3, 6, 5, "Y"), (17, 5, 3, 1, "O"), (17, 6, 2, 1, "O")]
dk_head_up = [(12, 1, 4, 1, "Y"), (11, 2, 6, 5, "Y"), (17, 3, 3, 1, "O"), (17, 4, 2, 1, "O")]
dk_head_quack = [(12, 2, 4, 1, "Y"), (11, 3, 6, 5, "Y"), (17, 4, 3, 1, "O"), (17, 6, 3, 1, "O")]
dk_head_low = [(12, 4, 4, 1, "Y"), (11, 5, 6, 4, "Y"), (17, 7, 2, 1, "O")]
dk_wing = [(6, 9, 6, 2, "D")]
dk_wing_up = [(6, 5, 4, 4, "D")]
dk_feet = [(7, 14, 1, 1, "O"), (6, 15, 3, 1, "O"), (11, 14, 1, 1, "O"), (10, 15, 3, 1, "O")]
dk_step = [(6, 14, 3, 1, "O"), (11, 14, 1, 1, "O"), (10, 15, 3, 1, "O")]
dk_eye = [(15, 4, 1, 1, "E")]
duck_moods = {
    "idle": {"fps": 1, "frames": [dk_head + dk_wing + dk_feet + dk_eye, dk_head + dk_wing + dk_feet + dk_eye,
                                  dk_head + dk_wing + dk_feet + dk_eye, dk_head + dk_wing + dk_feet + [(14, 4, 2, 1, "E")]]},
    "thinking": {"frames": [dk_head_up + dk_wing + dk_feet + [(15, 2, 1, 1, "E"), (20, 0, 2, 2, "t")]]},
    "working": {"fps": 3, "frames": [dk_head + dk_wing + dk_step + dk_eye, dk_head + dk_wing_up + dk_feet + dk_eye]},
    "needs": {"fps": 4, "frames": [
        dk_head_quack + dk_wing_up + dk_feet + [(14, 3, 2, 2, "E"), (14, 3, 1, 1, "W"), (21, 0, 1, 3, "a"), (21, 4, 1, 1, "a")],
        dk_head_quack + dk_wing + dk_feet + [(14, 3, 2, 2, "E"), (14, 3, 1, 1, "W")],
    ]},
    "done": {"fps": 2, "frames": [
        dk_head + dk_wing_up + dk_feet + [(14, 4, 1, 1, "E"), (15, 3, 1, 1, "E"), (16, 4, 1, 1, "E"),
                                          (5, 1, 1, 1, "h"), (7, 1, 1, 1, "h"), (5, 2, 3, 1, "h"), (6, 3, 1, 1, "h")],
        dk_head + dk_wing_up + dk_feet + [(14, 4, 1, 1, "E"), (15, 3, 1, 1, "E"), (16, 4, 1, 1, "E")],
    ]},
    "error": {"frames": [dk_head + dk_wing + dk_feet + [(14, 3, 1, 1, "E"), (16, 3, 1, 1, "E"), (15, 4, 1, 1, "E"),
                                                       (14, 5, 1, 1, "E"), (16, 5, 1, 1, "E")]]},
    "sleeping": {"fps": 1, "frames": [dk_head_low + dk_wing + dk_feet + [(13, 6, 2, 1, "E")] + z,
                                      dk_head_low + dk_wing + dk_feet + [(13, 6, 2, 1, "E")]]},
}
duck = pet("Duck", "Yellow duckling: waddles while working, quacks and flaps when it needs you.", 22, 16,
           {"Y": "#F7D046", "D": "#E0A82E", "O": "#F08A24", "E": "#141413", "W": "#FBF8F2",
            "t": "#2A5DB0", "a": "#8A5A00", "h": "#E0546B", "z": "#5B4B9A"},
           duck_base, duck_moods)

# ---------- frog (front view, sitting) ----------
frog_base = [
    (5, 1, 4, 4, "G"), (13, 1, 4, 4, "G"),                              # eye bumps
    (5, 4, 12, 1, "G"), (3, 5, 16, 5, "G"), (4, 10, 14, 1, "G"), (5, 11, 12, 1, "G"),  # body
    (7, 8, 8, 3, "L"),                                                  # belly
    (2, 10, 3, 2, "G"), (1, 12, 3, 1, "G"), (17, 10, 3, 2, "G"), (18, 12, 3, 1, "G"),  # back legs
    (7, 12, 2, 2, "G"), (6, 14, 3, 1, "G"), (13, 12, 2, 2, "G"), (13, 14, 3, 1, "G"),  # front legs
]
fr_mouth = [(6, 7, 10, 1, "D")]
fr_smile = [(5, 6, 1, 1, "D"), (6, 7, 10, 1, "D"), (16, 6, 1, 1, "D")]
fr_frown = [(5, 8, 1, 1, "D"), (6, 7, 10, 1, "D"), (16, 8, 1, 1, "D")]
fr_eyes = [(6, 2, 2, 2, "W"), (7, 3, 1, 1, "E"), (14, 2, 2, 2, "W"), (14, 3, 1, 1, "E")]
fr_eyes_up = [(6, 2, 2, 2, "W"), (7, 2, 1, 1, "E"), (14, 2, 2, 2, "W"), (14, 2, 1, 1, "E")]
fr_eyes_big = [(5, 2, 4, 2, "W"), (6, 2, 2, 2, "E"), (13, 2, 4, 2, "W"), (14, 2, 2, 2, "E")]
fr_eyes_shut = [(6, 3, 2, 1, "E"), (14, 3, 2, 1, "E")]
fr_eyes_happy = [(5, 3, 1, 1, "E"), (6, 2, 2, 1, "E"), (8, 3, 1, 1, "E"), (13, 3, 1, 1, "E"), (14, 2, 2, 1, "E"), (16, 3, 1, 1, "E")]
fr_eyes_x = [(5, 1, 1, 1, "E"), (7, 1, 1, 1, "E"), (6, 2, 1, 1, "E"), (5, 3, 1, 1, "E"), (7, 3, 1, 1, "E"),
             (14, 1, 1, 1, "E"), (16, 1, 1, 1, "E"), (15, 2, 1, 1, "E"), (14, 3, 1, 1, "E"), (16, 3, 1, 1, "E")]
fr_fly = [(20, 2, 1, 1, "f")]
fr_tongue = [(16, 7, 1, 1, "P"), (17, 6, 1, 1, "P"), (18, 5, 1, 1, "P"), (19, 4, 1, 1, "P"), (20, 3, 1, 1, "P")]
fr_sac = [(7, 8, 8, 4, "S"), (8, 12, 6, 1, "S")]
frog_moods = {
    "idle": {"fps": 1, "frames": [fr_eyes + fr_mouth, fr_eyes + fr_mouth, fr_eyes + fr_mouth, fr_eyes_shut + fr_mouth]},
    "thinking": {"frames": [fr_eyes_up + fr_mouth + [(19, 0, 2, 2, "t"), (19, 3, 1, 1, "t")]]},
    "working": {"fps": 3, "frames": [fr_eyes + fr_mouth + fr_fly, fr_eyes + fr_mouth + fr_tongue]},
    "needs": {"fps": 3, "frames": [fr_eyes_big + fr_mouth + fr_sac + [(20, 0, 1, 3, "a"), (20, 4, 1, 1, "a")],
                                   fr_eyes_big + fr_mouth]},
    "done": {"fps": 2, "frames": [
        fr_eyes_happy + fr_smile + [(18, 0, 1, 1, "h"), (20, 0, 1, 1, "h"), (18, 1, 3, 1, "h"), (19, 2, 1, 1, "h")],
        fr_eyes_happy + fr_smile,
    ]},
    "error": {"frames": [fr_eyes_x + fr_frown]},
    "sleeping": {"fps": 1, "frames": [fr_eyes_shut + fr_mouth + [(18, 0, 3, 1, "z"), (19, 1, 1, 1, "z"), (18, 2, 3, 1, "z")],
                                      fr_eyes_shut + fr_mouth]},
}
frog = pet("Frog", "Green frog: snaps at flies while working, croaks when it needs you.", 22, 16,
           {"G": "#5DB84F", "D": "#2F6B28", "L": "#C8E6A0", "S": "#EAF6D6", "W": "#FBF8F2", "E": "#141413",
            "P": "#E06A7A", "f": "#141413", "t": "#2A5DB0", "a": "#8A5A00", "h": "#E0546B", "z": "#5B4B9A"},
           frog_base, frog_moods)

# ---------- owl (front view) ----------
owl_base = [
    (5, 0, 2, 2, "B"), (15, 0, 2, 2, "B"),                              # ear tufts
    (6, 2, 10, 1, "B"), (5, 3, 12, 10, "B"), (6, 13, 10, 1, "B"),       # body
    (6, 3, 4, 4, "F"), (12, 3, 4, 4, "F"),                              # facial discs
    (10, 5, 2, 2, "O"),                                                 # beak
    (8, 8, 6, 5, "L"), (9, 9, 1, 1, "D"), (12, 9, 1, 1, "D"), (10, 11, 1, 1, "D"), (13, 11, 1, 1, "D"),  # belly
    (7, 14, 3, 1, "O"), (12, 14, 3, 1, "O"),                            # talons
]
ow_wings = [(4, 6, 2, 6, "D"), (16, 6, 2, 6, "D")]
ow_spread = [(2, 4, 3, 5, "D"), (17, 4, 3, 5, "D")]
ow_left_eye = [(7, 4, 2, 2, "Y")]
ow_right_eye = [(13, 4, 2, 2, "Y")]
ow_eyes = ow_left_eye + ow_right_eye + [(8, 5, 1, 1, "E"), (13, 5, 1, 1, "E")]
ow_look_l = ow_left_eye + ow_right_eye + [(7, 5, 1, 1, "E"), (13, 5, 1, 1, "E")]
ow_look_r = ow_left_eye + ow_right_eye + [(8, 5, 1, 1, "E"), (14, 5, 1, 1, "E")]
ow_wink = [(7, 5, 2, 1, "E")] + ow_right_eye + [(13, 5, 1, 1, "E")]
ow_up = ow_left_eye + ow_right_eye + [(8, 4, 1, 1, "E"), (13, 4, 1, 1, "E")]
ow_big = [(6, 3, 4, 4, "Y"), (7, 4, 2, 2, "E"), (12, 3, 4, 4, "Y"), (13, 4, 2, 2, "E")]
ow_shut = [(7, 5, 2, 1, "E"), (13, 5, 2, 1, "E")]
ow_happy = [(6, 5, 1, 1, "E"), (7, 4, 2, 1, "E"), (9, 5, 1, 1, "E"), (12, 5, 1, 1, "E"), (13, 4, 2, 1, "E"), (15, 5, 1, 1, "E")]
ow_x = [(7, 3, 1, 1, "E"), (9, 3, 1, 1, "E"), (8, 4, 1, 1, "E"), (7, 5, 1, 1, "E"), (9, 5, 1, 1, "E"),
        (12, 3, 1, 1, "E"), (14, 3, 1, 1, "E"), (13, 4, 1, 1, "E"), (12, 5, 1, 1, "E"), (14, 5, 1, 1, "E")]
owl_moods = {
    "idle": {"fps": 1, "frames": [ow_wings + ow_eyes, ow_wings + ow_eyes, ow_wings + ow_eyes, ow_wings + ow_wink]},
    "thinking": {"frames": [ow_wings + ow_up + [(19, 0, 2, 2, "t"), (19, 3, 1, 1, "t")]]},
    "working": {"fps": 2, "frames": [ow_wings + ow_look_l, ow_wings + ow_look_r]},
    "needs": {"fps": 3, "frames": [ow_spread + ow_big + [(20, 0, 1, 3, "a"), (20, 4, 1, 1, "a")], ow_wings + ow_big]},
    "done": {"fps": 2, "frames": [
        ow_spread + ow_happy + [(18, 0, 1, 1, "h"), (20, 0, 1, 1, "h"), (18, 1, 3, 1, "h"), (19, 2, 1, 1, "h")],
        ow_wings + ow_happy,
    ]},
    "error": {"frames": [ow_wings + ow_x]},
    "sleeping": {"fps": 1, "frames": [ow_wings + ow_shut + [(18, 1, 3, 1, "z"), (19, 2, 1, 1, "z"), (18, 3, 3, 1, "z")],
                                      ow_wings + ow_shut]},
}
owl = pet("Owl", "Brown owl: eyes dart while working, spreads its wings when it needs you.", 22, 16,
          {"B": "#8A5A3C", "D": "#5E3B24", "F": "#E8D3B0", "L": "#D9B98F", "Y": "#F2C14E", "E": "#141413",
           "O": "#E8962E", "t": "#2A5DB0", "a": "#8A5A00", "h": "#E0546B", "z": "#5B4B9A"},
          owl_base, owl_moods)

# ---------- fox (front view, sitting) ----------
fox_base = [
    (5, 3, 12, 5, "R"), (7, 8, 8, 1, "R"),                              # head, narrowing to the snout
    (8, 6, 6, 3, "W"), (5, 6, 2, 2, "W"), (15, 6, 2, 2, "W"),           # muzzle + cheeks
    (10, 8, 2, 1, "K"),                                                 # nose
    (6, 9, 10, 5, "R"), (9, 9, 4, 4, "W"),                              # body + chest
    (7, 14, 2, 2, "K"), (13, 14, 2, 2, "K"),                            # dark socks
]
fx_ears = [(5, 0, 1, 1, "K"), (5, 1, 2, 1, "R"), (5, 2, 3, 1, "R"), (6, 2, 1, 1, "W"),
           (16, 0, 1, 1, "K"), (15, 1, 2, 1, "R"), (14, 2, 3, 1, "R"), (15, 2, 1, 1, "W")]
fx_ears_up = [(5, 0, 2, 1, "K"), (5, 1, 2, 2, "R"), (6, 1, 1, 2, "W"),
              (15, 0, 2, 1, "K"), (15, 1, 2, 2, "R"), (15, 1, 1, 2, "W")]
fx_ears_flat = [(3, 3, 3, 1, "R"), (2, 3, 1, 1, "K"), (16, 3, 3, 1, "R"), (19, 3, 1, 1, "K")]
fx_tail = [(16, 11, 3, 3, "R"), (18, 9, 3, 3, "R"), (19, 7, 2, 2, "W")]
fx_tail_swish = [(16, 11, 3, 3, "R"), (19, 10, 2, 3, "R"), (20, 8, 2, 2, "W")]
fx_eyes = [(7, 4, 2, 2, "Y"), (8, 4, 1, 2, "E"), (13, 4, 2, 2, "Y"), (13, 4, 1, 2, "E")]
fx_eyes_up = [(7, 4, 2, 2, "Y"), (8, 4, 1, 1, "E"), (13, 4, 2, 2, "Y"), (13, 4, 1, 1, "E")]
fx_eyes_big = [(6, 3, 3, 3, "Y"), (7, 3, 2, 3, "E"), (13, 3, 3, 3, "Y"), (13, 3, 2, 3, "E")]
fx_eyes_shut = [(7, 5, 2, 1, "E"), (13, 5, 2, 1, "E")]
fx_eyes_happy = [(7, 5, 1, 1, "E"), (8, 4, 1, 1, "E"), (9, 5, 1, 1, "E"), (12, 5, 1, 1, "E"), (13, 4, 1, 1, "E"), (14, 5, 1, 1, "E")]
fx_eyes_x = [(6, 3, 1, 1, "E"), (8, 3, 1, 1, "E"), (7, 4, 1, 1, "E"), (6, 5, 1, 1, "E"), (8, 5, 1, 1, "E"),
             (13, 3, 1, 1, "E"), (15, 3, 1, 1, "E"), (14, 4, 1, 1, "E"), (13, 5, 1, 1, "E"), (15, 5, 1, 1, "E")]
fx_dig_l = [(7, 14, 2, 2, "."), (7, 13, 2, 1, "K"), (6, 15, 1, 1, "B")]
fx_dig_r = [(13, 14, 2, 2, "."), (13, 13, 2, 1, "K"), (15, 15, 1, 1, "B")]
fox_moods = {
    "idle": {"fps": 1, "frames": [fx_ears + fx_tail + fx_eyes, fx_ears + fx_tail + fx_eyes,
                                  fx_ears + fx_tail + fx_eyes, fx_ears + fx_tail + fx_eyes_shut]},
    "thinking": {"frames": [fx_ears + fx_tail + fx_eyes_up + [(19, 0, 2, 2, "t"), (19, 3, 1, 1, "t")]]},
    "working": {"fps": 3, "frames": [fx_ears + fx_tail + fx_eyes + fx_dig_l, fx_ears + fx_tail_swish + fx_eyes + fx_dig_r]},
    "needs": {"fps": 3, "frames": [fx_ears_up + fx_tail_swish + fx_eyes_big + [(20, 0, 1, 3, "a"), (20, 4, 1, 1, "a")],
                                   fx_ears_up + fx_tail + fx_eyes_big]},
    "done": {"fps": 2, "frames": [
        fx_ears + fx_tail_swish + fx_eyes_happy + [(18, 0, 1, 1, "h"), (20, 0, 1, 1, "h"), (18, 1, 3, 1, "h"), (19, 2, 1, 1, "h")],
        fx_ears + fx_tail + fx_eyes_happy,
    ]},
    "error": {"frames": [fx_ears_flat + fx_tail + fx_eyes_x]},
    "sleeping": {"fps": 1, "frames": [fx_ears + fx_tail + fx_eyes_shut + [(18, 1, 3, 1, "z"), (19, 2, 1, 1, "z"), (18, 3, 3, 1, "z")],
                                      fx_ears + fx_tail + fx_eyes_shut]},
}
fox = pet("Fox", "Red fox: digs while working, ears up when it needs you.", 22, 16,
          {"R": "#E8743B", "K": "#3A2A24", "W": "#FBF8F2", "Y": "#F2B53C", "E": "#141413", "B": "#9C7A5B",
           "t": "#2A5DB0", "a": "#8A5A00", "h": "#E0546B", "z": "#5B4B9A"},
          fox_base, fox_moods)

# ---------- bunny (front view, sitting; whole-sprite frames so it can hop) ----------
bn_body = [
    (6, 5, 10, 1, "B"), (5, 6, 12, 5, "B"),                             # head
    (10, 9, 2, 1, "p"), (10, 10, 2, 1, "W"),                            # nose + buck teeth
    (6, 11, 10, 4, "B"), (8, 11, 6, 4, "W"),                            # body + belly
    (6, 15, 3, 1, "W"), (13, 15, 3, 1, "W"),                            # feet
    (16, 13, 2, 2, "W"),                                                # puff tail
]
bn_ears = [(6, 0, 2, 5, "B"), (7, 1, 1, 3, "p"), (14, 0, 2, 5, "B"), (14, 1, 1, 3, "p")]
bn_ears_flop = [(6, 0, 2, 5, "B"), (7, 1, 1, 3, "p"), (14, 4, 2, 1, "B"), (15, 3, 4, 2, "B"), (16, 3, 2, 1, "p")]
bn_ears_droop = [(2, 6, 3, 2, "B"), (3, 6, 2, 1, "p"), (17, 6, 3, 2, "B"), (17, 6, 2, 1, "p")]
bn_ears_back = [(6, 3, 2, 2, "B"), (14, 3, 2, 2, "B")]
bn_eyes = [(7, 7, 2, 2, "E"), (7, 7, 1, 1, "W"), (13, 7, 2, 2, "E"), (13, 7, 1, 1, "W")]
bn_eyes_up = [(7, 6, 2, 2, "E"), (7, 6, 1, 1, "W"), (13, 6, 2, 2, "E"), (13, 6, 1, 1, "W")]
bn_eyes_big = [(6, 6, 3, 3, "E"), (6, 6, 1, 1, "W"), (13, 6, 3, 3, "E"), (13, 6, 1, 1, "W")]
bn_eyes_shut = [(7, 8, 2, 1, "E"), (13, 8, 2, 1, "E")]
bn_eyes_happy = [(6, 8, 1, 1, "E"), (7, 7, 1, 1, "E"), (8, 8, 1, 1, "E"), (13, 8, 1, 1, "E"), (14, 7, 1, 1, "E"), (15, 8, 1, 1, "E")]
bn_eyes_x = [(6, 6, 1, 1, "E"), (8, 6, 1, 1, "E"), (7, 7, 1, 1, "E"), (6, 8, 1, 1, "E"), (8, 8, 1, 1, "E"),
             (13, 6, 1, 1, "E"), (15, 6, 1, 1, "E"), (14, 7, 1, 1, "E"), (13, 8, 1, 1, "E"), (15, 8, 1, 1, "E")]
bn_bang = [(20, 0, 1, 3, "a"), (20, 4, 1, 1, "a")]
bn_heart = [(18, 0, 1, 1, "h"), (20, 0, 1, 1, "h"), (18, 1, 3, 1, "h"), (19, 2, 1, 1, "h")]
bunny_moods = {
    "idle": {"fps": 1, "frames": [bn_body + bn_ears + bn_eyes, bn_body + bn_ears + bn_eyes,
                                  bn_body + bn_ears + bn_eyes, bn_body + bn_ears + bn_eyes_shut]},
    "thinking": {"frames": [bn_body + bn_ears_flop + bn_eyes_up + [(20, 0, 2, 2, "t"), (21, 3, 1, 1, "t")]]},
    "working": {"fps": 3, "frames": [bn_body + bn_ears + bn_eyes, shift_up(bn_body + bn_ears + bn_eyes)]},
    "needs": {"fps": 4, "frames": [bn_body + bn_ears + bn_eyes_big + bn_bang, shift_up(bn_body + bn_ears + bn_eyes_big)]},
    "done": {"fps": 2, "frames": [shift_up(bn_body + bn_ears + bn_eyes_happy) + bn_heart, bn_body + bn_ears + bn_eyes_happy]},
    "error": {"frames": [bn_body + bn_ears_droop + bn_eyes_x]},
    "sleeping": {"fps": 1, "frames": [bn_body + bn_ears_back + bn_eyes_shut + [(18, 1, 3, 1, "z"), (19, 2, 1, 1, "z"), (18, 3, 3, 1, "z")],
                                      bn_body + bn_ears_back + bn_eyes_shut]},
}
bunny = pet("Bunny", "Grey bunny: hops while working, flops an ear while thinking.", 22, 16,
            {"B": "#B9AFA6", "W": "#FBF8F2", "p": "#F2A7B5", "E": "#141413",
             "t": "#2A5DB0", "a": "#8A5A00", "h": "#E0546B", "z": "#5B4B9A"},
            [], bunny_moods)

for name, data in (("crab", crab), ("robot", robot), ("cat", cat), ("turtle", turtle), ("dog", dog), ("penguin", penguin), ("duck", duck), ("frog", frog), ("owl", owl), ("fox", fox), ("bunny", bunny)):
    with open(f"{out_dir}/{name}.json", "w") as f:
        # Frames one row per line so the pixel art stays readable.
        text = json.dumps(data, indent=2)
        f.write(text + "\n")
    print(name)
    for row in data["moods"]["needs"]["frames"][0]:
        print("  " + row)
