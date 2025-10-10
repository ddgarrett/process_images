
# du command to output tab delimited directory structure with human readable directory size, file counts and oldest and newest modified date of files in each directory. Show Dates in yyyy-mm-dd format. Only report on directories one level deep but count children directories for those directories.
# command is /home/dgarrett/Documents/projects/process_images/disk_analyze.sh

#!/bin/bash

# Loop through each top-level directory (one level deep)
for dir in */; do
    # Remove trailing slash for cleaner output
    dir_name="${dir%/}"

    # Get human-readable size of the directory
    size=$(du -sh "$dir_name" | awk '{print $1}')

    # Count files and subdirectories within the current directory (including children directories)
    file_count=$(find "$dir_name" -type f | wc -l)
    subdir_count=$(find "$dir_name" -mindepth 1 -maxdepth 1 -type d | wc -l)

    # Find the oldest and newest modified dates of files within the directory
    oldest_date=$(find "$dir_name" -type f -printf '%T@\t%TY-%Tm-%Td\n' | sort -n | head -n 1 | cut -f2)
    newest_date=$(find "$dir_name" -type f -printf '%T@\t%TY-%Tm-%Td\n' | sort -nr | head -n 1 | cut -f2)

    # Handle cases where no files are found in a directory
    if [ -z "$oldest_date" ]; then
        oldest_date="N/A"
    fi
    if [ -z "$newest_date" ]; then
        newest_date="N/A"
    fi

    # Print the tab-delimited output
    echo -e "$dir_name\t$size\t$file_count\t$subdir_count\t$oldest_date\t$newest_date"
done