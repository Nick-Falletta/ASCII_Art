import argparse
import os
import sys
from typing import List, Tuple
from PIL import Image

# Character Set
# These presets map brightness to characters
# Darker pixels -> Darker characters
CHARSETS = {
    "standard": "@%#*+=-:. ",
    "classic": "$@B%8&WM#*oahkbdpqwmZ0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!l;:,\"^`'. ",
    "blocks": "█▓▒░  ",
    "dots": "⣿⣾⣶⣤⣀  ",
}


# CLI parsing
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render images as ASCII art.")
    parser.add_argument("input", help="Path to image file")
    parser.add_argument("--width", type=int, default=100,
                        help="Output character width (default: 100)")
    parser.add_argument("--charset", type=str, default="standard",
                        help="Charset preset name or a custom string (default: standard). "
                             f"Presets: {', '.join(CHARSETS.keys())}")
    parser.add_argument("--invert", action="store_true",
                        help="Invert brightness → characters mapping (light becomes dark)")
    parser.add_argument("--color", action="store_true",
                        help="ANSI truecolor output (terminal/HTML) using original pixel colors")
    parser.add_argument("--no-dither", action="store_true",
                        help="Disable Floyd–Steinberg dithering (use nearest character only)")
    parser.add_argument("--gamma", type=float, default=1.0,
                        help="Gamma correction (default: 1.0). >1 brightens midtones, <1 darkens.")
    parser.add_argument("--out", type=str, default=None,
                        help="Save output to .txt or .html (guessed by extension). If omitted, prints.")
    parser.add_argument("--height-scale", type=float, default=0.55,
                        help="Character height scaling (default: 0.55). "
                             "Compensates for the fact that terminal chars are taller than wide.")
    return parser.parse_args()


def resolve_charset(charset_arg: str) -> str:
    if charset_arg in CHARSETS:
        return CHARSETS[charset_arg]
    if len(charset_arg.strip()) == 0:
        raise ValueError("Custom charset must not be empty.")
    return charset_arg


# Image Creation
def luminance(rgb: Tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def apply_gamma(y: float, gamma: float) -> float:
    if gamma <= 0:
        gamma = 1.0
    return 255.0 * ((y / 255.0) ** (1.0 / gamma))


def resize_image(img: Image.Image, width: int, height_scale: float) -> Image.Image:
    w, h = img.size
    new_w = max(1, width)
    aspect = h / w if w else 1.0       # image aspect ratio
    new_h = max(1, int(aspect * new_w * height_scale))
    return img.resize((new_w, new_h), Image.BICUBIC)


# Character Mapping
def build_levels(n: int) -> List[float]:
    if n <= 1:
        return [128.0]
    step = 255.0 / (n - 1)
    return [i * step for i in range(n)]


def nearest_level(y: float, levels: List[float]) -> Tuple[int, float]:
    n = len(levels)
    idx = int(round((y / 255.0) * (n - 1)))
    idx = max(0, min(n - 1, idx))
    return idx, levels[idx]


# Floyd–Steinberg Dithering
def fs_dither(grays: List[List[float]], levels: List[float]) -> List[List[int]]:
    h = len(grays)
    w = len(grays[0]) if h > 0 else 0
    idx_grid: List[List[int]] = [[0] * w for _ in range(h)]

    # Dithering Loop
    for y in range(h):
        for x in range(w):
            old = grays[y][x]
            idx, new = nearest_level(old, levels)
            idx_grid[y][x] = idx
            err = old - new

            # Distribute error to neighbors
            if x + 1 < w:
                grays[y][x + 1] += err * (7 / 16)
            if y + 1 < h:
                if x - 1 >= 0:
                    grays[y + 1][x - 1] += err * (3 / 16)
                grays[y + 1][x] += err * (5 / 16)
                if x + 1 < w:
                    grays[y + 1][x + 1] += err * (1 / 16)
    return idx_grid


# Grayscale Grid
def build_grayscale_grid(img_rgb: Image.Image, gamma: float) -> List[List[float]]:
    w, h = img_rgb.size
    px = img_rgb.load()
    grid: List[List[float]] = [[0.0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            y_lin = luminance(px[x, y])       # brightness
            grid[y][x] = apply_gamma(y_lin, gamma)
    return grid


# Indices to ASCII
def indices_to_ascii(idx_grid: List[List[int]], charset: str, invert: bool) -> List[str]:
    if invert:
        charset = charset[::-1]
    lines: List[str] = []
    h = len(idx_grid)
    w = len(idx_grid[0]) if h > 0 else 0
    for y in range(h):
        row_chars = [charset[idx_grid[y][x]] for x in range(w)]
        lines.append("".join(row_chars))
    return lines


# Colorization
def colorize_ansi(lines: List[str], img_rgb: Image.Image) -> List[str]:
    w, h = img_rgb.size
    px = img_rgb.load()
    colored: List[str] = []
    ESC = "\x1b"
    RESET = f"{ESC}[0m"
    for y, line in enumerate(lines):
        out_chars = []
        for x, ch in enumerate(line):
            r, g, b = px[x, y]
            out_chars.append(f"\x1b[38;2;{r};{g};{b}m{ch}")
        colored.append("".join(out_chars) + RESET)
    return colored


# Exporters (HTML / TXT)
def export_html(lines: List[str], img_rgb: Image.Image = None, use_color: bool = False, out_path: str = "output.html"):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        
        # Minimal HTML with dark background for contrast
        f.write("<!doctype html><meta charset='utf-8'>\n")
        f.write("<title>ASCII Art</title>\n")
        f.write("<style>body{margin:0;background:#000}"
                "pre{line-height:0.9;font:10px/10px monospace;color:#fff;padding:8px;}</style>\n")
        f.write("<pre>\n")
        if use_color and img_rgb is not None:
            w, h = img_rgb.size
            px = img_rgb.load()
            for y, line in enumerate(lines):
                for x, ch in enumerate(line):
                    r, g, b = px[x, y]
                    f.write(f"<span style='color:rgb({r},{g},{b})'>{ch}</span>")
                f.write("\n")
        else:
            for line in lines:
                f.write(line + "\n")
        f.write("</pre>\n")
    print(f"Saved HTML → {out_path}")


def export_txt(lines: List[str], out_path: str = "output.txt"):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Saved text → {out_path}")


# Main
def main():
    args = parse_args()

    # Validate input path
    if not os.path.isfile(args.input):
        print(f"Input not found: {args.input}")
        sys.exit(1)

    # Resolve charset
    try:
        charset = resolve_charset(args.charset)
    except ValueError as e:
        print(f"Invalid charset: {e}")
        sys.exit(1)

    # Load image
    src = Image.open(args.input).convert("RGB")

    # Resize image
    resized_rgb = resize_image(src, width=args.width, height_scale=args.height_scale)

    # Build grayscale grid
    grays = build_grayscale_grid(resized_rgb, gamma=args.gamma)

    levels = build_levels(len(charset))
    if args.no_dither:
        h = len(grays)
        w = len(grays[0]) if h > 0 else 0
        idx_grid = [[0] * w for _ in range(h)]
        for y in range(h):
            for x in range(w):
                idx, _ = nearest_level(grays[y][x], levels)
                idx_grid[y][x] = idx
    else:
        idx_grid = fs_dither(grays, levels)

    # Convert indices to ASCII characters
    lines = indices_to_ascii(idx_grid, charset, invert=args.invert)

    # Output
    if args.out:
        if args.out.lower().endswith(".html"):
            export_html(lines, img_rgb=resized_rgb, use_color=args.color, out_path=args.out)
        else:
            save_lines = colorize_ansi(lines, resized_rgb) if args.color else lines
            export_txt(save_lines, out_path=args.out)
    else:
        # Print to terminal
        if args.color:
            lines = colorize_ansi(lines, resized_rgb)
        print("\n".join(lines))


# Run Main
if __name__ == "__main__":
    main()
