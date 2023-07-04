'''
    Select parent directory for a collection of images.
'''

import os
import pathlib

import exifread

import tkinter as tk
from tkinter import filedialog

from csv_table import CsvTable

image_sfx = [".jpg",".jpeg"]

cols = ["file_id","file_root","file_name","rvw_lvl","img_lon","img_lat","img_width","img_len","tags"]

lon_row_idx = cols.index("img_lon")
lat_row_idx = cols.index("img_lat")

# map exif_keys to csv_table column indexes
exif_keys = (
    ("Image ImageWidth",6),
    ("Image ImageLength",7) )

lon_key     = "GPS GPSLongitude"
lon_ref_key = "GPS GPSLongitudeRef"
lat_key     = "GPS GPSLatitude"
lat_ref_key = "GPS GPSLatitudeRef"

# print("dir:",dir)

# return latitude and longitude from exif data
# in decimal format
def conv_lat_lon(lat,lat_ref,lon,lon_ref)-> tuple[float,float]:
    lat_dec = lat[0] + lat[1]/60 + lat[2]/3600
    lon_dec = lon[0] + lon[1]/60 + lon[2]/3600

    if lat_ref == "S":
        lat_dec = -lat_dec
    elif lat_ref != "N":
        print("lat ref: ",lat_ref)
    
    if lon_ref == "W":
        lon_dec = -lon_dec
    elif lon_ref != "E":
        print("lon ref:",lon_ref)

    return round(float(lat_dec),6),round(float(lon_dec),6)

def select_dir(root:tk.Tk=None) -> str:
    '''
    Select a directory of images to use in creating a new collection.

    Returns the directory name as a string. 
    An empty directory name means no directory was chosen.
    '''
    passed_root = True
    if root == None:
        passed_root = False
        root = tk.Tk()
        # root.withdraw()

    d = filedialog.askdirectory(title="Select Image Directory")

    if not passed_root:
        root.destroy()

    return d

def set_image_data(file_path:str,row:list[any]):
    f = open(file_path, 'rb')
    tags = exifread.process_file(f, details=False)

    for ki in exif_keys:
        key = ki[0]
        if key in tags:
            idx = ki[1]
            row[idx] = tags[key]

    # convert and save latitude and longitude
    if lat_key in tags:
        lat     = tags[lat_key].values
        lat_ref = tags[lat_ref_key].values
        lon     = tags[lon_key].values
        lon_ref = tags[lon_ref_key].values

        lat,lon = conv_lat_lon(lat,lat_ref,lon,lon_ref)

        row[lat_row_idx] = lat
        row[lon_row_idx] = lon

        # print(lat,lon)

    f.close()

def load_dir(startpath:str) -> list[list[any]]:
    file_id:int = 1000
    rows = []
    for root, dirs, files in os.walk(startpath):
        subdir = root.replace(startpath, '')
        dir_path = pathlib.Path(root)
        # print(subdir)
        for fn in files:
            file_path = dir_path.joinpath(fn)
            sfx = file_path.suffix
            if sfx in image_sfx:
                file_id += 1
                row = [""]*len(cols)
                row[0] = file_id
                row[1] = subdir
                row[2] = fn
                row[3] = 0  # review count
                set_image_data(file_path,row)
                rows.append(row)

    return rows


if __name__ == "__main__":
    d:str = select_dir()
    if d == "":
        print("directory not selected")
        exit(0)

    metadata = CsvTable("image_collection_metadata.csv")
    
    os.chdir(d)
    print("dir",d)
    
    #### TODO: check if there is already a "image_collection.csv" file in the directory

    if os.path.isfile("image_collection.csv"):
        print("image_collection.csv already defined")
        print("to regenerate, delete file then rerun this process")
        exit(1)

    print("loading data for image files")
    rows = load_dir(d)

    print(f"creating table with {len(rows)} rows")
    t = CsvTable("image_collection.csv",columns=cols,rows=rows)

    print("saving table")
    t.save()


    