import argparse
import csv
import hashlib
import os
import sys
from datetime import date, datetime
from pathlib import Path

MEDIA_CSV_HEADERS = [
    "Directory Name",
    "Full Path",
    "File Count",
    "Total Size (MB)",
    "Directory Hash",
    "dup_cnt",
    "run_date",
]

PARMS_CSV_HEADERS = [
    "Path",
    "run_date",
    "run_time",
]

PARMS_FILENAME = "reconcile_media_parms.csv"


def norm_path(p):
    return os.path.normpath(os.path.abspath(p))


def path_is_under(child_path, parent_path):
    c = norm_path(child_path)
    p = norm_path(parent_path)
    if c == p:
        return True
    return c.startswith(p + os.sep)


def row_matches_any_scan_root(full_path, scan_roots_norm):
    return any(path_is_under(full_path, r) for r in scan_roots_norm)


def get_file_hash(filepath, block_size=65536, sample_size=3 * 1024 * 1024):
    """
    Generates a hash. For large videos, it only hashes the first 'sample_size'
    to significantly increase performance.
    """
    hasher = hashlib.md5()
    video_extensions = {".mp4", ".mov", ".avi", ".mkv"}

    try:
        file_extension = Path(filepath).suffix.lower()
        file_size = os.path.getsize(filepath)

        with open(filepath, "rb") as f:
            # Large videos: hash only the first sample_size bytes
            if file_extension in video_extensions and file_size > sample_size:
                buf = f.read(sample_size)
                hasher.update(buf)
            else:
                buf = f.read(block_size)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(block_size)

        return hasher.hexdigest()
    except (PermissionError, OSError):
        return None


def _validate_csv_headers(path, reader_fieldnames, expected):
    if reader_fieldnames is None:
        sys.exit(
            f"Error: '{path}' has no header row or could not be read. "
            "Fix or remove the file; no data was written."
        )
    if list(reader_fieldnames) != expected:
        sys.exit(
            f"Error: '{path}' headers do not match the expected layout. "
            f"Expected {expected}, got {list(reader_fieldnames)}. "
            "No data was written."
        )


def load_existing_media_rows(output_csv):
    if not os.path.isfile(output_csv):
        return []
    with open(output_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _validate_csv_headers(output_csv, reader.fieldnames, MEDIA_CSV_HEADERS)
        return list(reader)


def load_existing_parm_rows(parms_csv):
    if not os.path.isfile(parms_csv):
        return []
    with open(parms_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _validate_csv_headers(parms_csv, reader.fieldnames, PARMS_CSV_HEADERS)
        return list(reader)


def scan_media_directories(source_directories, run_date_str):
    """Walk scan roots and return new media rows (dicts without dup_cnt set)."""
    valid_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".heic",
    }
    rows = []
    processed_count = 0

    for root_path in source_directories:
        if not os.path.exists(root_path):
            print(f"Warning: Path does not exist -> {root_path}")
            continue

        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if not d.startswith(("_", "."))]
            if os.path.basename(root).startswith(("_", ".")):
                dirs.clear()
                continue

            media_files = [
                f
                for f in files
                if Path(f).suffix.lower() in valid_extensions
                and "map" not in f.lower()
                and not f.startswith(("_", "."))
            ]

            if not media_files:
                continue

            file_hashes = []
            total_size = 0

            for filename in sorted(media_files):
                filepath = os.path.join(root, filename)
                if os.path.islink(filepath):
                    continue
                f_hash = get_file_hash(filepath)
                if f_hash:
                    file_hashes.append(f_hash)
                    total_size += os.path.getsize(filepath)

            combined_hash = hashlib.md5("".join(file_hashes).encode()).hexdigest()
            size_mb = round(total_size / (1024 * 1024), 2)

            rows.append(
                {
                    "Directory Name": os.path.basename(root),
                    "Full Path": root,
                    "File Count": str(len(media_files)),
                    "Total Size (MB)": str(size_mb),
                    "Directory Hash": combined_hash,
                    "run_date": run_date_str,
                }
            )
            processed_count += 1
            print(f"Analyzed: {root}")

    return rows, processed_count


def recompute_dup_cnt(rows):
    """Set dup_cnt on each row dict from Directory Hash counts (count - 1)."""
    counts = {}
    for r in rows:
        h = r["Directory Hash"]
        counts[h] = counts.get(h, 0) + 1
    for r in rows:
        r["dup_cnt"] = str(counts[r["Directory Hash"]] - 1)


def write_media_csv(output_csv, rows):
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=MEDIA_CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def write_parms_csv(parms_csv, rows):
    with open(parms_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=PARMS_CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def merge_parm_rows(existing_rows, scan_paths_norm, run_date_str, run_time_str):
    scan_set = set(scan_paths_norm)
    kept = [
        r
        for r in existing_rows
        if norm_path(r["Path"]) not in scan_set
    ]
    new_rows = [
        {
            "Path": p,
            "run_date": run_date_str,
            "run_time": run_time_str,
        }
        for p in scan_paths_norm
    ]
    return kept + new_rows


def reconcile_media(source_directories, output_csv):
    """Crawls directories and generates a CSV report with directory fingerprints."""
    run_date_str = date.today().isoformat()
    run_time_str = datetime.now().strftime("%H:%M")

    output_csv = os.path.abspath(os.path.normpath(output_csv))
    parms_csv = str(Path(output_csv).parent / PARMS_FILENAME)

    scan_roots_norm = []
    seen_scan = set()
    for p in source_directories:
        n = norm_path(p)
        if n not in seen_scan:
            seen_scan.add(n)
            scan_roots_norm.append(n)

    print("--- Starting Reconciliation ---")

    kept_media = []
    if os.path.isfile(output_csv):
        all_existing = load_existing_media_rows(output_csv)
        kept_media = [
            r
            for r in all_existing
            if not row_matches_any_scan_root(r["Full Path"], scan_roots_norm)
        ]

    parm_existing = []
    if os.path.isfile(parms_csv):
        parm_existing = load_existing_parm_rows(parms_csv)

    new_media, processed_count = scan_media_directories(
        source_directories,
        run_date_str,
    )

    merged_media = kept_media + new_media
    recompute_dup_cnt(merged_media)
    write_media_csv(output_csv, merged_media)

    merged_parms = merge_parm_rows(
        parm_existing,
        scan_roots_norm,
        run_date_str,
        run_time_str,
    )
    write_parms_csv(parms_csv, merged_parms)

    hash_tracker = {}
    for r in merged_media:
        h = r["Directory Hash"]
        hash_tracker[h] = hash_tracker.get(h, 0) + 1
    duplicate_sets = [h for h, count in hash_tracker.items() if count > 1]

    print("\n--- Process Complete ---")
    print(f"Directories analyzed this run: {processed_count}")
    print(f"Total rows in report: {len(merged_media)}")
    print(f"Identical directory sets found: {len(duplicate_sets)}")
    print(f"Report saved to: {output_csv}")
    print(f"Parameters log saved to: {parms_csv}")


def main():
    parser = argparse.ArgumentParser(
        description="Reconcile media files across multiple drives."
    )

    parser.add_argument(
        "--paths", nargs="+", required=True, help="One or more directory paths to scan."
    )

    parser.add_argument(
        "--output",
        default="reconciliation_report.csv",
        help="The name of the CSV file to generate (default: reconciliation_report.csv)",
    )

    args = parser.parse_args()

    reconcile_media(args.paths, args.output)


if __name__ == "__main__":
    main()

# python reconcile_media.py --paths /path/one /path/two --output reconcile_media.csv
