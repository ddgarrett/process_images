'''
    Show → Duplicate Group: filter the collection to one duplicate cluster
    based on the current selection (tree, gallery, or main image).
'''
from __future__ import annotations

import pi_config as c
from pi_action import PiAction
from pi_dup_group import DuplicateGroupFilter, resolve_duplicate_group_target


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
