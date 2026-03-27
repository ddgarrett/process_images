import argparse
import csv
import hashlib
import os
from pathlib import Path


def get_file_hash(filepath, block_size=65536):
    """Generates a hash for an individual file using MD5."""
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            buf = f.read(block_size)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(block_size)
        return hasher.hexdigest()
    except (PermissionError, OSError):
        return None


def reconcile_media(source_directories, output_csv):
    """Crawls directories and generates a CSV report with directory fingerprints."""
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
    headers = [
        "Directory Name",
        "Full Path",
        "File Count",
        "Total Size (MB)",
        "Directory Hash",
    ]

    hash_tracker = {}  # Used to count duplicates for the final summary
    processed_count = 0

    print("--- Starting Reconciliation ---")

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for root_path in source_directories:
            if not os.path.exists(root_path):
                print(f"Warning: Path does not exist -> {root_path}")
                continue

            for root, dirs, files in os.walk(root_path):
                # Filter: Media extensions + exclude filenames containing "map"
                media_files = [
                    f
                    for f in files
                    if Path(f).suffix.lower() in valid_extensions
                    and "map" not in f.lower()
                ]

                if not media_files:
                    continue

                file_hashes = []
                total_size = 0

                # Sort ensures consistent hashing regardless of OS file ordering
                for filename in sorted(media_files):
                    filepath = os.path.join(root, filename)
                    f_hash = get_file_hash(filepath)
                    if f_hash:
                        file_hashes.append(f_hash)
                        total_size += os.path.getsize(filepath)

                # Create the Directory Fingerprint
                combined_hash = hashlib.md5("".join(file_hashes).encode()).hexdigest()
                size_mb = round(total_size / (1024 * 1024), 2)

                writer.writerow(
                    [
                        os.path.basename(root),
                        root,
                        len(media_files),
                        size_mb,
                        combined_hash,
                    ]
                )

                # Track hashes to identify duplicates later
                hash_tracker[combined_hash] = hash_tracker.get(combined_hash, 0) + 1
                processed_count += 1
                print(f"Analyzed: {root}")

    # Final Summary Logic
    duplicate_sets = [h for h, count in hash_tracker.items() if count > 1]

    print("\n--- Process Complete ---")
    print(f"Total directories scanned: {processed_count}")
    print(f"Identical directory sets found: {len(duplicate_sets)}")
    print(f"Report saved to: {output_csv}")


def main():
    parser = argparse.ArgumentParser(
        description="Reconcile media files across multiple drives."
    )

    # Allows passing multiple paths: --paths /drive1/photos /drive2/backups
    parser.add_argument(
        "--paths", nargs="+", required=True, help="One or more directory paths to scan."
    )

    # Allows customizing the output filename
    parser.add_argument(
        "--output",
        default="reconciliation_report.csv",
        help="The name of the CSV file to generate (default: reconciliation_report.csv)",
    )

    args = parser.parse_args()

    reconcile_media(args.paths, args.output)


if __name__ == "__main__":
    main()

""" 
    examples: 

    python reconcile_media.py --paths /Users/douglasgarrett/Documents/pictures /Volumes/T7 --output reconcile_media.csv
"""
