## End-to-End Status Logic (Landscape Print)

| Dedup inputs | CSV status | Collection (`img_status`,`rvw_lvl`) | `cosine_sim` | Display |
|---|---|---|---|---|
| `S < PQT` | `poor quality` | `bad`, `"1"` | `-1` | `bad` |
| `S >= PQT` and duplicate (`sim >= MST`, same folder, GPS if enabled) | `dup` | `dup`, `"2"` | `sim` | `dup` |
| Not duplicate and `S > BST` | `best` | `best`, `"5"` | `-1` | `best` |
| Not duplicate and `S > TBS` (not `best`) | `good` | `tbd`, `"4"` | `-1` | `tbd, Best?` |
| Not duplicate, else | `TBD` | `tbd`, `"3"` | `-1` | `tbd, Good?` |
| Unknown or empty CSV status (import) | unknown / empty | `tbd`, `"0"` | varies | `tbd, Reject?` |

**Parms file:** `dedup_parms.json` next to `image_scores_and_status.csv` (same thresholds as that run). **Recalc Status:** tree menu; uses parms in folder or parent; keeps `dup_photo`; blank `cosine_sim` skips cosine adjust for that row (see `scoring.md`).

### Legend

- `S` = `musiq_score`
- `PQT` = poor quality threshold (default `4.0`)
- `MST` = min cosine similarity for dup (default `0.65`)
- `BST` = best score threshold (default `6.0`), `TBS` = good band threshold (default `5.0`)
- After `S > BST` check, `S > TBS` yields CSV `good`; else `TBD` (if not poor / dup)
- Dedupe only considers rows with `S >= PQT`, same-folder buckets, lower score vs keeper
