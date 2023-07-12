'''
    Application wide singleton with global shared variables and constants.

    Exmaple use:
        import pi_config as c
        c.window['-STATUS-'].update(f'{len(c.table)} rows in table')
'''
from __future__ import annotations

import PySimpleGUI as sg

from csv_table import CsvTable
from image_collection import ImageCollection
from pi_util import EventListener

''' constants '''
VERSION = '0.1.0'
WINDOW_CONFIG = "__WINDOW CONFIG__"
# image file types
IMG_FILE_TYPES = [".jpg",".jpeg",".png",".gif",".tiff"]

''' initialized here '''
metadata:CsvTable = CsvTable("image_collection_metadata.csv")

# standard events
EVT__FILE_OPEN  = '-FILE_OPEN-'
EVT_FILE_NEW    = '-FILE_NEW-'
EVT_FILE_SAVE   = '-FILE_SAVE-'
EVT_FILE_PROPS  = '-FILE_PROPS-'
EVT_EXIT        = '-EXIT-'
EVT_ABOUT       = '-ABOUT-'

EVT_TREE        = '-TREE-'
EVT_TABLE_LOAD  = '-TABLE_LOAD-'
EVT_WIN_CONFIG  = WINDOW_CONFIG

EVT_ACT_MAP     = '-MAP-'

''' global Event Listner '''
listeners = EventListener()

''' set when collection is created or loaded '''
table:ImageCollection = ImageCollection('') # may be filtered
directory = ""  # current directory (should have this in the ImageCollection table?)

''' initialized in main() '''
window:sg.Window = None   # main window
status:sg.Element = None  # status display element


