## End-to-End Status Logic (Landscape Print)

| Dedup inputs | CSV status | Collection (`img_status`,`rvw_lvl`) | Display |
|---|---|---|---|
| `S < PQT` | `poor quality` | `bad`, `"1"` | `bad` |
| `S >= PQT` and duplicate (`sim >= MST` to higher-scored keeper, same folder, GPS gate if enabled) | `dup` | `dup`, `"2"` | `dup` |
| Not duplicate and `S > 6` | `best` | `best`, `"5"` | `best` |
| Not duplicate and `5 < S <= 6` | `good` | `tbd`, `"4"` | `tbd, Best?` |
| Not duplicate and `S <= 5` | `TBD` | `tbd`, `"3"` | `tbd, Good?` |
| Unknown or empty status fallback | unknown or empty | `tbd`, `"0"` | `tbd, Reject?` |

### Legend

- `S` = `musiq_score`
- `PQT` = poor quality threshold (default `4.0`)
- `MST` = cosine similarity duplicate threshold (default `0.65`)
- Duplicate checks run only on rows with `S >= PQT`, in same-folder buckets, and against lower-priority rows in score order.
