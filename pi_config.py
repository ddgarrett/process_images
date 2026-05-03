'''
    Application wide singleton with global shared variables and constants.

    Exmaple use:
        import pi_config as c
        c.window['-STATUS-'].update(f'{len(c.table)} rows in table')
'''
from __future__ import annotations

import FreeSimpleGUI as sg

from csv_table import CsvTable
from image_collection import ImageCollection
from pi_action import *
from pi_action_cleanup_dir import PiCleanupDir
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
EVT_FILE_OPEN_FOLDER = '-FILE_OPEN_FOLDER-'
EVT_FILE_OPEN_CSV = '-FILE_OPEN_CSV-'
EVT_FILE_NEW   = '-FILE_NEW-'
EVT_FILE_SAVE  = '-FILE_SAVE-'
EVT_ADD_FOLDERS  = '-ADD_FOLDERS-'
EVT_CLEANUP_DIR  = '-REORG_IMG-'
EVT_FILE_PROPS = '-FILE_PROPS-'
EVT_EXIT       = '-EXIT-'
EVT_ABOUT      = '-ABOUT-'
EVT_TEST_CODE  = '-TEST_CODE-'

EVT_SHOW_ALL           = '-SHOW_ALL-'
EVT_SHOW_TBD           = '-SHOW_TBD-'
EVT_SHOW_POSSIBLE_DUP  = '-SHOW_POSSIBLE_DUP-'
EVT_SHOW_POSSIBLE_GOOD_PLUS = '-SHOW_POSSIBLE_GOOD_PLUS-'
EVT_SHOW_POSSIBLE_BEST = '-SHOW_POSSIBLE_BEST-'
EVT_SHOW_TBD_BEST_PLUS_BEST = '-SHOW_TBD_BEST_PLUS_BEST-'
EVT_SHOW_FINAL_BEST    = '-SHOW_FINAL_BEST-'
EVT_SHOW_CUSTOM        = '-SHOW_CUSTOM-'

EVT_NOT_IMPL       = '-NOT_IMPLEMENTED-'

EVT_TREE          = '-TREE-'
EVT_IMG_SELECT    = '-IMGSEL-'
EVT_DUP_IMG_SELECT = '-DUP_IMGSEL-'
EVT_TABLE_LOAD    = '-TABLE_LOAD-'
EVT_TABLE_ROW_CHG = '-ROW_CHG-'
EVT_WIN_CONFIG    = WINDOW_CONFIG
EVT_TREE_SCORE    = '-TREE_SCORE-'

# Canonical "Set status" menu events (single global handlers; row source from status_menu_rowgetter).
EVT_STATUS_SET_REJECT = '-STS_REJECT-'
EVT_STATUS_SET_POOR_QUALITY = '-STS_POOR-'
EVT_STATUS_SET_DUPLICATE = '-STS_DUP-'
EVT_STATUS_SET_JUST_OKAY = '-STS_OK-'
EVT_STATUS_SET_GOOD = '-STS_GOOD-'
EVT_STATUS_SET_BEST = '-STS_BEST-'
EVT_STATUS_TBD_REJECT = '-STSTBD_REJECT-'
EVT_STATUS_TBD_POOR_QUALITY = '-STSTBD_POOR-'
EVT_STATUS_TBD_DUPLICATE = '-STSTBD_DUP-'
EVT_STATUS_TBD_OK_GOOD_BEST = '-STSTBD_OKGB-'
EVT_STATUS_TBD_GOOD_OR_BEST = '-STSTBD_GOB-'

# Recalculate img_status / rvw_lvl from dedup_parms.json (tree context menu).
EVT_RECALC_STATUS = '-RECALC-STATUS-'

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

# Callable(values) -> list of rows; set on right-click before status menu (see pi_status_menu_context).
status_menu_rowgetter = None

# Last full values dict from window.read(); used when macOS Tk menu emits write_event_value(..., None).
last_window_values = None

# True while tree slider is programmatically syncing tab sliders.
syncing_from_tree = False

# True when the tree score comparator is in "<" mode.
tree_score_cmp_less_than = False

# User-facing label for current Show... filter status.
current_show_filter_label = "All Images"

''' standard global actions '''
PiOpenCollectionFolder(EVT_FILE_OPEN_FOLDER)
PiOpenCollectionCsv(EVT_FILE_OPEN_CSV)
PiNewCollection(EVT_FILE_NEW)
PiAddFolders(EVT_ADD_FOLDERS)
PiSaveCollection(EVT_FILE_SAVE)
PiFileProperties(EVT_FILE_PROPS)
PiAboutApp(EVT_ABOUT)
PiTestCode(EVT_TEST_CODE)
PiCleanupDir(EVT_CLEANUP_DIR)
PiNotImplemented(EVT_NOT_IMPL)

''' global filter table events '''
PiFilterTable(EVT_SHOW_ALL, None)
PiFilterTable(EVT_SHOW_TBD, FilterTbd())
PiFilterTable(EVT_SHOW_POSSIBLE_DUP, FilterPossibleDup())
PiFilterTable(EVT_SHOW_POSSIBLE_GOOD_PLUS, FilterPossibleGoodPlus())
PiFilterTable(EVT_SHOW_POSSIBLE_BEST, FilterPossibleBest())
PiFilterTable(EVT_SHOW_TBD_BEST_PLUS_BEST, FilterTbdBestPlusBest())
PiFilterTable(EVT_SHOW_FINAL_BEST, FilterFinalBest())

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
