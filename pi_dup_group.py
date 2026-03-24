'''
    Shared duplicate-group helper logic used by actions and UI elements.
'''
from __future__ import annotations

from pi_filters import Filter
from table import Row


def row_dup_ref(row: Row) -> str:
    '''How a row is identified in ``dup_photo``: ``file_location``/``file_name``.'''
    loc = row.get('file_location') or ''
    fn = row.get('file_name') or ''
    loc = loc.rstrip('/')
    return f'{loc}/{fn}' if loc else fn


def normalize_dup_path_key(s: str) -> str:
    '''Canonical key for comparing ``dup_photo`` to ``row_dup_ref``.'''
    t = str(s or '').strip().replace('\\', '/')
    return t.lstrip('/')


def resolve_duplicate_group_target(selected: list[Row], all_rows: list[Row]) -> str | None:
    '''Return the normalized duplicate group key, or None if no chain found.'''
    if not selected or not all_rows:
        return None

    for row in selected:
        dp = row.get('dup_photo')
        if str(dp or '').strip():
            return normalize_dup_path_key(dp)

        ref = normalize_dup_path_key(row_dup_ref(row))
        if ref and any(
            normalize_dup_path_key(r.get('dup_photo')) == ref for r in all_rows
        ):
            return ref

    return None


class DuplicateGroupFilter(Filter):
    '''Keep canonical row(s) for ``dup_target`` and rows with that ``dup_photo``.'''

    def __init__(self, dup_target: str):
        self._dup_target = dup_target

    def test(self, row: Row):
        key = normalize_dup_path_key(row_dup_ref(row))
        dp_key = normalize_dup_path_key(row.get('dup_photo'))
        return key == self._dup_target or dp_key == self._dup_target

    def get_descr(self):
        if not self._dup_target:
            return "Duplicate group"
        return f"Duplicate group (/{self._dup_target})"
