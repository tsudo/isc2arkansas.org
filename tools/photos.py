"""Build site images from source photos and brand files.

Reads tools/photos.json, writes resized, metadata-free WebP files into
site/img/, and rewrites the photo grid in site/index.html between the
<!-- photos:start --> and <!-- photos:end --> markers.

With --review, also builds site/photo-review/ showing every source photo
numbered, for choosing picks. That folder must not ship to production.

Run from the repo root:  py -3.14 tools/photos.py [--review]
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
CONFIG = ROOT / "tools" / "photos.json"
SIZES = (600, 1200)
QUALITY = 78


def fail(msg: str) -> None:
    print(f"photos.py: {msg}", file=sys.stderr)
    sys.exit(1)


def load_image(path: Path) -> Image.Image:
    try:
        im = Image.open(path)
        im = ImageOps.exif_transpose(im)
        return im.convert("RGB")
    except (OSError, ValueError) as exc:
        fail(f"cannot read {path}: {exc}")
        raise  # unreachable; keeps type checkers quiet


def save_webp(im: Image.Image, long_edge: int, dest: Path) -> tuple[int, int]:
    copy = im.copy()
    copy.thumbnail((long_edge, long_edge), Image.Resampling.LANCZOS)
    # Pillow writes no EXIF/XMP unless passed explicitly, so output is metadata-free.
    copy.save(dest, "WEBP", quality=QUALITY, method=6)
    return copy.size


def source_files(src_dir: Path) -> list[Path]:
    files = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not files:
        fail(f"no source photos in {src_dir}")
    return files


def build_picks(cfg: dict, files: list[Path]) -> str:
    out_dir = SITE / "img" / "photos"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.webp"):
        old.unlink()
    figures = []
    for pick in cfg["picks"]:
        n = pick["n"]
        if not 1 <= n <= len(files):
            fail(f"pick {n} is outside 1..{len(files)}")
        im = load_image(files[n - 1])
        dims = {}
        for size in SIZES:
            dims[size] = save_webp(im, size, out_dir / f"{n:02d}-{size}.webp")
        w, h = dims[600]
        alt = html.escape(pick["alt"], quote=True)
        cap = html.escape(pick["caption"])
        figures.append(
            "        <figure>\n"
            f'          <img src="/img/photos/{n:02d}-600.webp" '
            f'srcset="/img/photos/{n:02d}-600.webp {dims[600][0]}w, /img/photos/{n:02d}-1200.webp {dims[1200][0]}w" '
            f'sizes="(min-width: 900px) 30vw, (min-width: 600px) 45vw, 92vw" '
            f'width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">\n'
            f"          <figcaption>{cap}</figcaption>\n"
            "        </figure>"
        )
    return "\n".join(figures)


def inject(markup: str) -> None:
    index = SITE / "index.html"
    text = index.read_text(encoding="utf-8")
    start, end = "<!-- photos:start -->", "<!-- photos:end -->"
    if start not in text or end not in text:
        fail(f"markers missing in {index}")
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    index.write_text(f"{head}{start}\n{markup}\n        {end}{tail}", encoding="utf-8", newline="\n")


def build_brand() -> None:
    brand = ROOT.parent / "inputs" / "wp-media" / "brand"
    img = SITE / "img"
    logo = load_image(brand / "isc2ar_logo.png")
    for size in (96, 192):
        save_webp(logo, size, img / f"logo-{size}.webp")
    icon = load_image(brand / "cropped-isc2ar_logo.png")
    for size, name in ((32, "favicon-32.png"), (180, "apple-touch-icon.png")):
        c = ImageOps.pad(icon, (size, size), color="white")
        c.save(SITE / name, "PNG", optimize=True)


def build_review(files: list[Path]) -> None:
    out = SITE / "photo-review"
    out.mkdir(exist_ok=True)
    cells = []
    for n, f in enumerate(files, 1):
        save_webp(load_image(f), 600, out / f"{n:02d}.webp")
        cells.append(f'<figure><img src="{n:02d}.webp" alt="" loading="lazy"><figcaption>{n:02d}</figcaption></figure>')
    (out / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex">'
        '<title>Photo review</title><link rel="stylesheet" href="/css/site.css"></head>'
        '<body><main class="container stack"><h1>Photo review (not for production)</h1>'
        "<p>Every source photo, numbered. Picks live in <code>tools/photos.json</code>.</p>"
        f'<div class="photo-grid">{"".join(cells)}</div></main></body></html>\n',
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    files = source_files((CONFIG.parent / cfg["source_dir"]).resolve())
    inject(build_picks(cfg, files))
    build_brand()
    if "--review" in sys.argv:
        build_review(files)
    print(f"photos.py: {len(cfg['picks'])} picks from {len(files)} sources")


if __name__ == "__main__":
    main()
