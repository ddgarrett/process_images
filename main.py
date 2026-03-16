'''
    Main program for Image Processing System

    1. Prompt user for existing or new image library folder
    2. Display folder hiearchy and images in the folder

    Note that main menu changes depending on if we are running
    the Organize Images or Review Images function.

'''

import sys
import subprocess

# Check Tcl/Tk version in a subprocess so we never load tkinter in the main process
# when it would trigger the native "macOS 26 required" abort (Apple's Tcl 8.5 on macOS).
def _check_tcl_version():
    try:
        r = subprocess.run(
            [sys.executable, '-c', 'import tkinter; print(tkinter.Tcl().eval("info patchlevel"))'],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode != 0:
            return None  # e.g. abort in subprocess
        version = (r.stdout or '').strip()
        return version
    except Exception:
        return None

def _require_tcl_86():
    version = _check_tcl_version()
    if version is None:
        print('Process Images could not detect Tcl/Tk, or the GUI runtime failed (e.g. "macOS 26 required" / abort).')
        print('On macOS, use a Python that includes Tcl/Tk 8.6:')
        print('  - Install Python from https://www.python.org/downloads/ (3.10+), or')
        print('  - Use Homebrew: brew install python-tk, then create your venv with that Python.')
        print('Then recreate your venv and run this program again.')
        sys.exit(1)
    if version.startswith('8.5'):
        print('Process Images requires Tcl/Tk 8.6 or newer. This Python has Tcl/Tk {}.'.format(version))
        print('On macOS, the system Python often ships with old Tcl/Tk 8.5, which causes crashes.')
        print('Install Python from https://www.python.org/downloads/ (3.10+) or use Homebrew python-tk,')
        print('then recreate your venv with that Python and run again.')
        sys.exit(1)

_require_tcl_86()

import warnings
# Suppress FreeSimpleGUI's tkinter 8.5 warning if we ever run with 8.5 (we normally exit above)
warnings.filterwarnings('ignore', message='.*VERY old version of tkinter.*Please upgrade to 8.6')

import FreeSimpleGUI as sg

import pi_config as c
from pi_gallery_elem import PiGalleryElem

from pi_tree_list import PiTreeList
from pi_image_elem import PiImageElem
from pi_folder_stats import FolderStats
from csv_table import CsvTable

elements = []

def init_window():
    # Main Menu for either Organize Images
    # or Review Images
    if c.app_function == c.APP_ORG_IMG:
        from pi_oi_menu import PiMenu
        window_title = 'Organize Images'
    else:
        from pi_menu import PiMenu
        window_title = 'Review Images'

    sg.theme('black')
    # sg.set_options(margins=(0, 0))
    
    menu = PiMenu()
    tree = PiTreeList(key=c.EVT_TREE,headings=FolderStats.get_headers())
    image = PiImageElem(key="-IMAGE-",event=[c.EVT_TREE,c.EVT_IMG_SELECT])
    gallery = PiGalleryElem(key="-GALLERY-",event=c.EVT_TREE)

    image_tab = image.get_element()
    gallery_tab = gallery.get_element()

    # The TabgGroup layout - it must contain only Tabs
    tab_group_layout = [[sg.Tab('Gallery', gallery_tab, key='-GALLERY_TAB-'),
                         sg.Tab('Image', image_tab,     key='-IMAGE_TAB-')]]
    
    tab_group = [[sg.TabGroup(tab_group_layout,
                       enable_events=True,
                       expand_x=True,expand_y=True,
                       key='-TABGROUP-')]]

    # ------ GUI Defintion ------ #
    layout = [[menu.get_element()],
              [sg.Pane(
                    [   sg.Column([[tree.get_element()]], expand_y=True),
                        sg.Column(tab_group, key="-IMGCOL-")
                    ],
                    orientation='h', relief=sg.RELIEF_SUNKEN, 
                    expand_x=True, expand_y=True, k='-PANE-',
                    border_width=1, background_color="white")
              ],
              [sg.Text('', relief=sg.RELIEF_SUNKEN,
                    size=(55, 1), pad=(0, 3), key='-STATUS-', expand_x=True),
                sg.Sizegrip(pad=(3,3))
                ]
              ]

    return sg.Window(window_title, layout, size=(800, 500), finalize=True,
                     resizable=True, enable_window_config_events=True)

def update_status(text):
    c.window['-STATUS-'].update(text)

def main():

    c.window = init_window()
    c.status = c.window['-STATUS-']

    c.window.bind("<Control_L><s>", '-FILE_SAVE-')

    # print(f'window has status: {"-STATUS-" in c.window.AllKeysDict}')

    # ------ Loop & Process events Until exit ------ #
    # buffer one event
    next_event = None
    next_values = None
    while True:
        if next_event != None:
            event = next_event
            values = next_values
            next_event = next_values = None
        else:
            event, values = c.window.read()

        # if event has MENU_KEY_SEPARATOR, remove it
        if event != None and type(event) == str:
            _,_,event = event.rpartition(sg.MENU_KEY_SEPARATOR)

        if  event != c.EVT_WIN_CONFIG:
            v = str(values)
            if len(v) > 120:
                v = v[:120]+"..."            
            print(f'e: {event}, v: {str(values)}')
        else:
            # remove multiple window config calls 
            new_event, new_values = c.window.read(timeout=500)
            while new_event  == c.EVT_WIN_CONFIG:
                new_event,new_values = c.window.read(timeout=500)

            # if a event other than timeout, buffer it for next loop
            if new_event != '__TIMEOUT__':
                next_event = new_event
                next_values = new_values
                print(f"buffering: {next_event}")

            print(f'e: {event} ')

        c.listeners.notify(event,values)

        if event in (sg.WIN_CLOSED, c.EVT_EXIT):
            ''' Putting test here allows other elements to do cleanup before exit  '''
            break

    c.window.close()


if __name__ == '__main__':
    main()
