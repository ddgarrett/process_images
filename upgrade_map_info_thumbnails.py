#!/usr/bin/env python3
"""
Upgrade saved gmplot HTML maps: prepend clickable blog thumbnails to InfoWindow
content that currently has only the text link (same HTML shape as pi_action_map).

This script does not import pi_action_map, pi_config, or other project modules.
Duplicate constants must stay in sync with pi_config.BLOG_URI and
pi_action_map.MAP_INFO_THUMB_MAX_PX if you change them there.

Tested against gmplot output that uses:
  new google.maps.InfoWindow({ content: '...' });
with single-quoted content and backslash-escaped quotes / newlines.

Usage:
  python3 upgrade_map_info_thumbnails.py /path/to/dir
  python3 upgrade_map_info_thumbnails.py /path/to/map.html
  python3 upgrade_map_info_thumbnails.py /path/to/dir --dry-run
  python3 upgrade_map_info_thumbnails.py /path/to/dir --no-recurse
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

# Keep in sync with pi_config.BLOG_URI (no trailing slash).
BLOG_PREFIX = "https://www.garrettblog.com"

# Keep in sync with pi_action_map.MAP_INFO_THUMB_MAX_PX.
MAP_INFO_THUMB_MAX_PX = 120

_IMG_SRC_RE = re.compile(
    r'<img\b[^>]*\bsrc\s*=\s*([\'"])(?P<src>.*?)\1',
    re.IGNORECASE | re.DOTALL,
)

INFO_CONTENT_RE = re.compile(
    r"content:\s*'((?:\\.|[^'\\])*)'",
    re.DOTALL,
)

OLD_SEGMENT_RE = re.compile(
    r'^<a href="([^"]+)"\s+target="_blank">(.*?)</a>$',
    re.IGNORECASE | re.DOTALL,
)


def js_unescape_single_quoted(s: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            n = s[i + 1]
            if n == "'":
                out.append("'")
                i += 2
                continue
            if n == 'n':
                out.append('\n')
                i += 2
                continue
            if n == 'r':
                out.append('\r')
                i += 2
                continue
            if n == '\\':
                out.append('\\')
                i += 2
                continue
            out.append(s[i])
            i += 1
            continue
        out.append(s[i])
        i += 1
    return ''.join(out)


def js_escape_single_quoted(s: str) -> str:
    return (
        s.replace('\\', '\\\\')
        .replace("'", "\\'")
        .replace('\n', '\\n')
        .replace('\r', '\\r')
    )


def fetch_page_ascii(url: str) -> str:
    try:
        with urlopen(url) as f:
            return f.read().decode('ASCII', 'ignore')
    except URLError:
        return ''


def fetch_page_ascii_cached(uri: str, page_cache: dict[str, str], log: bool) -> str:
    if uri in page_cache:
        return page_cache[uri]
    if log:
        print(f'    fetching: {uri}')
    t0 = time.perf_counter()
    body = fetch_page_ascii(uri)
    elapsed = time.perf_counter() - t0
    page_cache[uri] = body
    if log:
        print(f'    fetch done in {elapsed:.2f}s ({len(body)} bytes)')
    return body


def find_anchor_slice(page_html: str, anchor: str) -> str | None:
    tag = f'id="{anchor}"'
    idx = page_html.find(tag)
    if idx < 0:
        return None
    return page_html[idx:]


def get_figure_image_src(anchor_html: str) -> str | None:
    if not anchor_html:
        return None
    low = anchor_html.lower()
    fc = low.find('<figcaption>')
    head = anchor_html[:fc] if fc >= 0 else anchor_html
    m = _IMG_SRC_RE.search(head)
    if not m:
        return None
    src = m.group('src').strip()
    return src or None


def upgrade_info_window_html(
    inner: str,
    page_cache: dict[str, str],
    log: bool,
) -> tuple[str, bool]:
    parts = re.split(r'(<BR>)', inner, flags=re.IGNORECASE)
    changed = False
    out: list[str] = []

    for i in range(0, len(parts), 2):
        seg = parts[i]
        br = parts[i + 1] if i + 1 < len(parts) else ''
        stripped = seg.strip()
        if '<img' in stripped.lower():
            out.append(seg)
            if br:
                out.append(br)
            continue
        if BLOG_PREFIX not in stripped:
            out.append(seg)
            if br:
                out.append(br)
            continue
        m = OLD_SEGMENT_RE.match(stripped)
        if not m:
            out.append(seg)
            if br:
                out.append(br)
            continue
        raw_href = html.unescape(m.group(1))
        link_inner = m.group(2)
        if '#' not in raw_href:
            out.append(seg)
            if br:
                out.append(br)
            continue
        uri, _, anchor = raw_href.partition('#')
        if not uri or not anchor:
            out.append(seg)
            if br:
                out.append(br)
            continue
        page = fetch_page_ascii_cached(uri, page_cache, log)
        anchor_slice = find_anchor_slice(page, anchor)
        img_src = get_figure_image_src(anchor_slice or '')
        blog_url = f'{uri}#{anchor}'
        safe_href = html.escape(blog_url, quote=True)
        href = f'<a href="{safe_href}" target="_blank">{link_inner}</a>'
        if img_src:
            safe_src = html.escape(img_src, quote=True)
            img_tag = (
                f'<img src="{safe_src}" alt="" '
                f'style="max-width:{MAP_INFO_THUMB_MAX_PX}px;height:auto;'
                'display:block;margin:0 auto 8px;">'
            )
            thumb = f'<a href="{safe_href}" target="_blank">{img_tag}</a>'
            new_seg = f'{thumb}{href}'
        else:
            new_seg = href
        if new_seg != stripped:
            changed = True
            if log:
                a_disp = anchor[:56] + ('...' if len(anchor) > 56 else '')
                found = 'yes' if img_src else 'no (link text only)'
                print(f'    segment: id="{a_disp}" thumbnail: {found}')
            prefix = seg[: len(seg) - len(seg.lstrip())]
            suffix = seg[len(seg.rstrip()) :]
            out.append(prefix + new_seg + suffix)
        else:
            out.append(seg)
        if br:
            out.append(br)

    return ''.join(out), changed


def replace_info_windows_in_text(
    text: str,
    *,
    page_cache: dict[str, str],
    log: bool,
) -> tuple[str, int]:
    matches = list(INFO_CONTENT_RE.finditer(text))
    total = len(matches)
    candidates = 0
    for m in matches:
        inner = js_unescape_single_quoted(m.group(1))
        if BLOG_PREFIX in inner and '<img' not in inner.lower():
            candidates += 1
    if log and total:
        print(f'  InfoWindow strings in file: {total} ({candidates} may need work)')

    replacements = 0
    chunks: list[str] = []
    last = 0
    for idx, m in enumerate(matches, start=1):
        chunks.append(text[last : m.start()])
        encoded = m.group(1)
        inner = js_unescape_single_quoted(encoded)
        if BLOG_PREFIX not in inner or '<img' in inner.lower():
            if log and BLOG_PREFIX in inner:
                print(f'  InfoWindow {idx}/{total}: skip (already has <img>)')
            chunks.append(m.group(0))
            last = m.end()
            continue
        if log:
            print(f'  InfoWindow {idx}/{total}: start')
        t0 = time.perf_counter()
        new_inner, ch = upgrade_info_window_html(inner, page_cache, log)
        elapsed = time.perf_counter() - t0
        if ch:
            chunks.append("content: '" + js_escape_single_quoted(new_inner) + "'")
            replacements += 1
            if log:
                print(f'  InfoWindow {idx}/{total}: done in {elapsed:.2f}s (updated)')
        else:
            chunks.append(m.group(0))
            if log:
                print(f'  InfoWindow {idx}/{total}: done in {elapsed:.2f}s (no change)')
        last = m.end()
    chunks.append(text[last:])
    return ''.join(chunks), replacements


def iter_html_files(root: Path, recurse: bool):
    if recurse:
        yield from root.rglob('*.html')
        yield from root.rglob('*.htm')
    else:
        yield from root.glob('*.html')
        yield from root.glob('*.htm')


def collect_targets(target: Path, recurse: bool) -> list[Path]:
    target = target.expanduser().resolve()
    if target.is_file():
        suf = target.suffix.lower()
        if suf not in ('.html', '.htm'):
            print(f'Not an HTML file: {target}', file=sys.stderr)
            sys.exit(1)
        return [target]
    if not target.is_dir():
        print(f'Not a file or directory: {target}', file=sys.stderr)
        sys.exit(1)
    return sorted(p for p in iter_html_files(target, recurse) if p.is_file())


def main() -> int:
    p = argparse.ArgumentParser(
        description='Add blog thumbnails to old gmplot map HTML info windows.'
    )
    p.add_argument(
        'path',
        type=Path,
        metavar='PATH',
        help='HTML map file (.html / .htm) or directory of maps',
    )
    p.add_argument(
        '--dry-run',
        action='store_true',
        help='Report changes but do not write files',
    )
    p.add_argument(
        '--no-recurse',
        action='store_true',
        help='When PATH is a directory, only scan that folder (not subfolders)',
    )
    p.add_argument(
        '--quiet',
        action='store_true',
        help='Less progress output (still prints file-level start/end)',
    )
    args = p.parse_args()
    paths = collect_targets(args.path, recurse=not args.no_recurse)
    log_detail = not args.quiet

    touched = 0
    total_windows = 0

    for path in paths:
        text = path.read_text(encoding='utf-8', errors='replace')
        if 'InfoWindow' not in text or BLOG_PREFIX not in text:
            print(f'=== skip (not a matching map): {path} ===')
            continue

        size_b = path.stat().st_size
        print(f'=== file: {path} ({size_b} bytes) ===')
        print('  conversion started')
        t_file = time.perf_counter()
        page_cache: dict[str, str] = {}
        new_text, n = replace_info_windows_in_text(
            text,
            page_cache=page_cache,
            log=log_detail,
        )
        elapsed_file = time.perf_counter() - t_file
        if n == 0:
            print(f'  conversion finished in {elapsed_file:.2f}s (nothing to upgrade)')
            print()
            continue
        touched += 1
        total_windows += n
        print(
            f'  conversion finished in {elapsed_file:.2f}s '
            f'({n} InfoWindow(s) updated, {len(page_cache)} unique page fetch(es))'
        )
        if args.dry_run:
            print('  dry-run: not writing file')
        else:
            path.write_text(new_text, encoding='utf-8')
            print('  wrote updated HTML')
        print()

    if args.dry_run and touched:
        print(f'Summary dry-run: {touched} file(s), {total_windows} InfoWindow(s) (not written)')
    elif touched:
        print(f'Summary: updated {touched} file(s), {total_windows} InfoWindow(s)')
    elif paths:
        print('No matching HTML or nothing to upgrade.')
    else:
        print('No HTML files found.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
