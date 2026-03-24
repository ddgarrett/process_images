'''
    General utility functions for Process Images System

'''
import os
from pathlib import Path

import PIL.Image, PIL.ImageTk

try:
    _LANCZOS = PIL.Image.Resampling.LANCZOS
except AttributeError:
    _LANCZOS = PIL.Image.LANCZOS

_BADGE_PATH = Path(__file__).resolve().parent / "assets" / "dup_target_badge.png"
_badge_source = None


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
):
    ''' Convert a file or byte stream to a Tkinter image.
        If resize value provide, resize the image.
        If dup_target_badge, overlay assets/dup_target_badge.png bottom-right.
        badge_for_gallery True uses a smaller icon than the main image view.
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

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        return PIL.ImageTk.PhotoImage(img), osize
    except Exception as e:
        print(f"image util exception: {e}")
        return "", (0, 0)
