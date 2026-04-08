## Display Logic From Cosine Similarity and MUSIQ Score

This document describes how a final display value in `process_images` is derived from:

1. Duplicate detection in `image_analysis_lib` (cosine similarity + score ordering)
2. Status assignment in `image_scores_and_status.csv`
3. Optional `dedup_parms.json` written beside that CSV (thresholds used on that dedupe run)
4. Import mapping into `image_collection.csv` (`img_status`, `rvw_lvl`, `cosine_sim`)
5. UI display translation for `img_status == "tbd"` (`Reject?`, `Bad?`, `Dup?`, `Good?`, `Best?`)
6. Optional **Recalc Status** (tree context menu): re-apply thresholds from a `dedup_parms.json` without re-running CNN dedupe

Shared rules live in `image_analysis_lib/scoring.py` (`csv_status_for_row`, `status_csv_to_collection_fields`, `collection_fields_from_score_bands`, etc.).

### Symbols

- `S` = `musiq_score` for the row
- `PQT` = `poor_quality_threshold` (default `4.0`)
- `MST` = `min_similarity_threshold` (default `0.65`)
- `BST` = `best_score_threshold` (default `6.0`): CSV `best` when `S > BST` (strictly greater, same as prior hardcoded `6`)
- `TBS` = `tbd_best_score_threshold` (default `5.0`): CSV `good` when `S > TBS` after the `best` check (same as prior hardcoded `5`)
- `sim` = cosine similarity between duplicate image and assigned higher-scoring keeper
- Duplicate checks run only for rows with `S >= PQT`, within the same folder, and only against lower-priority rows in score order.

---

### A) Dedup + status CSV logic

| Condition | `status` in `image_scores_and_status.csv` | `dup_photo` | `cosine_sim` |
|---|---|---|---|
| `S` exists and `S < PQT` | `poor quality` | empty | `-1` |
| `S >= PQT` and duplicate (`sim >= MST` vs higher-scored keeper, same folder, GPS gate if enabled) | `dup` | keeper relative path | `sim` (numeric) |
| Not duplicate, and `S > BST` | `best` | empty | `-1` |
| Not duplicate, and `S > TBS` (and not `best` above) | `good` | empty | `-1` |
| All other cases (including missing or invalid score when not duplicate) | `TBD` | empty | `-1` |

---

### B) Import mapping into `image_collection.csv`

| CSV `status` | `img_status` | `rvw_lvl` |
|---|---|---|
| `poor quality` | `bad` | `"1"` |
| `dup` | `dup` | `"2"` |
| `best` | `best` | `"5"` |
| `good` | `tbd` | `"4"` |
| `TBD` | `tbd` | `"3"` |
| unknown or empty | `tbd` | `"0"` |

`cosine_sim` from the scores CSV is copied into the collection when that column exists; if the column is missing during import, the field is left empty for those rows. New collections include a `cosine_sim` column; older `image_collection.csv` files gain it on load (default blank) without breaking column order (`cosine_sim` is after `dup_target` in metadata).

---

### C) Display translation in UI

For non-`tbd` statuses, display is the raw status (`bad`, `dup`, `best`, etc.) with no question suffix.

For `img_status == "tbd"`, display text is determined by `rvw_lvl`:

| `img_status` | `rvw_lvl` | Display pair |
|---|---|---|
| `tbd` | `"0"` | `tbd, Reject?` |
| `tbd` | `"1"` | `tbd, Bad?` |
| `tbd` | `"2"` | `tbd, Dup?` |
| `tbd` | `"3"` | `tbd, Good?` |
| `tbd` | `"4"` | `tbd, Best?` |
| `tbd` | `"5"` | `tbd, ???` |

---

### D) End-to-end outcomes driven by cosine + score (initial dedupe)

| Core condition (`sim`, `S`) | CSV `status` | Imported (`img_status`,`rvw_lvl`) | Display |
|---|---|---|---|
| `S < PQT` | `poor quality` | `bad`, `"1"` | `bad` |
| `S >= PQT` and duplicate (`sim >= MST` to higher-scored keeper) | `dup` | `dup`, `"2"` | `dup` |
| Not duplicate and `S > BST` | `best` | `best`, `"5"` | `best` |
| Not duplicate and `S > TBS` (and not classed as `best`) | `good` | `tbd`, `"4"` | `tbd, Best?` |
| Not duplicate and neither band above (or score missing/invalid) | `TBD` | `tbd`, `"3"` (or `"0"` if unknown status text) | `tbd, Good?` (or `tbd, Reject?`) |

---

### E) `dedup_parms.json`

Written in the **same directory** as `image_scores_and_status.csv` when dedupe produces that CSV. Typical keys: `poor_quality_threshold`, `min_similarity_threshold`, `gps_radius_meters`, `best_score_threshold`, `tbd_best_score_threshold`, `musiq_csv_size`, `musiq_csv_prefix`.

You can copy and edit this file, then use **Recalc Status** in `process_images` to tune thresholds without re-encoding images (see below).

---

### F) Recalc Status (folder, quick tuning)

- **Menu:** tree right-click, **Recalc Status** (uses the folder of the selection).
- **Parm file:** `dedup_parms.json` in that folder, or if missing, one level up in the directory tree. If still missing, console: `Warning: "dedup_parms.json" file not found.` and no changes.
- **Scope:** all collection rows whose `file_location` matches the selected folder.
- **`dup_photo`:** never cleared; raised `MST` can drop `img_status` out of `dup` while links stay for a later lower threshold.
- **Blank `cosine_sim`:** cosine threshold step is skipped for that row; if `img_status` is not `dup`, score bands still run using parms. If `img_status` is `dup` and `cosine_sim` is blank, that row is left unchanged. Console lists how many rows had blank `cosine_sim` for the cosine skip message.
- **`-1` `cosine_sim`:** treat as not a duplicate for cosine logic; apply score bands only.
- **Numeric `cosine_sim`:** if `sim >= MST` (from JSON) and `dup_photo` non-empty, set collection to dup (`img_status` / `rvw_lvl`); otherwise apply score bands (same shared `collection_fields_from_score_bands` + mapping as import).

Recalc overwrites `img_status` / `rvw_lvl` for affected rows per the rules above (manual edits there are not preserved).

---

### Notes

- Duplicate status from dedupe takes precedence over score bands once a row is in `duplicate_to_keeper`.
- Poor quality (`S < PQT`) is checked before duplicate assignment.
- CSV `good` maps to `img_status="tbd"` at level `"4"`, so display is `tbd, Best?`, not `good`.
