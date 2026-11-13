"""Renders every built-in pet as an SVG strip (one frame per mood) for the README.

Usage: python3 tools/preview_pets.py
Writes docs/pets/<name>.svg and prints a Markdown gallery.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PETS = ROOT / "extension" / "claude-pet@tmurphy-credibly.github.io" / "pets"
OUT = ROOT / "docs" / "pets"
MOODS = [  # (mood, label, status color) — keep in sync with config.js DEFAULTS
    ("idle", "Idle", "#B9B7AE"), ("thinking", "Thinking", "#6FA3FF"), ("working", "Working", "#FF9A6B"),
    ("needs", "Needs you", "#FFC233"), ("done", "Done", "#6BCB7A"), ("error", "Oops", "#FF6B5E"),
    ("sleeping", "Sleeping", "#9C8FE0"),
]
PX = 4          # screen px per pet pixel
CELL_W = 22 * PX + 24
LABEL_H = 18


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    gallery = []
    for path in sorted(PETS.glob("*.json")):
        pet = json.loads(path.read_text())
        palette = pet.get("palette", {})
        rows = max(len(f) for m in pet["moods"].values() for f in m["frames"])
        cols = max(len(r) for m in pet["moods"].values() for f in m["frames"] for r in f)
        cell_h = (rows + 2) * PX + LABEL_H + 8
        width = CELL_W * len(MOODS)
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{cell_h}" '
                 f'viewBox="0 0 {width} {cell_h}" shape-rendering="crispEdges" '
                 f'font-family="system-ui, sans-serif" font-size="11">']
        for i, (mood, label, color) in enumerate(MOODS):
            frames = pet["moods"].get(mood, pet["moods"]["idle"])["frames"]
            ox = i * CELL_W + (CELL_W - cols * PX) // 2
            for y, row in enumerate(frames[0]):
                for x, ch in enumerate(row):
                    if ch in ". ":
                        continue
                    fill = color if ch == "*" else palette[ch]
                    parts.append(f'<rect x="{ox + x * PX}" y="{y * PX}" width="{PX}" height="{PX}" fill="{fill}"/>')
            parts.append(f'<rect x="{ox + PX}" y="{(rows + 1) * PX}" width="{(cols - 2) * PX}" height="{PX}" fill="{color}"/>')
            parts.append(f'<text x="{i * CELL_W + CELL_W // 2}" y="{cell_h - 6}" text-anchor="middle" fill="#8a8a85">{label}</text>')
        parts.append("</svg>")
        (OUT / f"{path.stem}.svg").write_text("\n".join(parts) + "\n")
        gallery.append(f"**{pet['name']}** (`{path.stem}`): {pet.get('description', '')}\n\n"
                       f"![{pet['name']}](docs/pets/{path.stem}.svg)\n")
    print("\n".join(gallery))


if __name__ == "__main__":
    main()
