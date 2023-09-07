'''
    Export selected files to the '_export' directory where the collection.csv file
    is located.

    Listens for event names generated when this action was created.

    Like all actions, this class has a 'handle_event(self,event,values)' method.

    When a new instance of this class is created:
        text   - menu item text to display
        rowget - method to call to get list of rows to map

    To use, simply create a new instance with the name of the event
    and the key of the list within event values. For example:

        # set up action for Export Event and Tree List 
        PiActionExport(rowget=self.get_selected_rows).item(),
'''
import os

import pi_config as c
from pi_action import PiAction

class PiActionExport(PiAction):
    '''
        Export selected files and folders.
        Parms:
        text   - menu item text to display
        rowget - method to call to get list of rows to map

    '''

    last_id = 0  # for generating unique Event IDs

    @classmethod
    def next_id(cls):
        cls.last_id += 1
        return cls.last_id
    
    def __init__(self,text="Export",rowget=None):
        self._id = self.next_id()
        self._text = text
        self._rowget=rowget
        super().__init__(event=self._get_event())

    def _get_event(self):
        return f'-PiActionExport{self._id}-'

    def item(self):
        ''' return an item name and unique event id'''
        return f'{self._text}::{self._get_event()}'

    def handle_event(self,event,values):
        ''' Hand Map Event - get list of rows and display in map '''

        # callback row getter
        rows = self._rowget(values)

        for row in rows:
            subdir = row['file_location']
            fn     = row['file_name']
            src = f'{c.directory}{subdir}/{fn}'
            dst = f'{c.directory}/_export{subdir}/{fn}'
            print(f'copy from {src} to {dst}')
