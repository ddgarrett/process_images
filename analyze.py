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
import os
import datetime

def human_readable_size(size_bytes):
    """Converts bytes to a human-readable format."""
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f}{size_names[i]}"

def get_directory_summary(root_dir):
    """
    Generates a summary for directories one level deep within the root_dir.
    Includes size, file count, child directory count, and date range.
    """
    results = []
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            dir_path = entry.path
            total_size = 0
            file_count = 0
            child_dir_count = 0
            oldest_date = None
            newest_date = None

            for sub_entry in os.walk(dir_path):
                current_dir = sub_entry[0]
                files = sub_entry[2]
                dirs = sub_entry[1]

                if current_dir == dir_path:  # Only count direct children for child_dir_count
                    child_dir_count = len(dirs)

                for file_name in files:
                    file_path = os.path.join(current_dir, file_name)
                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        file_count += 1
                        mod_time = os.path.getmtime(file_path)
                        mod_date = datetime.datetime.fromtimestamp(mod_time).date()

                        if oldest_date is None or mod_date < oldest_date:
                            oldest_date = mod_date
                        if newest_date is None or mod_date > newest_date:
                            newest_date = mod_date
                    except OSError:
                        # Handle cases where file might be inaccessible or deleted
                        pass

            oldest_date_str = oldest_date.strftime("%Y-%m-%d") if oldest_date else "N/A"
            newest_date_str = newest_date.strftime("%Y-%m-%d") if newest_date else "N/A"

            results.append({
                "directory": entry.name,
                "size": human_readable_size(total_size),
                "file_count": file_count,
                "child_dir_count": child_dir_count,
                "oldest_file_date": oldest_date_str,
                "newest_file_date": newest_date_str,
                "sort_key_oldest_date": oldest_date # For sorting
            })

    # Sort results by oldest file date
    results.sort(key=lambda x: x["sort_key_oldest_date"] if x["sort_key_oldest_date"] else datetime.date.min)

    return results

def save_summary_to_file(summary_data, output_file="summary.csv"):
    """Saves the summary data to a tab-delimited file."""
    with open(output_file, "w") as f:
        # Write header
        f.write("Directory\tSize\tFile Count\tChild Dir Count\tOldest File Date\tNewest File Date\n")
        # Write data
        for item in summary_data:
            f.write(f"{item['directory']}\t{item['size']}\t{item['file_count']}\t"
                    f"{item['child_dir_count']}\t{item['oldest_file_date']}\t"
                    f"{item['newest_file_date']}\n")

if __name__ == "__main__":
    target_directory = "."  # Current directory, change as needed
    summary = get_directory_summary(target_directory)
    save_summary_to_file(summary)
    print(f"Directory summary saved to summary.csv in {os.getcwd()}")
