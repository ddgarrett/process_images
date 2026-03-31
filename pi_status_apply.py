"""
Single registration for all "Set status" right-click menu choices.

Row targets come from pi_config.status_menu_rowgetter, set on secondary-click
before the menu runs (macOS: pi_macos_popup; other OS: pi_status_menu_context).
"""

from pi_action import PiAction

import pi_config as c

_STATUS_SPECS = None


def _effective_values(values):
    if values is not None:
        return values
    return c.last_window_values if c.last_window_values is not None else {}


def _apply_status(event, values, status, level):
    rowget = c.status_menu_rowgetter
    if rowget is None:
        return
    vals = _effective_values(values)
    rows = rowget(vals)
    rows = [r for r in (rows or []) if r is not None]
    if not rows:
        return
    for row in rows:
        row['rvw_lvl'] = level
        row['img_status'] = status
    vals = dict(vals)
    vals[c.EVT_TABLE_ROW_CHG] = rows
    c.listeners.notify(c.EVT_TABLE_ROW_CHG, vals)


class PiStatusMenuApply(PiAction):
    """One PiAction per canonical status menu event."""

    def __init__(self, event, status, level):
        self._status = status
        self._level = level
        super().__init__(event=event)

    def handle_event(self, event, values):
        _apply_status(event, values, self._status, self._level)


def register_status_menu_handlers():
    """Register each status choice once (safe to call multiple times)."""
    global _STATUS_SPECS
    if _STATUS_SPECS is not None:
        return
    _STATUS_SPECS = [
        (c.EVT_STATUS_SET_REJECT, c.STAT_REJECT, c.LVL_INITIAL),
        (c.EVT_STATUS_SET_POOR_QUALITY, c.STAT_QUAL_BAD, c.LVL_QUAL),
        (c.EVT_STATUS_SET_DUPLICATE, c.STAT_DUP, c.LVL_DUP),
        (c.EVT_STATUS_SET_JUST_OKAY, c.STAT_OK, c.LVL_OK),
        (c.EVT_STATUS_SET_GOOD, c.STAT_GOOD, c.LVL_GOOD),
        (c.EVT_STATUS_SET_BEST, c.STAT_BEST, c.LVL_BEST),
        (c.EVT_STATUS_TBD_REJECT, c.STAT_TBD, c.LVL_INITIAL),
        (c.EVT_STATUS_TBD_POOR_QUALITY, c.STAT_TBD, c.LVL_QUAL),
        (c.EVT_STATUS_TBD_DUPLICATE, c.STAT_TBD, c.LVL_DUP),
        (c.EVT_STATUS_TBD_OK_GOOD_BEST, c.STAT_TBD, c.LVL_OK),
        (c.EVT_STATUS_TBD_GOOD_OR_BEST, c.STAT_TBD, c.LVL_GOOD),
    ]
    for evt, st, lvl in _STATUS_SPECS:
        PiStatusMenuApply(evt, st, lvl)
