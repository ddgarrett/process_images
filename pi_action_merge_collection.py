"""
Merge another image collection folder into the currently open collection.

Safety rules:
- Do not modify the source collection.
- Preflight all checks; on first error, show popup + print and abort.
- Only merge if CSV schemas (column names and order) match exactly.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import FreeSimpleGUI as sg

import pi_config as c
from image_collection import ImageCollection
from pi_action import PiAction


def _row_key(row) -> tuple[str, str]:
    return (row.get("file_location"), row.get("file_name"))


def _folder_for_file_location(root: str, file_location: str) -> Path:
    # file_location in this app typically starts with "/" for subfolders.
    rel = (file_location or "").lstrip("/")
    return Path(root) / rel


def _file_for_row(root: str, row) -> Path:
    folder = _folder_for_file_location(root, row.get("file_location"))
    return folder / (row.get("file_name") or "")


def _fail(msg: str) -> bool:
    print(f"Error: {msg}")
    sg.popup(msg)
    return False


class PiMergeCollection(PiAction):
    def handle_event(self, event, values):
        if not c.table or not c.directory or not c.table.fn:
            sg.popup("No collection loaded. Open a collection folder first.")
            c.update_status("No collection loaded")
            return

        src_root = sg.popup_get_folder(
            "Select folder containing image_collection.csv to merge",
            no_window=True,
        )
        if not src_root:
            c.update_status("Merge collection canceled")
            return

        src_csv = os.path.join(src_root, "image_collection.csv")
        if not os.path.isfile(src_csv):
            _fail(f"No image_collection.csv in {src_root}")
            c.update_status("Merge collection failed")
            return

        # Preflight: schema, duplicates, file existence, and collision-free.
        if not self._preflight(src_root, src_csv):
            c.update_status("Merge collection failed (preflight)")
            return

        copied = self._merge(src_root, src_csv)
        if copied is None:
            c.update_status("Merge collection failed")
            return

        msg = (
            f"Merge complete: {copied} images copied. "
            "Please use File -> Save to complete the merge."
        )
        print(msg)
        sg.popup(msg)
        c.update_status(msg)

    def _preflight(self, src_root: str, src_csv: str) -> bool:
        try:
            src_table = ImageCollection(src_csv)
        except Exception as e:
            return _fail(f"Could not open source collection CSV: {e}")

        cur_cols = list(c.table._cols.keys())
        src_cols = list(src_table._cols.keys())
        if cur_cols != src_cols:
            return _fail(
                "Source collection schema does not match current collection. "
                "Open and save the source collection with the current app version, then retry."
            )

        # Build index of existing rows in current collection (unfiltered).
        cur_keys: set[tuple[str, str]] = set()
        for r in c.table._original_rows:
            cur_keys.add(_row_key(r))

        # Source collection must also have no duplicate keys.
        src_seen: set[tuple[str, str]] = set()
        dst_root = c.directory

        for r in src_table._original_rows:
            key = _row_key(r)
            if key in src_seen:
                loc, name = key
                return _fail(
                    f"Source collection has duplicate row for file_location='{loc}', file_name='{name}'."
                )
            src_seen.add(key)

            if key in cur_keys:
                loc, name = key
                return _fail(
                    f"Duplicate image already exists in current collection CSV: "
                    f"file_location='{loc}', file_name='{name}'."
                )

            src_file = _file_for_row(src_root, r)
            if not src_file.is_file():
                loc, name = key
                return _fail(
                    f"Missing source image file for CSV row: "
                    f"file_location='{loc}', file_name='{name}'. Expected: {src_file}"
                )

            dst_file = _file_for_row(dst_root, r)
            if dst_file.exists():
                loc, name = key
                return _fail(
                    f"Destination file already exists: {dst_file} "
                    f"(file_location='{loc}', file_name='{name}')."
                )

        return True

    def _merge(self, src_root: str, src_csv: str) -> int | None:
        try:
            src_table = ImageCollection(src_csv)
        except Exception as e:
            _fail(f"Could not open source collection CSV: {e}")
            return None

        # Remove any filters before merge so we append to full set.
        c.table.filter_rows()

        dst_root = c.directory
        cols = list(c.table._cols.keys())

        copied = 0
        for src_row in src_table._original_rows:
            src_file = _file_for_row(src_root, src_row)
            dst_file = _file_for_row(dst_root, src_row)
            dst_dir = dst_file.parent
            dst_dir.mkdir(parents=True, exist_ok=True)

            # Preflight should guarantee no collisions, but keep it safe.
            if dst_file.exists():
                loc, name = _row_key(src_row)
                _fail(
                    f"Unexpected destination collision during merge: {dst_file} "
                    f"(file_location='{loc}', file_name='{name}')."
                )
                return None

            shutil.copy2(src_file, dst_file)

            new_row = c.table.new_row()
            for col in cols:
                new_row[col] = src_row.get(col)

            copied += 1

        c.table.resort()
        c.table.renumber()
        c.listeners.notify(c.EVT_TABLE_LOAD, c.last_window_values or {})
        return copied

