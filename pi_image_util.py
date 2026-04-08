'''
    General utility functions for Process Images System

'''
import os
from pathlib import Path

import PIL.Image, PIL.ImageTk
from PIL import ImageDraw, ImageFont

try:
    _LANCZOS = PIL.Image.Resampling.LANCZOS
except AttributeError:
    _LANCZOS = PIL.Image.LANCZOS

_BADGE_PATH = Path(__file__).resolve().parent / "assets" / "dup_target_badge.png"
_badge_source = None


def _load_overlay_font(size: int):
    """Load a readable TrueType font with cross-platform fallbacks."""
    candidates = [
        "DejaVuSans.ttf",
        "Arial.ttf",
        "Helvetica.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _get_badge_source():
    '''Load dup target badge PNG once; return RGBA Image or None.'''
    global _badge_source
    if _badge_source is not None:
        return _badge_source
    if not _BADGE_PATH.is_file():
        return None
    try:
        src = PIL.Image.open(_BADGE_PATH)
        _badge_source = src.convert("RGBA")
        return _badge_source
    except OSError:
        return None


def _paste_dup_target_badge(img: PIL.Image.Image, gallery_thumb: bool) -> PIL.Image.Image:
    '''Composite small corner badge on bottom-right. img may be any mode.'''
    src = _get_badge_source()
    if src is None:
        return img
    w, h = img.size
    if w < 8 or h < 8:
        return img
    if gallery_thumb:
        side = max(10, min(26, int(min(w, h) * 0.20)))
    else:
        side = max(28, min(64, int(min(w, h) * 0.12)))
    badge = src.resize((side, side), _LANCZOS)
    bw, bh = badge.size
    margin = max(2, side // 6)
    x = max(0, w - bw - margin)
    y = max(0, h - bh - margin)
    base = img.convert("RGBA")
    base.paste(badge, (x, y), badge)
    return base


def _draw_overlay_corner_text(
    img: PIL.Image.Image,
    text: str,
    gallery_thumb: bool,
    align: str,
) -> PIL.Image.Image:
    """Draw text along the bottom edge; align 'left' or 'right' (same style either way)."""
    if not text:
        return img
    w, h = img.size
    if w < 24 or h < 24:
        return img

    base = img.convert("RGBA")
    draw = ImageDraw.Draw(base, "RGBA")
    font_size = 13 if gallery_thumb else 18
    font = _load_overlay_font(font_size)

    max_chars = 24 if gallery_thumb else 44
    overlay_text = text
    if len(overlay_text) > max_chars:
        overlay_text = overlay_text[: max_chars - 3] + "..."

    left, top, right, bottom = draw.textbbox((0, 0), overlay_text, font=font)
    tw = right - left
    th = bottom - top

    pad_x = 4 if gallery_thumb else 8
    pad_y = 3 if gallery_thumb else 5
    margin = 2 if gallery_thumb else 6
    if align == "right":
        x = max(margin, w - tw - 2 * pad_x - margin)
    else:
        x = margin
    y = max(margin, h - th - 2 * pad_y - margin)

    draw.rectangle(
        (x, y, x + tw + 2 * pad_x, y + th + 2 * pad_y),
        fill=(0, 0, 0, 165),
    )
    draw.text((x + pad_x, y + pad_y), overlay_text, font=font, fill=(255, 255, 255, 255))
    return base


def is_image_file(fn) -> bool:
    ''' Return true if the file for fn is an image file '''
    if fn:
        return (os.path.isfile(fn) and 
                fn.lower().endswith((".png", ".gif",".jpg","jpeg")))
    return False

def cnv_image(
    file,
    resize=None,
    rotate=1,
    dup_target_badge=False,
    badge_for_gallery=False,
    overlay_text=None,
    overlay_text_right=None,
):
    ''' Convert a file or byte stream to a Tkinter image.
        If resize value provide, resize the image.
        If dup_target_badge, overlay assets/dup_target_badge.png bottom-right.
        badge_for_gallery True uses a smaller icon than the main image view.
        overlay_text_right draws a label bottom-right (after the badge if any).
        Return both the Tkinter image and the original image size.
    '''
    try:
        img = PIL.Image.open(file)

        if rotate > 1:
            if rotate == 3:
                img = img.rotate(180, expand=True)
            elif rotate == 6:
                img = img.rotate(270, expand=True)
            elif rotate == 8:
                img = img.rotate(90, expand=True)

        osize = img.size
        if resize:
            img.thumbnail(resize)

        if dup_target_badge:
            img = _paste_dup_target_badge(img, badge_for_gallery)
        if overlay_text:
            img = _draw_overlay_corner_text(
                img, overlay_text, badge_for_gallery, "left"
            )
        if overlay_text_right:
            img = _draw_overlay_corner_text(
                img, overlay_text_right, badge_for_gallery, "right"
            )

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        return PIL.ImageTk.PhotoImage(img), osize
    except Exception as e:
        print(f"image util exception: {e}")
        return "", (0, 0)
