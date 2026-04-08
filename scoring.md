## Display Logic From Cosine Similarity and MUSIQ Score

This document describes how a final display value in `process_images` is derived from:

1. Duplicate detection in `image_analysis_lib` (cosine similarity + score ordering)
2. Status assignment in `image_scores_and_status.csv`
3. Import mapping into `image_collection.csv` (`img_status`, `rvw_lvl`)
4. UI display translation for `img_status == "tbd"` (`Reject?`, `Bad?`, `Dup?`, `Good?`, `Best?`)

### Symbols

- `S` = `musiq_score` for the row
- `PQT` = `poor_quality_threshold` (default `4.0`)
- `MST` = `min_similarity_threshold` (default `0.65`)
- `sim` = cosine similarity between this image and a higher-scoring candidate keeper
- Duplicate checks run only for rows with `S >= PQT`, within the same folder, and only against lower-priority rows in score order.

---

### A) Dedup + Status CSV logic

| Condition | `status` in `image_scores_and_status.csv` | `dup_photo` |
|---|---|---|
| `S` exists and `S < PQT` | `poor quality` | empty |
| `S >= PQT` and row is marked duplicate (`sim >= MST` vs higher-scored keeper, same folder, GPS gate if enabled) | `dup` | keeper relative path |
| Not duplicate, and `S > 6` | `best` | empty |
| Not duplicate, and `5 < S <= 6` | `good` | empty |
| All other cases (including missing or invalid score when not duplicate) | `TBD` | empty |

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

### D) End-to-end outcomes driven by cosine + score

| Core condition (`sim`, `S`) | CSV `status` | Imported (`img_status`,`rvw_lvl`) | Display |
|---|---|---|---|
| `S < PQT` | `poor quality` | `bad`, `"1"` | `bad` |
| `S >= PQT` and duplicate (`sim >= MST` to higher-scored keeper) | `dup` | `dup`, `"2"` | `dup` |
| Not duplicate and `S > 6` | `best` | `best`, `"5"` | `best` |
| Not duplicate and `5 < S <= 6` | `good` | `tbd`, `"4"` | `tbd, Best?` |
| Not duplicate and `S <= 5` (or score missing/invalid) | `TBD` | `tbd`, `"3"` (or `"0"` if unknown) | `tbd, Good?` (or `tbd, Reject?`) |

---

### Notes

- Duplicate status takes precedence over score bands once duplicate is detected.
- Poor quality (`S < PQT`) is checked before duplicate assignment.
- In current mapping, CSV `good` maps to `img_status="tbd"` at level `"4"`, so display is `tbd, Best?`, not `good`.
