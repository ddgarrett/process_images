
import tkinter as tk
from tkinter import filedialog

def select_dir(root:tk.Tk=None) -> str:
    passed_root = True
    if root == None:
        passed_root = False
        root = tk.Tk()
        # root.withdraw()

    d = filedialog.askdirectory(title="Select Image Directory")

    if not passed_root:
        root.destroy()

    return d

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