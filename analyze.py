import os
import datetime

''' This script analyzes disk usage for directories. It outputs a tab-delimited summary including:
- Directory name
- Size (human-readable)
- Number of files
- Number of child directories
- Oldest file modification date
- Newest file modification date

To run,use the command `python /home/dgarrett/Documents/projects/process_images/analyze.py` 
in the directory you want to analyze.
'''

def get_human_readable_size(size_bytes):
    """Converts bytes to a human-readable format."""
    if size_bytes == 0:
        return "0 B"
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_names[i]}"

def analyze_directory(path):
    """Analyzes a directory and returns its size, file count, child directory count, and date range."""
    total_size = 0
    file_count = 0
    child_dir_count = 0
    oldest_date = None
    newest_date = None

    for entry in os.scandir(path):
        if entry.is_file():
            file_count += 1
            total_size += entry.stat().st_size
            mod_time = datetime.datetime.fromtimestamp(entry.stat().st_mtime)
            if oldest_date is None or mod_time < oldest_date:
                oldest_date = mod_time
            if newest_date is None or mod_time > newest_date:
                newest_date = mod_time
        elif entry.is_dir():
            child_dir_count += 1
            # Recursively calculate size and dates for subdirectories (for total_size and dates)
            # This is a simplified approach, a full recursive scan would be more complex
            # For this problem, we only care about the *files* within the immediate subdirectory for size/dates
            # and the *count* of child directories.

    return total_size, file_count, child_dir_count, oldest_date, newest_date

def main():
    current_directory = os.getcwd()
    output_file = "summary.csv"

    with open(output_file, "w") as f:
        f.write("Directory\tSize\tFiles\tChild Dirs\tOldest Mod Date\tNewest Mod Date\n")

        for entry in os.scandir(current_directory):
            if entry.is_dir():
                dir_path = entry.path
                dir_name = entry.name

                total_size, file_count, child_dir_count, oldest_date, newest_date = analyze_directory(dir_path)

                human_readable_size = get_human_readable_size(total_size)
                oldest_date_str = oldest_date.strftime("%Y-%m-%d") if oldest_date else "N/A"
                newest_date_str = newest_date.strftime("%Y-%m-%d") if newest_date else "N/A"

                f.write(f"{dir_name}\t{human_readable_size}\t{file_count}\t{child_dir_count}\t{oldest_date_str}\t{newest_date_str}\n")

if __name__ == "__main__":
    main()