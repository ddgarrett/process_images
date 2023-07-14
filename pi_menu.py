'''
    Menu for Process Image App

'''

import os

import PySimpleGUI as sg

# from csv_table import CsvTable
from image_collection import ImageCollection
from exif_loader import ExifLoader

import pi_config as c
import pi_util as util 
from pi_element import PiElement


class PiMenu(PiElement):

    def __init__(self,key=None):
        super().__init__(key=key)

        c.listeners.add(c.EVT__FILE_OPEN,self.open_collection)
        c.listeners.add(c.EVT_FILE_NEW,self.new_collection)
        c.listeners.add(c.EVT_FILE_SAVE,self.save_collection)
        c.listeners.add(c.EVT_FILE_PROPS,self.second_window)
        c.listeners.add(c.EVT_ABOUT,self.about_pi_app)

    def get_element(self) -> sg.Menu:
        ''' Return the sg.Menu element for Process Image App
        '''
        # ------ Menu Definition ------ #
        menu_def = [['&File', 
                        [f'&New::{c.EVT_FILE_NEW}',
                         f'&Open::{c.EVT__FILE_OPEN}', 
                         f'&Save::{c.EVT_FILE_SAVE}', 
                         f'&Properties::{c.EVT_FILE_PROPS}', 
                         f'E&xit::{c.EVT_EXIT}' 
                        ] 
                    ],
                    ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],
                    ['&Review', ['&0 - Initial ', '&1 - Quality', '&2 - Duplicates','&3 - Best','&4 - Best of Best','&All']],
                    ['&Help', f'&About...::{c.EVT_ABOUT}'], ]
        
        return sg.Menu(menu_def, )

    ''' Event Handlers '''

    def new_collection(self,event,values) -> bool:
        table,d = ExifLoader.new_collection()
        if table:
            util.set_collection(table,d,values)
            c.update_status(f"{len(c.table.rows())} images loaded from {d}")
            return False  # let other elements receive the "New" event?
        else:
            c.update_status("New collection canceled")

        return True
    
    def about_pi_app(self,event,values) -> bool:
        sg.popup('About this program', f'Process Images\nVersion {c.VERSION}', sg.get_versions())
        return True
    
    def open_collection(self,event,values) -> bool:
        filename = sg.popup_get_file('',no_window=True,file_types=(("Image Collection", "image_collection.csv"),))
        if filename:
            table = ImageCollection(filename)
            if table:
                d = os.path.dirname(filename)
                util.set_collection(table,d,values)
                c.update_status(f"Collection with {len(c.table.rows())} images loaded from {d}")
                return False # let other elements receive 'Open' event? Add Table to values?
            else:
                c.update_status("Error opening collection file")
        else:
            c.update_status("Open collection canceled")

        return True
    
    def save_collection(self,event,values):
        if c.table:
            c.table.save()
            c.update_status(f"Collection with {len(c.table.rows())} images saved to {c.table.fn}")
        else:
            c.update_status("No collection loaded")

        return True

    def second_window(self,event,values) -> bool:

        layout = [[sg.Text('The second form is small \nHere to show that opening a window using a window works')],
                [sg.OK()]]

        window = sg.Window('Second Form', layout)
        event, values = window.read()
        window.close()
        return True
    