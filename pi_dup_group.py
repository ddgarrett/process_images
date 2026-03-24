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


def refresh_dup_target_flags(rows: list[Row]) -> None:
    '''Set each row's dup_target to T or F from dup_photo links.

    T when another row's non-blank dup_photo normalizes to this row's
    row_dup_ref. Otherwise F.
    '''
    if not rows:
        return
    referenced: set[str] = set()
    for r in rows:
        dp = r.get('dup_photo')
        if str(dp or '').strip():
            referenced.add(normalize_dup_path_key(dp))
    for r in rows:
        key = normalize_dup_path_key(row_dup_ref(r))
        val = 'T' if key in referenced else 'F'
        r.set('dup_target', val)


def resolve_duplicate_group_target(selected: list[Row], all_rows: list[Row]) -> str | None:
    '''Return the normalized duplicate group key, or None if no chain found.

    For the canonical-row case, ``dup_target`` is always uppercase ``T`` or ``F``.
    Callers should refresh flags after ``dup_photo`` changes (e.g.
    ``apply_musiq_scores_csv``).
    '''
    if not selected or not all_rows:
        return None

    for row in selected:
        dp = row.get('dup_photo')
        if str(dp or '').strip():
            return normalize_dup_path_key(dp)

        if row.get('dup_target') == 'T':
            return normalize_dup_path_key(row_dup_ref(row))

    return None


class DuplicateGroupFilter(Filter):
    '''Keep rows in a duplicate cluster given normalized path key *cluster_key*.'''

    def __init__(self, cluster_key: str):
        self._cluster_key = cluster_key

    def test(self, row: Row):
        key = normalize_dup_path_key(row_dup_ref(row))
        dp_key = normalize_dup_path_key(row.get('dup_photo'))
        return key == self._cluster_key or dp_key == self._cluster_key

    def get_descr(self):
        if not self._cluster_key:
            return "Duplicate group"
        return f"Duplicate group (/{self._cluster_key})"
