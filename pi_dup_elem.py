'''
    Process Images Element to Display Duplicate Groups in a Gallery layout.
'''

import pi_config as c
from pi_dup_group import DuplicateGroupFilter, resolve_duplicate_group_target
from pi_filters import SelectedTreeNodesFilter
from pi_gallery_elem import PiGalleryElem
from pi_util import get_row_for_fn


class PiDupElem(PiGalleryElem):

    def __init__(self, key="-DUP-", event=c.EVT_TREE, cols=3, rows=3):
        # Behave like Gallery: rebuild only on the provided event.
        super().__init__(key=key, event=event, cols=cols, rows=rows)

    def files_selected(self, event, values):
        self._collection_rows = []
        self._selected_rows = []
        self._page = 0

        selected_rows = self._get_selected_rows(event, values)
        all_rows = c.table._original_rows if c.table else []
        dup_target = resolve_duplicate_group_target(selected_rows, all_rows)
        if dup_target:
            self._collection_rows = DuplicateGroupFilter(dup_target).filter(all_rows)
            self._update_status_if_active(values, f'Duplicates for /{dup_target}')
        else:
            self._update_status_if_active(
                values, "Duplicates: no duplicate group for current selection"
            )

        self._display_pg()

    def _get_selected_rows(self, event, values):
        rows = c.table.rows() if c.table else []
        if not rows:
            return []

        if event == c.EVT_TREE:
            selected = values.get(event, [])
            if not selected:
                return []
            return SelectedTreeNodesFilter(selected).filter(rows)

        return []

    def _update_status_if_active(self, values, msg):
        if self._is_active_tab(values):
            c.update_status(msg)

    def _is_active_tab(self, values):
        current_tab = values.get("-TABGROUP-")
        if current_tab:
            return current_tab == "-DUP_TAB-"

        if c.window is not None and "-TABGROUP-" in c.window.AllKeysDict:
            try:
                return c.window["-TABGROUP-"].get() == "-DUP_TAB-"
            except Exception:
                return False

        return False
