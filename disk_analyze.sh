
# du command to output tab delimited directory structure with human readable directory size, 
# file counts and oldest and newest modified date of files in each directory. Show Dates in yyyy-mm-dd format

#!/bin/bash

# Directory to analyze (current directory if not specified)
TARGET_DIR="${1:-.}"

echo -e "Path\tSize\tFile Count\tOldest Modified Date\tNewest Modified Date"

find "$TARGET_DIR" -type d -print0 | while IFS= read -r -d $'\0' dir; do
    # Get human-readable size of the directory
    DIR_SIZE=$(du -sh "$dir" | awk '{print $1}')

    # Get file count
    FILE_COUNT=$(find "$dir" -maxdepth 1 -type f | wc -l)

    # Get oldest and newest modified dates
    OLD_NEW_DATES=$(find "$dir" -maxdepth 1 -type f -printf "%T@ %TY-%Tm-%Td\n" | sort -n | awk '
        NR==1 {oldest_date=$2}
        END {
            if (NR > 0) {
                newest_date=$2;
                print oldest_date "\t" newest_date;
            } else {
                print "N/A\tN/A";
            }
        }
    ')

    # Print the tab-delimited output
    echo -e "${dir}\t${DIR_SIZE}\t${FILE_COUNT}\t${OLD_NEW_DATES}"
done