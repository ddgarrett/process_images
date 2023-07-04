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

elements = []
c.metadata = CsvTable("image_collection_metadata.csv")

def init_window():
    sg.theme('black')
    # sg.set_options(margins=(0, 0))
    
    menu = PiMenu()
    tree = PiTreeList(key="-TREE-")
    image = PiImageElem(key="-IMAGE-",event="-TREE-")

    elements.extend((menu,tree,image))
    
    # ------ GUI Defintion ------ #
    layout = [[menu.get_element()],
              [sg.Pane(
                [sg.Column([[tree.get_element()]], expand_y=True),
                # sg.VSeperator(),
                sg.Column([[image.get_element()]], expand_x=True, expand_y=True, key="-IMGCOL-")],
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
    status = c.window['-STATUS-']

    print(f'window has status: {"-STATUS-" in c.window.AllKeysDict}')

    # ------ Loop & Process button menu choices ------ #
    while True:
        event, values = c.window.read()
        event_handled = False

        for e in elements:
            if e.handle_event(event,values):
                event_handled = True
                break

        if event_handled:
            pass
        elif event in (sg.WIN_CLOSED, 'Exit'):
            ''' Putting test here allows other elements to do cleanup before exit.
                Also allows elements to veto the exit by returning True from their handle_event() method '''
            break
        else:
            print(f'e: {event}, v: {values}')

        # TODO: add logic for internal event notifications
        # such as '-TABLE-LOADED-'  {'table':table_object}
        # using python queues
        # OR
        # Have 'Open' and 'New' passed to the tree list object?
        # but that might have issues with order it's called, though it would be simpler.

    c.window.close()


if __name__ == '__main__':
    main()
