#!/usr/bin/env python3
"""Deterministically compose an artifact photo into a notebook-style PNG.

The source file is opened read-only and never overwritten. The default `contain`
mode keeps the complete photograph visible. This helper intentionally performs
no artifact recognition and invents no archaeological details.
"""

from __future__ import annotations

import argparse
import hashlib
import random
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install it with: python -m pip install -r scripts/requirements.txt"
    ) from exc


PAPER = (232, 216, 184)
INK = (67, 57, 45)
MATTE = (30, 28, 25)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_font(explicit: Path | None) -> Path:
    candidates = [
        explicit,
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise SystemExit("No CJK font found. Pass one with --font /path/to/font.ttf")


def fit_photo(image: Image.Image, size: tuple[int, int], mode: str) -> Image.Image:
    if mode == "cover":
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    return ImageOps.contain(image, size, method=Image.Resampling.LANCZOS)


def edge_sketch(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    base = ImageOps.contain(image.convert("RGB"), size, Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(base).filter(ImageFilter.GaussianBlur(0.7))
    edges = ImageOps.autocontrast(gray.filter(ImageFilter.FIND_EDGES))
    alpha = edges.point(lambda value: 0 if value < 28 else min(185, value))
    layer = Image.new("RGBA", base.size, (72, 62, 49, 0))
    layer.putalpha(alpha)
    return layer


def add_paper_texture(canvas: Image.Image, seed: int) -> None:
    rng = random.Random(seed)
    draw = ImageDraw.Draw(canvas, "RGBA")
    width, height = canvas.size
    for _ in range((width * height) // 900):
        x = rng.randrange(width)
        y = rng.randrange(height)
        radius = rng.choice((1, 1, 2, 3))
        color = rng.choice(((92, 68, 39, 10), (255, 250, 224, 14), (123, 84, 45, 8)))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def jagged_edge(width: int, height: int, y: int, seed: int) -> list[tuple[int, int]]:
    rng = random.Random(seed)
    points = [(0, y)]
    for x in range(0, width + 25, 25):
        points.append((min(x, width), y + rng.randint(-12, 12)))
    points.extend(((width, height), (0, height)))
    return points


def wrap_text(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int
) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        box = draw.textbbox((0, 0), candidate, font=font)
        if current and box[2] - box[0] > width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def compose(args: argparse.Namespace) -> None:
    source = args.input.resolve()
    output = args.output.resolve()
    if source == output:
        raise SystemExit("Output must not overwrite the source photograph.")
    before = sha256(source)

    with Image.open(source) as opened:
        photo = ImageOps.exif_transpose(opened).convert("RGB")

    orientation = args.orientation
    if orientation == "auto":
        orientation = "landscape" if photo.width / photo.height >= 1.2 else "portrait"
    canvas_size = (1600, 1200) if orientation == "landscape" else (1200, 1600)
    width, height = canvas_size
    canvas = Image.new("RGB", canvas_size, PAPER)
    add_paper_texture(canvas, args.seed)
    draw = ImageDraw.Draw(canvas, "RGBA")

    margin = 52
    photo_bottom = int(height * (0.54 if orientation == "portrait" else 0.53))
    box = (margin, 44, width - margin, photo_bottom)
    draw.rounded_rectangle(box, radius=10, fill=MATTE)
    target_size = (box[2] - box[0], box[3] - box[1])
    fitted = fit_photo(photo, target_size, args.photo_mode)
    px = box[0] + (target_size[0] - fitted.width) // 2
    py = box[1] + (target_size[1] - fitted.height) // 2
    canvas.paste(fitted, (px, py))

    note_top = photo_bottom - 8
    draw.polygon(jagged_edge(width, height, note_top, args.seed + 1), fill=(*PAPER, 255))

    font_path = find_font(args.font)
    title_font = ImageFont.truetype(str(font_path), 62 if orientation == "portrait" else 58)
    fact_font = ImageFont.truetype(str(font_path), 31 if orientation == "portrait" else 29)
    label_font = ImageFont.truetype(str(font_path), 23)

    text_x = 72
    text_width = int(width * (0.36 if orientation == "portrait" else 0.31))
    text_y = note_top + 70
    for line in wrap_text(draw, args.title, title_font, text_width):
        draw.text((text_x, text_y), line, font=title_font, fill=(*INK, 255))
        text_y += title_font.size + 9
    draw.line(
        (text_x, text_y + 4, text_x + text_width - 16, text_y + 4),
        fill=(*INK, 150),
        width=2,
    )
    text_y += 34
    for fact in args.fact:
        for line in wrap_text(draw, fact, fact_font, text_width):
            draw.text((text_x, text_y), line, font=fact_font, fill=(*INK, 238))
            text_y += fact_font.size + 11
        text_y += 4

    sketch_left = text_x + text_width + 42
    sketch_top = note_top + 64
    sketch_size = (width - sketch_left - 74, height - sketch_top - 78)
    if args.sketch:
        with Image.open(args.sketch) as supplied:
            sketch = ImageOps.contain(
                supplied.convert("RGBA"), sketch_size, Image.Resampling.LANCZOS
            )
    else:
        sketch = edge_sketch(photo, sketch_size)
    sx = sketch_left + (sketch_size[0] - sketch.width) // 2
    sy = sketch_top + (sketch_size[1] - sketch.height) // 2
    canvas.paste(sketch, (sx, sy), sketch)

    draw.rectangle(
        (sketch_left, sketch_top, width - 74, height - 78),
        outline=(*INK, 72),
        width=2,
    )
    tick = 15
    corners = (
        (sketch_left, sketch_top),
        (width - 74, sketch_top),
        (sketch_left, height - 78),
        (width - 74, height - 78),
    )
    for x, y in corners:
        draw.line((x - tick, y, x + tick, y), fill=(*INK, 90), width=2)
        draw.line((x, y - tick, x, y + tick), fill=(*INK, 90), width=2)
    draw.text(
        (sketch_left, height - 63),
        "依据原照片机械提取的观察线稿",
        font=label_font,
        fill=(*INK, 180),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="PNG", optimize=True)
    after = sha256(source)
    if before != after:
        raise RuntimeError("Source photograph changed unexpectedly.")
    print(f"saved={output}")
    print(f"canvas={width}x{height}")
    print("source_unchanged=true")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Source artifact photograph")
    parser.add_argument("--output", type=Path, required=True, help="Destination PNG")
    parser.add_argument("--title", required=True, help="Verified artifact name or category")
    parser.add_argument("--fact", action="append", default=[], help="Verified fact; repeat as needed")
    parser.add_argument(
        "--orientation", choices=("auto", "portrait", "landscape"), default="auto"
    )
    parser.add_argument("--photo-mode", choices=("contain", "cover"), default="contain")
    parser.add_argument("--sketch", type=Path, help="Optional verified line-art image")
    parser.add_argument("--font", type=Path, help="Optional CJK font file")
    parser.add_argument("--seed", type=int, default=54, help="Paper texture seed")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        compose(parse_args())
    except (FileNotFoundError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
