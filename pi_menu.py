'''
    Menu for Process Image App

'''

import os

import PySimpleGUI as sg

# from csv_table import CsvTable
from image_collection import ImageCollection
from exif_loader import ExifLoader

import pi_config as c
from pi_element import PiElement

class PiMenu(PiElement):

    def __init__(self,key=None):
        super().__init__(key=key)

        self._events = {
            "New": self.new_collection,
            "Open": self.open_collection,
            "Save": self.save_collection,
            "Properties": self.second_window,
            "About...": self.about_pi_app 
        }

    def get_element(self) -> sg.Menu:
        ''' Return the sg.Menu element for Process Image App
        '''
        # ------ Menu Definition ------ #
        menu_def = [['&File', ['&New','&Open', '&Save', '&Properties', 'E&xit']],
                    ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],
                    ['&Toolbar', ['---', 'Command &1', 'Command &2',
                                    '---', 'Command &3', 'Command &4']],
                    ['&Help', '&About...'], ]
        
        return sg.Menu(menu_def, )
    
    def handle_event(self,event,values) -> bool:
        if event in self._events:
            return self._events[event](event,values)
        
        return False

    ''' Event Handlers '''

    def new_collection(self,evnt,values) -> bool:
        table,d = self._init_new_collection()
        if table:
            c.table = table
            c.directory = d
            self.update_status(f"{len(c.table)} images loaded from {d}")
            return False  # let other elements receive the "New" event?
        else:
            self.update_status("New collection canceled")

        return True
    
    def about_pi_app(self,event,values) -> bool:
        sg.popup('About this program', f'Process Images\nVersion {c.VERSION}', sg.get_versions())
        return True
    
    def open_collection(self,event,values) -> bool:
        filename = sg.popup_get_file('',no_window=True,file_types=(("Image Collection", "image_collection.csv"),))
        if filename:
            table = ImageCollection(filename)
            if table:
                c.table = table
                c.directory = os.path.dirname(filename)
                self.update_status(f"Collection with {len(c.table)} images loaded from {filename}")
                return False # let other elements receive 'Open' event? Add Table to values?
            else:
                self.update_status("Error opening collection file")
        else:
            self.update_status("Open collection canceled")

        return True
    
    def save_collection(self,event,values):
        if c.table:
            c.table.save()
            self.update_status(f"Collection with {len(c.table)} images saved to {c.table.fn}")
        else:
            self.update_status("No collection loaded")

        return True

    def second_window(self,event,values) -> bool:

        layout = [[sg.Text('The second form is small \nHere to show that opening a window using a window works')],
                [sg.OK()]]

        window = sg.Window('Second Form', layout)
        event, values = window.read()
        window.close()
        return True
    
    ''' private methods '''
    def _init_new_collection(self):
        d = sg.popup_get_folder('',no_window=True)
        if not d:
            return None,None

        collection_fn = os.path.join(d, "image_collection.csv")
        if os.path.exists(collection_fn):
            msg = f'''
                Collection file already exists: \n 
                "{collection_fn}"\n
                Delete file then retry.
            '''
            sg.popup(msg)
            return None,None

        self.update_status(f"Searching for pictures in {d}...")
        c.window.refresh()

        table = ImageCollection(collection_fn)
        loader = ExifLoader(table,c.metadata)
        loader.load_dir(d)

        return table,d