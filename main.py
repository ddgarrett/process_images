'''
    Main program for Image Processing System

    1. Prompt user for existing or new image library folder
    2. Display folder hiearchy and images in the folder

'''

import PySimpleGUI as sg

import pi_config as c
from pi_gallery_elem import PiGalleryElem
from pi_menu import PiMenu
from pi_tree_list import PiTreeList
from pi_image_elem import PiImageElem
from pi_folder_stats import FolderStats
from csv_table import CsvTable

elements = []

def init_window():
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

    menu.set_handlers() # set non-global handlers

    return sg.Window('Process Images', layout, size=(800, 500), finalize=True,
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
