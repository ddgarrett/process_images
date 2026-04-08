"""
Recalculate img_status and rvw_lvl for one folder using dedup_parms.json and
stored musiq_score, cosine_sim, dup_photo (dup_photo is not cleared).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pi_config as c
from pi_action import PiAction
from pi_dup_group import refresh_dup_target_flags

try:
    from image_analysis_lib.scoring import (
        COSINE_SIM_SENTINEL,
        collection_fields_from_score_bands,
        parse_cosine_cell,
        parse_musiq_score,
        status_csv_to_collection_fields,
    )

    _parse_musiq_score = parse_musiq_score
except ImportError as e:
    _parse_musiq_score = None  # type: ignore
    _IMPORT_ERR = e
else:
    _IMPORT_ERR = None

DEDUP_PARMS_NAME = "dedup_parms.json"


def _fs_dir_for_file_location(root: str, file_location: str) -> Path:
    loc = (file_location or "").strip().replace("\\", "/").lstrip("/")
    if not loc:
        return Path(root)
    return Path(root) / loc


def find_dedup_parms_path(root: str, file_location: str) -> str | None:
    """Return file path to dedup_parms.json in folder or parent, or None."""
    folder = _fs_dir_for_file_location(root, file_location)
    direct = folder / DEDUP_PARMS_NAME
    if direct.is_file():
        return str(direct)
    parent = folder.parent
    if parent != folder:
        up = parent / DEDUP_PARMS_NAME
        if up.is_file():
            return str(up)
    return None


def recalc_rows_for_folder(
    rows: list,
    *,
    target_file_location: str,
    poor_quality_threshold: float,
    min_similarity_threshold: float,
    best_score_threshold: float,
    tbd_best_score_threshold: float,
) -> tuple[list, int]:
    """
    Update img_status and rvw_lvl for rows in target_file_location.
    dup_photo is never changed. Returns (updated_row_list, blank_cosine_count).
    """
    updated: list = []
    blank_cosine = 0

    for row in rows:
        if row.get("file_location") != target_file_location:
            continue

        sim = parse_cosine_cell(row.get("cosine_sim"))
        score = _parse_musiq_score(row.get("musiq_score"))
        dup_photo_ok = str(row.get("dup_photo") or "").strip() != ""

        if sim is None:
            blank_cosine += 1
            if row.get("img_status") == "dup":
                continue
            img_st, rvw = collection_fields_from_score_bands(
                score,
                poor_quality_threshold=poor_quality_threshold,
                best_score_threshold=best_score_threshold,
                tbd_best_score_threshold=tbd_best_score_threshold,
            )
        elif sim == float(COSINE_SIM_SENTINEL):
            img_st, rvw = collection_fields_from_score_bands(
                score,
                poor_quality_threshold=poor_quality_threshold,
                best_score_threshold=best_score_threshold,
                tbd_best_score_threshold=tbd_best_score_threshold,
            )
        elif sim >= min_similarity_threshold and dup_photo_ok:
            img_st, rvw = status_csv_to_collection_fields("dup")
        else:
            img_st, rvw = collection_fields_from_score_bands(
                score,
                poor_quality_threshold=poor_quality_threshold,
                best_score_threshold=best_score_threshold,
                tbd_best_score_threshold=tbd_best_score_threshold,
            )

        row["img_status"] = img_st
        row["rvw_lvl"] = rvw
        updated.append(row)

    return updated, blank_cosine


class PiRecalcFolderStatus(PiAction):
    """Recalc status for rows in the folder of the current tree selection."""

    def __init__(self, event: str, rowget):
        self._rowget = rowget
        super().__init__(event=event)

    def handle_event(self, event, values):
        if _IMPORT_ERR is not None or _parse_musiq_score is None:
            print(
                "Recalc Status requires image_analysis_lib: ",
                _IMPORT_ERR,
            )
            c.update_status("Recalc Status: image_analysis_lib not available.")
            return

        if not c.table or not c.directory:
            c.update_status("No collection loaded.")
            return

        rows = self._rowget(values)
        rows = [r for r in (rows or []) if r is not None]
        if not rows:
            c.update_status("Recalc Status: no rows selected.")
            return

        target_loc = rows[0].get("file_location")
        parms_path = find_dedup_parms_path(c.directory, target_loc)
        if not parms_path:
            print(f'Warning: "{DEDUP_PARMS_NAME}" file not found.')
            c.update_status(f"Recalc Status: {DEDUP_PARMS_NAME} not found.")
            return

        try:
            with open(parms_path, encoding="utf-8") as f:
                parms = json.load(f)
        except OSError as e:
            print(f"Recalc Status: could not read {parms_path}: {e}")
            return

        pqt = float(parms["poor_quality_threshold"])
        mst = float(parms["min_similarity_threshold"])
        best_t = float(parms["best_score_threshold"])
        tbd_t = float(parms["tbd_best_score_threshold"])

        all_rows = c.table._original_rows
        touch_rows, blank_n = recalc_rows_for_folder(
            all_rows,
            target_file_location=target_loc,
            poor_quality_threshold=pqt,
            min_similarity_threshold=mst,
            best_score_threshold=best_t,
            tbd_best_score_threshold=tbd_t,
        )

        if blank_n:
            print(
                f"{blank_n} rows: blank cosine_sim; cosine threshold adjustment skipped; "
                "score bands still applied where applicable."
            )

        refresh_dup_target_flags(all_rows)
        vals = dict(values or {})
        vals[c.EVT_TABLE_ROW_CHG] = touch_rows
        c.listeners.notify(c.EVT_TABLE_ROW_CHG, vals)
        c.update_status(
            f"Recalc Status: updated {len(touch_rows)} row(s) using {os.path.basename(parms_path)}."
        )


def register_recalc_status_handler(rowget):
    PiRecalcFolderStatus(c.EVT_RECALC_STATUS, rowget)
