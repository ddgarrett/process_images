'''
    Show → Duplicate Group: filter the collection to one duplicate cluster
    based on the current selection (tree, gallery, or main image).
'''
from __future__ import annotations

import pi_config as c
from pi_action import PiAction
from pi_filters import Filter
from table import Row


def row_dup_ref(row: Row) -> str:
    '''How a row is identified in ``dup_photo``: ``file_location``/``file_name``.

    Matches tree paths built with ``file_location`` + ``/`` + ``file_name``.
    '''
    loc = row.get('file_location') or ''
    fn = row.get('file_name') or ''
    loc = loc.rstrip('/')
    return f'{loc}/{fn}' if loc else fn


def normalize_dup_path_key(s: str) -> str:
    '''Canonical key for comparing ``dup_photo`` to ``row_dup_ref``.

    ``file_location`` often has a leading ``/`` (e.g. ``/2024-09-10``) while
    CSV ``dup_photo`` may omit it (``2024-09-10/PXL_....jpg``). Normalizing
    strips leading slashes and normalizes backslashes so both match.
    '''
    t = str(s or '').strip().replace('\\', '/')
    return t.lstrip('/')


def resolve_duplicate_group_target(selected: list[Row], all_rows: list[Row]) -> str | None:
    '''Return the normalized cluster key for ``dup_photo`` / row refs, or None.

    Uses the first row in *selected* (in order) that either has a non-blank
    ``dup_photo`` or is referenced by another row's ``dup_photo`` (same
    normalized key as this row's ``row_dup_ref``). Search uses *all_rows*.
    '''
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
    '''Keep the canonical row(s) for ``dup_target`` and rows with that ``dup_photo``.'''

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


class PiShowDuplicateGroup(PiAction):
    last_id = 0

    @classmethod
    def next_id(cls):
        cls.last_id += 1
        return cls.last_id

    def __init__(self, text="Duplicate &Group", rowget=None):
        self._id = self.next_id()
        self._text = text
        self._rowget = rowget
        super().__init__(event=self._get_event())

    def _get_event(self):
        return f'-PiShowDupGroup{self._id}-'

    def item(self):
        return f'{self._text}::{self._get_event()}'

    def handle_event(self, event, values):
        if not c.table:
            return
        if self._rowget is None:
            c.update_status("Duplicate Group: not available here")
            return
        selected = [r for r in (self._rowget(values) or []) if r is not None]
        if not selected:
            c.update_status("Duplicate Group: select one or more images first")
            return
        all_rows = c.table._original_rows
        dup_target = resolve_duplicate_group_target(selected, all_rows)
        if dup_target is None:
            c.update_status(
                "Duplicate Group: selection is not in a duplicate chain "
                "(no dup_photo and not referenced by another row's dup_photo)"
            )
            return
        flt = DuplicateGroupFilter(dup_target)
        c.table.filter_rows(flt)
        c.listeners.notify(c.EVT_TABLE_LOAD, values)
        c.update_status(f"Collection filtered for {flt.get_descr()}")
