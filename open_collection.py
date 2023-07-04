'''
    Open CSV that defines a collection of images.
'''

import os

import tkinter as tk
from tkinter import filedialog

from csv_table import CsvTable

import new_collection
# cols = ["file_id","file_root","file_name","rvw_lvl","img_lon","img_lon_ref","img_lat","img_lat_ref","img_width","img_len","tags"]
cols = new_collection.cols

def select_collection(root:tk.Tk=None):
    passed_root = True
    if root == None:
        passed_root = False
        root = tk.Tk()
        # root.withdraw()

    d = filedialog.askopenfilename(
        title="Select Collections CSV File",
        filetypes=[('Collection Files', "image_collection.csv")])

    if not passed_root:
        root.destroy()

    return d

def get_collection_table() -> CsvTable:
    d = select_collection()
    if d == "":
        print("image collection csv not selected")
        exit(0)

    dirname = os.path.dirname(d)
    os.chdir(dirname)

    print("loading image collection csv:",d)
    t = CsvTable(d)

    if t[t.COL_NAMES] != cols:
        print(f"unrecognized csv column names: \n{t[t.COL_NAMES]} vs\n{cols}")
        exit(1)

    return t

if __name__ == "__main__":
    t = get_collection_table()

    print(f'Rows in table: {len(t)}')
    print(f'first row: {t._rows[0]._data}')
