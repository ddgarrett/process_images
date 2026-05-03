'''
    Display a Tree List based on data in the global config.table table
'''


import FreeSimpleGUI as sg

import pi_config as c
from pi_action_blog import PiActionBlog
from pi_action_export import PiActionExport
from pi_action_map import PiActionMap
from pi_element import PiElement
from pi_filters import SelectedTreeNodesFilter
from pi_treedata import PiTreeData
from status_menu import StatusMenu

MUSIQ_SLIDER_MIN_NO_FILTER = 3.0


def _musiq_cell_at_or_above_threshold(cell, thr: float) -> bool:
    if cell is None:
        return False
    s = str(cell).strip()
    if len(s) != 5 or s[1] != ".":
        return False
    if not all(ch.isdigit() for ch in (s[0], s[2], s[3], s[4])):
        return False
    floor_s = f"{round(thr, 1):.3f}"
    return s >= floor_s


def _musiq_cell_strictly_below_threshold(cell, thr: float) -> bool:
    if cell is None:
        return False
    s = str(cell).strip()
    if len(s) != 5 or s[1] != ".":
        return False
    if not all(ch.isdigit() for ch in (s[0], s[2], s[3], s[4])):
        return False
    floor_s = f"{round(thr, 1):.3f}"
    return s < floor_s


def _tree_slider_value(values):
    base = c.last_window_values if c.last_window_values is not None else {}
    overlay = values if values is not None else {}
    merged = {**base, **overlay}
    try:
        return round(float(merged.get(c.EVT_TREE_SCORE, MUSIQ_SLIDER_MIN_NO_FILTER)), 1)
    except (TypeError, ValueError):
        return MUSIQ_SLIDER_MIN_NO_FILTER


def get_tree_visible_rows(values, score_cmp_less_than=False):
    rows = c.table.rows() if c.table else []
    thr = _tree_slider_value(values)
    visible = []
    for row in rows:
        if score_cmp_less_than:
            keep = _musiq_cell_strictly_below_threshold(row.get("musiq_score"), thr)
        else:
            keep = _musiq_cell_at_or_above_threshold(row.get("musiq_score"), thr)
        if keep:
            visible.append(row)
    return visible


class PiTreeList(PiElement):

    def __init__(self,key="-TREE-",headings=[],events=[]):
        super().__init__(key)

        c.listeners.add(c.EVT_TABLE_LOAD,self.update_list)
        c.listeners.add(c.EVT_TABLE_ROW_CHG,self.update_rows)

        menu = None

        if c.app_function == c.APP_RVW_IMG:
            status_menu = StatusMenu()
            menu = ['',
            [ status_menu.get_set_menu(),
                '---',
                f'Recalc Status::{c.EVT_RECALC_STATUS}',
                PiActionMap(rowget=self.get_selected_rows).item(), 
                PiActionExport(rowget=self.get_selected_rows).item(), 
                PiActionBlog(rowget=self.get_selected_rows).item(),
                f'Properties::{c.EVT_FILE_PROPS}',
                'S&how', status_menu.get_show_submenu(),
                f'&Save::{c.EVT_FILE_SAVE}',
                f'E&xit::{c.EVT_EXIT}' ]]
        self._menu = menu

        self._tree_data = PiTreeData(c.table.rows())
        self._score_slider_key = c.EVT_TREE_SCORE
        self._score_cmp_btn_key = f"{self.key}SCORECMP-"
        self._score_cmp_less_than = c.tree_score_cmp_less_than
        self._show_events = (
            c.EVT_SHOW_ALL,
            c.EVT_SHOW_TBD,
            c.EVT_SHOW_POSSIBLE_DUP,
            c.EVT_SHOW_POSSIBLE_GOOD_PLUS,
            c.EVT_SHOW_POSSIBLE_BEST,
            c.EVT_SHOW_TBD_BEST_PLUS_BEST,
            c.EVT_SHOW_FINAL_BEST,
        )
        self._tree = (
            sg.Tree(data=self._tree_data,
                    headings=headings,
                    auto_size_columns=True,
                    select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                    num_rows=5,
                    col0_width=25,
                    key=self.key,
                    # show_expanded=False,
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    right_click_menu=menu
                    )
            )
        
        self._key_id_dict = {}
        c.listeners.add(self._score_slider_key, self._tree_score_changed)
        c.listeners.add(self._score_cmp_btn_key, self._toggle_tree_score_comparator)
        for evt in self._show_events:
            c.listeners.add(evt, self._show_filter_selected)

    def get_element(self) -> sg.Column:
        cmp_button = sg.Button(
            self._score_cmp_button_text(),
            key=self._score_cmp_btn_key,
            enable_events=True,
            tooltip="Toggle  score comparator",
            button_color=self._score_cmp_button_color(),
            size=(8, 1),
            pad=((8, 8), (2, 6)),
        )
        score_slider = sg.Slider(
            (3.0, 6.0),
            default_value=3.0,
            orientation="h",
            resolution=0.1,
            enable_events=True,
            key=self._score_slider_key,
            size=(28, 16),
            pad=((8, 8), (2, 6)),
        )
        slider_row = [
            sg.Push(),
            sg.Column([[cmp_button]], pad=(0, 0), vertical_alignment="bottom"),
            sg.Column([[score_slider]], pad=(0, 0), vertical_alignment="bottom"),
            sg.Push(),
        ]
        return sg.Column([[self._tree], slider_row], expand_x=True, expand_y=True, pad=(0, 0))
    
    def get_selected_rows(self,values):
        ''' Return a list of selected rows. 
            A selected folder returns all of the rows in the folder.
            Values is the values returned by window.read().
            Therefore we extract the list of selected
            files and folders via our own key.
        '''
        files_folders = values[self.key]
        rows = self._tree_data.rows
        if len(rows) == 0 or len(files_folders) == 0:
            return []
        
        filter = SelectedTreeNodesFilter(files_folders)
        rows = filter.filter(rows)
        # print(f'{len(rows)} rows selected')
        return rows

    ''' Event Handlers '''
    def update_list(self,event,values):
        ''' Update the tree data after a table is loaded or filtered '''
        self._rebuild_tree(values)
        self._update_status_summary(values)
        self._notify_tree_selection_with_threshold(values, self._tree_slider_value(values))

    def update_rows(self,event,values):
        ''' update display after row value changes '''
        rows = values[c.EVT_TABLE_ROW_CHG]
        self._tree_data._update_rows(self._tree,self._key_id_dict,rows)

    def _tree_score_changed(self, event, values):
        threshold = self._tree_slider_value(values)
        self._rebuild_tree(values)
        self._update_status_summary(values)
        self._notify_tree_selection_with_threshold(values, threshold)

    def _toggle_tree_score_comparator(self, event, values):
        self._score_cmp_less_than = not self._score_cmp_less_than
        c.tree_score_cmp_less_than = self._score_cmp_less_than
        if c.window is not None and self._score_cmp_btn_key in c.window.AllKeysDict:
            c.window[self._score_cmp_btn_key].update(
                text=self._score_cmp_button_text(),
                button_color=self._score_cmp_button_color(),
            )
        threshold = self._tree_slider_value(values)
        # Keep tree slider threshold, but reset tab sliders to "off".
        self._sync_tab_sliders(MUSIQ_SLIDER_MIN_NO_FILTER)
        base = c.last_window_values if c.last_window_values is not None else {}
        overlay = values if values is not None else {}
        merged = {**base, **overlay}
        merged[self._score_slider_key] = threshold
        self._rebuild_tree(merged)
        self._update_status_summary(merged)
        self._notify_tree_selection_with_threshold(merged, threshold)

    def _show_filter_selected(self, event, values):
        threshold = MUSIQ_SLIDER_MIN_NO_FILTER
        if c.window is not None and self._score_slider_key in c.window.AllKeysDict:
            c.window[self._score_slider_key].update(value=threshold)
        self._sync_tab_sliders(threshold)

    def _tree_slider_value(self, values):
        return _tree_slider_value(values)

    def _sync_tab_sliders(self, threshold):
        if c.window is None:
            return
        c.syncing_from_tree = True
        try:
            for key in ("-GALLERY-MUSIQ-", "-DUP-MUSIQ-"):
                if key in c.window.AllKeysDict:
                    c.window[key].update(value=threshold)
        finally:
            c.syncing_from_tree = False

    def _notify_tree_selection_with_threshold(self, values, threshold):
        base = c.last_window_values if c.last_window_values is not None else {}
        overlay = values if values is not None else {}
        merged = {**base, **overlay}
        merged[self._score_slider_key] = threshold
        merged[self.key] = self._current_tree_selection_keys()
        c.listeners.notify(self.key, merged)

    def _visible_rows(self, values):
        return get_tree_visible_rows(values, self._score_cmp_less_than)

    def _snapshot_tree_state(self):
        if c.window is None:
            return [], []
        widget = c.window[self.key].Widget
        selected_keys = []
        expanded_keys = []
        for item_id in widget.selection():
            key = self._tree.IdToKey.get(item_id)
            if key is not None:
                selected_keys.append(key)
        for item_id, key in self._tree.IdToKey.items():
            try:
                if widget.item(item_id, "open"):
                    expanded_keys.append(key)
            except Exception:
                continue
        return selected_keys, expanded_keys

    def _restore_tree_state(self, selected_keys, expanded_keys):
        if c.window is None:
            return
        widget = c.window[self.key].Widget
        key_to_id = {key: item_id for item_id, key in self._tree.IdToKey.items()}
        for key in expanded_keys:
            item_id = key_to_id.get(key)
            if item_id is not None:
                try:
                    widget.item(item_id, open=True)
                except Exception:
                    pass
        selected_ids = []
        for key in selected_keys:
            item_id = key_to_id.get(key)
            if item_id is not None:
                selected_ids.append(item_id)
        try:
            widget.selection_set(selected_ids)
            if len(selected_ids) > 0:
                widget.focus(selected_ids[0])
        except Exception:
            pass

    def _rebuild_tree(self, values):
        selected_keys, expanded_keys = self._snapshot_tree_state()
        self._tree_data = PiTreeData(self._visible_rows(values))
        c.window[self.key].update(values=self._tree_data)
        self._key_id_dict = {v:k for k, v in self._tree.IdToKey.items()}
        self._restore_tree_state(selected_keys, expanded_keys)

    def _update_status_summary(self, values):
        threshold = self._tree_slider_value(values)
        score_txt = f"{self._score_cmp_symbol()}{threshold:.1f}"
        show_txt = c.current_show_filter_label
        visible = len(self._tree_data.rows)
        c.update_status(
            f"Show: {show_txt} | Score: {score_txt} | Visible files: {visible}"
        )

    def _score_cmp_button_text(self):
        if self._score_cmp_less_than:
            return "Score <"
        return "Score >="

    def _score_cmp_symbol(self):
        if self._score_cmp_less_than:
            return "<"
        return ">="

    def _score_cmp_button_color(self):
        if self._score_cmp_less_than:
            return ("white", "#1F7A1F")
        return ("white", "#2F5D8A")

    def _current_tree_selection_keys(self):
        if c.window is None:
            return []
        widget = c.window[self.key].Widget
        keys = []
        for item_id in widget.selection():
            key = self._tree.IdToKey.get(item_id)
            if key is not None:
                keys.append(key)
        return keys

