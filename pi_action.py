
'''
    Base Class for other Process Image Actions.

    Actions are usually created in response to an event such
    as one generated from a Menu Selection.

    Actions set themselves up as a listener when created and contain a
    callback to handle the event.

    Subclasses generally only need to override the handle_event methods.

'''
import os

import PySimpleGUI as sg
from exif_loader import ExifLoader

from image_collection import ImageCollection
import pi_config as c  # configuration/globals singleton
import pi_util as util 
from pi_filters import Filter

class PiAction:
    ''' Parent Action Class '''

    def __init__(self,event=None):
        self._event = event
        if event != None:
            c.listeners.add(event,self.handle_event)

    def add_handler(self,event=None):
        if event != None:
            self._event = event
        if self._event != None:
            c.listeners.add(event,self.handle_event)

    def remove_handler(self):
        c.listeners.remove(self._event,self.handle_event)
        
    def handle_event(self,event,values):
        print("unhandled action event: ",event)

''' A few Common Global Actions for New, Save, Open, Filter Table'''

class PiOpenCollection(PiAction):
    def handle_event(self,event,values):
        filename = sg.popup_get_file('',no_window=True,file_types=(("Image Collection", "image_collection.csv"),))
        if filename:
            table = ImageCollection(filename)
            if table:
                d = os.path.dirname(filename)
                util.set_collection(table,d,values)
                c.update_status(f"Collection with {len(c.table.rows())} images loaded from {d}")
            else:
                c.update_status("Error opening collection file")
        else:
            c.update_status("Open collection canceled")

class PiNewCollection(PiAction):
    def handle_event(self,event,values):
        table,d = ExifLoader.new_collection()
        table.resort()
        table.renumber()
        if table:
            util.set_collection(table,d,values)
            c.update_status(f"{len(c.table.rows())} images loaded from {d}")
        else:
            c.update_status("New collection canceled")

class PiAddFolders(PiAction):
    def handle_event(self,event,values):
        # get count of rows before adding any folders
        c.table.filter_rows()
        pic_count = len(c.table.rows())

        # add folders to table
        table,d = ExifLoader.add_folders()
        table.resort()
        table.renumber()
        if table:
            util.set_collection(table,d,values)
            pics_added = len(c.table.rows()) - pic_count
            c.update_status(f"{pics_added} images added from {d}")
        else:
            c.update_status("Add folders canceled")

class PiSaveCollection(PiAction):
    def handle_event(self,event,values):
        if c.table and len(c.table.fn) > 0:
            c.table.save()
            c.update_status(f"Collection with {len(c.table._original_rows)} images saved to {c.table.fn}")
        else:
            c.update_status("No collection loaded")

class PiAboutApp(PiAction):
    def handle_event(self,event,values):
        sg.popup('About this program', f'Process Images\nVersion {c.VERSION}', sg.get_versions())

class PiNotImplemented(PiAction):
    def handle_event(self,event,values):
        sg.popup(f'Function not yet implemented')

class PiFilterTable(PiAction):
    def __init__(self, event=None,filter:Filter=None):
        self._filter = filter
        super().__init__(event)

    def handle_event(self,event,values):
        if not c.table:
            return 
        
        c.table.filter_rows(self._filter)
        c.listeners.notify(c.EVT_TABLE_LOAD,values)

        if self._filter == None:
            c.update_status("Showing All Images")
        else:
           c.update_status(f"Collection Filtered for {self._filter.get_descr()}")