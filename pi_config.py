'''
    Application wide singleton with global shared variables and constants.

    Exmaple use:
        import pi_config as c
        c.window['-STATUS-'].update(f'{len(c.table)} rows in table')
'''

import PySimpleGUI as sg

from csv_table import CsvTable
from image_collection import ImageCollection

''' constants '''
VERSION = '0.1.0'
WINDOW_CONFIG = "__WINDOW CONFIG__"

''' initialized here '''
metadata:CsvTable = CsvTable("image_collection_metadata.csv")

''' event callbacks '''
event_cb:dict[any:any] = []

''' set when collection is created or loaded '''
table:ImageCollection = ImageCollection('') # may be filtered
otable:ImageCollection = table  # original table - unfiltered
directory = ""

''' initialized in main() '''
window:sg.Window = None   # main window
status:sg.Element = None  # status display element



