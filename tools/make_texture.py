"""Generate the 16x16 music disc item texture.

The disc silhouette follows the vanilla music disc look (solid body, small
centre hole) and the palette is sampled from the "星拂云锦" album cover so the
item still reads as the same artwork at 16x16.

Run from the repository root:
    <python> tools/make_texture.py <cover-image> <output-png>
"""

import sys

import numpy as np
from PIL import Image

SIZE = 16
CENTRE = 7.5


def disc_alpha() -> np.ndarray:
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    radius = np.sqrt((xx - CENTRE) ** 2 + (yy - CENTRE) ** 2)
    alpha = np.clip((8.0 - radius) / 0.9, 0.0, 1.0)
    alpha[radius <= 7.0] = 1.0          # solid body
    alpha[radius <= 1.2] = 0.35         # transparent spindle hole
    return alpha


def to_oklab(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    l = np.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = np.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = np.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return np.stack(
        [
            0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
        ],
        axis=-1,
    )


def to_rgb(lab: np.ndarray) -> np.ndarray:
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    out = np.stack(
        [
            4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
        ],
        axis=-1,
    )
    return np.clip(out, 0.0, 1.0)


def cover_palette(src: str) -> tuple[np.ndarray, np.ndarray]:
    """Return (label colour, shadow body colour) sampled from the cover art."""
    img = Image.open(src).convert("RGB")
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    img = img.crop((left, top, left + side, top + side))
    pixels = np.asarray(img.resize((48, 48), Image.LANCZOS)).astype(np.float64) / 255.0
    pixels = pixels.reshape(-1, 3)

    lab = to_oklab(pixels)
    # Prefer saturated, mid-to-light pixels: those are the flowers and gold.
    chroma = np.sqrt(lab[:, 1] ** 2 + lab[:, 2] ** 2)
    score = chroma * 2.0 - np.abs(lab[:, 0] - 0.62)

    # Two well-separated picks give the label a warm/cool split like the art.
    first = int(np.argmax(score))
    far = np.sqrt(((lab - lab[first]) ** 2).sum(axis=1))
    second = int(np.argmax(score * np.clip(far, 0.0, None)))

    picks = pixels[[first, second]]
    lab_picks = to_oklab(picks)
    lab_picks[:, 0] = np.minimum(0.76, lab_picks[:, 0] + 0.16)
    labels = to_rgb(lab_picks)

    dark = pixels[pixels.max(axis=1) < 0.35]
    body = dark.mean(axis=0) if len(dark) > 20 else np.array([0.06, 0.05, 0.07])
    body = np.clip(body * 0.85, 0.02, 0.5)
    return labels, body


def build(src: str | None) -> Image.Image:
    col = np.arange(SIZE, dtype=np.float64)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    radius = np.sqrt((xx - CENTRE) ** 2 + (yy - CENTRE) ** 2)

    label_colours = np.array([[0.85, 0.42, 0.45], [0.35, 0.72, 0.66]])
    body_colour = np.array([0.07, 0.06, 0.09])
    if src:
        label_colours, body_colour = cover_palette(src)

    rgb = np.zeros((SIZE, SIZE, 3))
    # Base vinyl body, very slightly lighter towards the middle.
    body_shade = 1.0 + 0.45 * np.clip(1.0 - radius / 8.0, 0.0, 1.0)
    rgb[:] = body_colour * body_shade[..., None]

    # Fine groove rings, alternating as they radiate outwards.
    ring = np.clip(1.0 + 0.16 * np.cos(radius * 2.0 * np.pi / 1.5), 0.7, 1.35)
    rgb *= ring[..., None]

    # Coloured centre label, warm on one side and cool on the other.
    blend = np.clip((xx - yy + 6.0) / 12.0, 0.0, 1.0)[..., None]
    label = label_colours[0] * (1.0 - blend) + label_colours[1] * blend
    rgb = np.where((radius <= 4.3)[..., None], label, rgb)

    # Thin metallic ring around the label, echoing the album's gold linework.
    gold = np.array([0.83, 0.70, 0.36])
    gold_band = (radius > 4.3) & (radius <= 4.9)
    rgb = np.where(gold_band[..., None], gold, rgb)

    # Highlight on the upper-left rim, shadow on the lower-right rim.
    light = np.clip((xx + yy - 8.0) / 14.0, -1.0, 1.0)
    rim = np.clip((radius - 5.0) / 3.0, 0.0, 1.0)
    rgb *= (1.0 - 0.30 * light * rim)[..., None]

    rgba = np.dstack([np.clip(rgb, 0.0, 1.0), disc_alpha()])
    return Image.fromarray((rgba * 255.0 + 0.5).astype(np.uint8), mode="RGBA")


if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) >= 3 else None
    destination = sys.argv[2] if len(sys.argv) >= 3 else sys.argv[1]
    build(source).save(destination)
    print(f"wrote {destination}")
