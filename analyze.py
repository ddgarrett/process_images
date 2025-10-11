

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

''' Google Search: 
    generate a python program to output tab delimited directory structure with human readable directory size, 
    file counts and oldest and newest modified date of files in each directory. 
    Only include files which are images and videos. 
    Show Dates in yyyy-mm-dd format. 
    Only report on directories one level deep but count children directories for those directories. 
    Sort results by oldest file date. Save the result in a file named summary.csv
'''

import os
import csv
from datetime import datetime

def convert_size(size_bytes):
    """
    Converts a size in bytes to a more human-readable format.
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f}{size_name[i]}"

def analyze_directory(base_path):
    """
    Analyzes directories one level deep from the base_path for image and video files.
    """
    allowed_extensions = (
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.heif', '.heic',
        '.mp4', '.mov', '.mkv', '.avi', '.wmv', '.flv', '.webm'
    )
    
    report_data = []
    
    # Iterate over all items in the base directory
    with os.scandir(base_path) as entries:
        for entry in entries:
            if entry.is_dir():
                dir_path = entry.path
                total_size = 0
                file_count = 0
                oldest_date = None
                newest_date = None
                child_dirs_count = 0

                # Walk the subdirectory to find image and video files
                for root, dirs, files in os.walk(dir_path):
                    child_dirs_count += len(dirs)
                    for file_name in files:
                        if file_name.lower().endswith(allowed_extensions):
                            file_path = os.path.join(root, file_name)
                            try:
                                stats = os.stat(file_path)
                                total_size += stats.st_size
                                file_count += 1
                                mod_date = datetime.fromtimestamp(stats.st_mtime)

                                if oldest_date is None or mod_date < oldest_date:
                                    oldest_date = mod_date
                                if newest_date is None or mod_date > newest_date:
                                    newest_date = mod_date
                            except (OSError, FileNotFoundError):
                                continue # Skip files with permission errors or broken links

                # Only include the directory if it contains relevant files
                if file_count > 0:
                    report_data.append({
                        'directory_name': entry.name,
                        'total_size': convert_size(total_size),
                        'file_count': file_count,
                        'child_directories': child_dirs_count,
                        'oldest_file': oldest_date.strftime('%Y-%m-%d') if oldest_date else 'N/A',
                        'newest_file': newest_date.strftime('%Y-%m-%d') if newest_date else 'N/A',
                        'sort_key': oldest_date # For sorting purposes
                    })

    # Sort the data by the oldest file date, ascending
    report_data.sort(key=lambda x: x['sort_key'] if x['sort_key'] else datetime.min)
    
    return report_data

def save_to_csv(data, filename='summary.csv'):
    """
    Saves the analyzed data to a tab-delimited CSV file.
    """
    if not data:
        print("No image or video files found in the specified directories.")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'Directory Name', 'Total Size', 'File Count', 
            'Child Directories', 'Oldest File Date', 'Newest File Date'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        
        writer.writeheader()
        for row in data:
            del row['sort_key'] # Remove the temporary sort key
            writer.writerow({
                'Directory Name': row['directory_name'],
                'Total Size': row['total_size'],
                'File Count': row['file_count'],
                'Child Directories': row['child_directories'],
                'Oldest File Date': row['oldest_file'],
                'Newest File Date': row['newest_file']
            })

    print(f"Summary saved to {filename}")

if __name__ == "__main__":
    # Specify the directory you want to analyze
    # This example uses the current working directory.
    # To analyze a different path, replace '.' with your desired path (e.g., r'C:\Photos').
    path_to_analyze = '.' 
    
    summary = analyze_directory(path_to_analyze)
    save_to_csv(summary)

