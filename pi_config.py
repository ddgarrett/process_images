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
from pi_action import *
from pi_action_props import PiFileProperties
from pi_util import EventListener
from pi_filters import *

''' constants '''
VERSION = '0.2.0'
WINDOW_CONFIG = "__WINDOW CONFIG__"
BLOG_URI = 'https://www.garrettblog.com'

# image file types
IMG_FILE_TYPES = [".jpg",".jpeg",".png",".gif",".tiff",".tif"]

''' initialized here '''
metadata:CsvTable = CsvTable("image_collection_metadata.csv")

# print events as they are handled?
TRACE_EVENTS = True

# standard events
EVT_FILE_OPEN  = '-FILE_OPEN-'
EVT_FILE_NEW   = '-FILE_NEW-'
EVT_FILE_SAVE  = '-FILE_SAVE-'
EVT_ADD_FOLDERS  = '-ADD_FOLDERS-'
EVT_REORG_IMG  = '-REORG_IMG-'
EVT_FILE_PROPS = '-FILE_PROPS-'
EVT_EXIT       = '-EXIT-'
EVT_ABOUT      = '-ABOUT-'

EVT_SHOW_ALL           = '-SHOW_ALL-'
EVT_SHOW_TBD           = '-SHOW_TBD-'
EVT_SHOW_POSSIBLE_DUP  = '-SHOW_POSSIBLE_DUP-'
EVT_SHOW_POSSIBLE_GOOD_PLUS = '-SHOW_POSSIBLE_GOOD_PLUS-'
EVT_SHOW_POSSIBLE_BEST = '-SHOW_POSSIBLE_BEST-'
EVT_SHOW_CUSTOM        = '-SHOW_CUSTOM-'

EVT_NOT_IMPL       = '-NOT_IMPLEMENTED-'

EVT_TREE          = '-TREE-'
EVT_IMG_SELECT    = '-IMGSEL-'
EVT_TABLE_LOAD    = '-TABLE_LOAD-'
EVT_TABLE_ROW_CHG = '-ROW_CHG-'
EVT_WIN_CONFIG    = WINDOW_CONFIG

# EVT_ACT_MAP     = '-MAP-'

# standard image statuses
STAT_REJECT     = 'reject'
STAT_QUAL_BAD   = 'bad'
STAT_DUP        = 'dup'
STAT_OK         = 'ok'
STAT_GOOD       = 'good'
STAT_BEST       = 'best'
STAT_TBD        = 'tbd'

# standard review levels
LVL_INITIAL     = '0'
LVL_QUAL        = '1'
LVL_DUP         = '2'
LVL_OK          = '3'
LVL_GOOD        = '4'
LVL_BEST        = '5'

''' global Event Listner '''
listeners = EventListener()

''' standard global actions '''
PiOpenCollection(EVT_FILE_OPEN)
PiNewCollection(EVT_FILE_NEW)
PiAddFolders(EVT_ADD_FOLDERS)
PiSaveCollection(EVT_FILE_SAVE)
PiFileProperties(EVT_FILE_PROPS)
PiAboutApp(EVT_ABOUT)
PiNotImplemented(EVT_NOT_IMPL)

''' global filter table events '''
PiFilterTable(c.EVT_SHOW_ALL, None)
PiFilterTable(c.EVT_SHOW_TBD, FilterTbd())
PiFilterTable(c.EVT_SHOW_POSSIBLE_DUP, FilterPossibleDup())
PiFilterTable(c.EVT_SHOW_POSSIBLE_GOOD_PLUS, FilterPossibleGoodPlus())
PiFilterTable(c.EVT_SHOW_POSSIBLE_BEST, FilterPossibleBest())

''' set when collection is created or loaded '''
table:ImageCollection = ImageCollection('') # may be filtered
directory = ""  # current directory (should have this in the ImageCollection table?)

''' Application Functions '''
APP_ORG_IMG = "OI"  # runnning "organize images" function of app
APP_RVW_IMG = "RI"  # running "review images" function of app
app_function = APP_RVW_IMG  # default to Review Images

''' initialized in main() '''
window:sg.Window = None   # main window
status:sg.Element = None  # status display element

def update_status(msg):
    if status != None:
        status.update(msg)
