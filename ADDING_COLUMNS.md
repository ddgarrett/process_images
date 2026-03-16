# Adding a Column to image_collection.csv

The columns for `image_collection.csv` are defined in **`image_collection_metadata.csv`**. The program uses that file when creating new collections (File → New), when adding folders to an existing collection (Add Folders), and when opening an existing CSV (any columns in the metadata that are missing from the file are added with the default value).

## 1. Add a row in image_collection_metadata.csv

Each column is one row in the metadata file. The header row defines these fields:

| Field        | Meaning |
|-------------|---------|
| **col_name**  | Column name (no spaces; use underscore). |
| **col_type**  | `int`, `float`, `str`, or `any`. |
| **default**   | Value when no EXIF/source is used (e.g. `0`, `na`, ` `, or leave empty). |
| **load_func** | How to fill from EXIF: `get_key`, `get_lat_lon`, `get_key_value`, or leave empty to use **default** only. |
| **exif_tags** | EXIF tag name(s) for that loader (e.g. `Image Make` or a JSON array of alternatives). Leave empty if you only use **default**. |
| **notes**     | Optional description. |

### Examples

- **Column you fill in later** (like `notes` or `img_tags`): leave `load_func` and `exif_tags` empty; set `default` as needed (e.g. a space or blank).

- **Column from a single EXIF tag:** set `load_func` = `get_key` and `exif_tags` = the tag name (e.g. `EXIF ExposureTime`).

- **Column from one of several possible EXIF tags:** set `load_func` = `get_key` and `exif_tags` = a JSON array, e.g. `["EXIF DateTimeOriginal","Image DateTime"]`.

## 2. No code changes required

The table and EXIF loader are metadata-driven. Once the new column is in `image_collection_metadata.csv`, it will appear in new and existing collections. If you want the column to appear in a specific part of the UI (e.g. gallery, tree, or an export), you may need to add code there; for “just another column in the CSV,” the metadata change is enough.
