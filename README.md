## Process Images

## Running on macOS

This app uses FreeSimpleGUI (tkinter). On macOS you need **Python with Tcl/Tk 8.6 or newer**. The system Python (`/usr/bin/python3`) ships with old Tcl/Tk 8.5, which can cause a PNG warning, a "macOS 26 (2603) or later required" message, and `zsh: abort`.

**Recommended: use Homebrew's Python 3.12** (includes Tcl/Tk 8.6 or 9.x):

```bash
brew install python@3.12
```

Homebrew does not add a `python3` symlink for this version; use the versioned executable. On Apple Silicon the path is `/opt/homebrew/opt/python@3.12/bin/python3.12`. Create and use a venv:

```bash
rm -rf .venv
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

On Intel Macs, use `brew --prefix python@3.12` to get the path (often `/usr/local`). **Alternative:** Install Python 3.10+ from [python.org/downloads](https://www.python.org/downloads/); the official installers bundle Tcl/Tk 8.6.

The project pins `urllib3` to 1.x so it works with macOS’s LibreSSL Save `requirements.txt` as **UTF-8**; if it is saved as UTF-16, `pip install -r requirements.txt` will fail.

## Adding columns to the image collection

To add a column to the `image_collection.csv` file that the program creates and opens, edit **`image_collection_metadata.csv`**. See [ADDING_COLUMNS.md](ADDING_COLUMNS.md) for step-by-step instructions.

---

Review your photos to select only the best for inclusion in Google Albums and Blogger.com posts. Advanced features generate skeleton HTML for Blogger.com entries. If your pictures have GPS data embedded, you can even generate HTML pages to display Google Maps with pins that link to your Blogger.com entries.


## Overview


It's fun to take a lot of pictures during trips, family gatherings, or just daily outings. The difficult part is when you return home and want to sort through those pictures to find the best of potentially thousands of pictures. Process Images (PI) supports an iterative process to easily review your pictures to winnow out the poor, the duplicates and the "just okay" pictures, and help you identify the very best of your thousands of pictures. Those are the pictures you'd want to keep in something like a Google Photo Album so you could later relive your trip or share the pictures with friends and family. Without boring them to death.


Personally, I keep all of my photos backed up on external hard drives and rarely delete any pictures. I  use PI to review all of my pictures from a trip and select the top 10%. I then take the top 10% or so of those, the top 1% of all of my trip photos, and put them in a Google Photo Album that shows the best on <a href="https://www.garrettblog.com" target="_blank">my blogger.com website,</a> sometimes along with a description of what was happening that day.


If your photo review process is similar to mine you can use Process Images (PI) to quickly review your pictures and weed out those which are obviously not going to be in your final albums. This would include pictures you took of menus or signs to share with others, accidental shots or those which are grossly out of focus or otherwise flawed.


Next you can use PI to filter out those previously rejected pictures and do a second review to weed out those which are maybe just "so-so" or those where you wanted to see how the photo would turn out, and it just didn't work as you wanted. Maybe the picture is just "ok" but not really good enough to show others.


If you're anything like me, you tend to take a number of pictures of the same thing to see which turn out best. Or a number of pictures say of the inside of a church or another tourist attraction, but you just want to keep a few of the best. PI allows you to see a gallery of multiple pictures where you can select just one or a few of them for inclusion in a final album, marking the others as "duplicate".


With PI you can then filter your list of pictures to see just those which have survived the previous reviews and are potential winning pictures. Here you might have some which are good, but just not good enough. Or maybe you just don't want to bore others with too many pictures.


Or maybe there was a sight you did want to show others, even if the picture wasn't the best? PI makes it easy to "unfilter" the list of pictures and show previously rejected photos, giving you a second chance to review those pictures you might want to include in your final selection. For me, knowing that I can at a moment's notice go back for a second look at a previously rejected picture, makes it much easier for me to reject a photo in the first place.


By this point, if you've taken thousands of pictures like I do, you've narrowed it down to just your best 10% or maybe even less. These are the ones you'd want to upload to Google Photo Albums to create an organized set of lasting memories. Memories that you'd be proud to show others as well as fond of enough to review for yourself from time to time. This is where you can use PI to filter to show just your good photos and then export them to another folder. From those folders you can then drag and drop them into the Google Photo Albums that you create.


If you use blogger.com, like I do, you can take it one step further and do a final review to select your very best photos, those which you want to upload and write about on blogger.com. PI allows you to do this final review by filtering for just the "good" or better pictures and selecting the "best" pictures from those. You can then have the PI program filter to show just the "best" photos and export those to create folders of pictures you want to upload to blogger.com. While your photos are filtered to show just the "best" pictures you can use PI to generate skeleton HTML you can copy and paste into a blogger.com entry. The skeleton HTML will include HTML comments of where to upload and insert pictures into your blog entry, where you can add optional text comments to describe the pictures, and where you can add links to the Google Photo Albums so your blog readers can see the entire album for a day if they, and you, so wish.


Taking it one step further, if you've used a smartphone or some other GPS enabled camera to take your photos, you can now create a map based on where those "best" pictures you blogged about were taken. The map will contain a pin for every photo in your "best" category with links to anchors in the blogger.com posts previously created. The description for the pin will be the caption you entered for the picture when you created the blog entry. You can then upload that map HTML to a free github website and allow friends to view the map via a blogger.com post.


You can see examples of all of this on my blogger.com website. There is even a blog post with <a href="https://www.garrettblog.com/2023/05/back-home-from-japan.html">a link to an example map.</a> If you follow that link you'll seen a screen shot of a map. If you click on that screen shot it will take you to <a href="https://ddgarrett.github.io/2023-04_japan_trip.html">the map itself.</a> You can even see the source for that map on <a href="https://github.com/ddgarrett/ddgarrett.github.io">my GitHub repository</a>. HTML uploaded to the GitHub repo named 'ddgarrett.github.io' will be served up on the URL 'ddgarrett.github.io'.


The best part of all of this is, the Google Photo Albums, the blogger.com web page, the GitHub website and the Google Maps API are all free! Assuming you stay below certain limits of course.

## Using MUSIQ scores and duplicates from `backup_pics`

The `backup_pics` project and this app share a common image analysis library, `image_analysis_lib`,
which provides:

- MUSIQ image-quality scoring.
- Scene duplicate detection (CNN encodings + optional GPS radius).

### Typical Pi + Mac workflow

1. **On Raspberry Pi 5 (using `backup_pics`)**
   - Run `backup_pics` to copy images from phone/SD card into dated backup folders on the Pi SSD.
   - In a terminal on the Pi, run MUSIQ scoring on one or more day folders, for example:

     ```bash
     image-analysis score /home/dgarrett/Documents/pictures/MEDIA_BACKUP/yyyy-mm-dd_backup \
       --max-size 1024 0 \
       --output-prefix image_evaluation_musiq_results
     ```

   - Optionally run scene duplicate detection on an individual day folder:

     ```bash
     image-analysis dedupe /home/dgarrett/Documents/pictures/MEDIA_BACKUP/yyyy-mm-dd_backup \
       --musiq-csv-size 1024 \
       --threshold 0.65 \
       --gps-radius-meters 200
     ```

   - These commands write:
     - `image_evaluation_musiq_results_1024.csv` (and/or `_full.csv`) with MUSIQ scores.
     - `scene_duplicates_report.json` with keeper/duplicate mappings.
     - `image_scores_and_status.csv` with MUSIQ scores, EXIF extras, and initial status/duplicate labels.
     - `_by_status/` folders grouping images by `best`, `good`, `dup`, `poor quality`, etc.

2. **On MacBook Air (or the same Pi)**
   - Mount or copy the same `MEDIA_BACKUP/yyyy-mm-dd_backup` folders.
   - If desired, re-run scoring or deduplication with different thresholds for experimentation:

     ```bash
     image-analysis score /Volumes/PI_BACKUP/yyyy-mm-dd_backup --max-size 1024
     image-analysis dedupe /Volumes/PI_BACKUP/yyyy-mm-dd_backup --threshold 0.6
     ```

   - This keeps CSV formats stable so they continue to work with this app.

3. **In Process Images**
   - Start the app (on Pi or Mac) and create or open a collection that points at the same day folders.
   - When the collection is built/updated:
     - The MUSIQ score from the CSV is loaded into the `musiq_score` column.
     - Any status/duplicate information from `image_scores_and_status.csv` is available to guide your review.
   - Use the existing filters and menus:
     - Filter by status (`tbd`, `reject`, `bad`, `dup`, `ok`, `good`, `best`).
     - Use the Duplicate Review level and the “possible duplicate” filters to quickly review auto-flagged duplicates.
     - Use `TBD Best + Best` to focus on final-best candidates (`rvw_lvl='4' and status='tbd'`) plus already selected Best (`rvw_lvl='5' and status='best'`).
     - Use `Best` to show only rows already selected as Best (`rvw_lvl='5' and status='best'`).

Because the analysis happens in a shared library, you can:

- Run initial heavy work on the Raspberry Pi 5 (close to where images are ingested).
- Re-run or tweak thresholds later on a faster MacBook Air without changing this GUI.
- Keep `backup_pics` and `process_images` in sync via the same CSV and folder layouts.

## Review

Below is the process I've used for reviewing my photos using the Process Image (PI) project. 

### Grouping Pictures by Day

To be continued...


### Selecting Images to Process

To Be continued...


