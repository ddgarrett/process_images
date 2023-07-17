'''
    Main program for Image Processing System

    1. Prompt user for existing or new image library folder
    2. Display folder hiearchy and images in the folder

'''

import PySimpleGUI as sg

from csv_table import CsvTable

import pi_config as c
from pi_menu import PiMenu
from pi_tree_list import PiTreeList
from pi_image_elem import PiImageElem
from pi_folder_stats import FolderStats

elements = []

def init_window():
    sg.theme('black')
    # sg.set_options(margins=(0, 0))
    
    menu = PiMenu()
    tree = PiTreeList(key=c.EVT_TREE,headings=FolderStats.get_headers())
    image = PiImageElem(key="-IMAGE-",event=c.EVT_TREE)
    # image = PiImageThumbElem(key="-IMAGE-",event=c.EVT_TREE)

    gallery_tab = [[sg.Text('Tab 1')],
               [sg.Text('Put your layout in here')],
               [sg.Text('Input something'), sg.Input(size=(12,1), key='-IN-TAB1-')]]
    
    image_tab = image.get_element()

    # The TabgGroup layout - it must contain only Tabs
    tab_group_layout = [[sg.Tab('Image', image_tab,     key='-IMAGE_TAB-'),
                         sg.Tab('Gallery', gallery_tab, key='-GALLERY_TAB-')]]
    
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
    while True:
        event, values = c.window.read()

        # if event has MENU_KEY_SEPARATOR, remove it
        if event != None:
            _,_,event = event.rpartition(sg.MENU_KEY_SEPARATOR)

        v = str(values)
        if len(v) > 120:
            v = v[:120]+"..."
        print(f'e: {event}, v: {v}')

        c.listeners.notify(event,values)

        if event in (sg.WIN_CLOSED, c.EVT_EXIT):
            ''' Putting test here allows other elements to do cleanup before exit  '''
            break

    c.window.close()


if __name__ == '__main__':
    main()
