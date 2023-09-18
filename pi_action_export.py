'''
    Export selected files to the '_export' directory where the collection.csv file
    is located.

    Listens for event names generated when this action was created.

    Like all actions, this class has a 'handle_event(self,event,values)' method.

    When a new instance of this class is created:
        text   - menu item text to display
        rowget - method to call to get list of rows to export

    To use, simply create a new instance with the name of the event
    and the key of the list within event values. For example:

        # set up action for Export Event and Tree List 
        PiActionExport(rowget=self.get_selected_rows).item(),
'''
import os
from pathlib import Path
import shutil

import pi_config as c
from pi_action import PiAction

class PiActionExport(PiAction):
    '''
        Export selected files and folders.
        Parms:
        text   - menu item text to display
        rowget - method to call to get list of rows to export
    '''

    last_id = 0  # for generating unique Event IDs

    @classmethod
    def next_id(cls):
        cls.last_id += 1
        return cls.last_id
    
    @staticmethod
    def copy_file(src_dir, dst_dir,fn,msg=None):
            ''' Copy file name fn from source directory src_dir
                to destination directory dst_dir.
                If msg is specified show it in the status'''
            
            # make sure to prefix source and dest with root directory name
            src = f'{c.directory}{src_dir}/{fn}'
            dst = f'{c.directory}{dst_dir}/{fn}'

            # make sure destination directory exists
            Path(f'{c.directory}{dst_dir}').mkdir(parents=True, exist_ok=True)

            if msg:
                c.update_status(msg)
                c.window.Refresh()

            shutil.copy2(src,dst)

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
        ''' Handle Export Event - get list of rows and copy
            those images to _export subdirectory. '''

        rows = self._rowget(values)
        copy_cnt = len(rows)
        cnt = 0

        for row in rows:
            cnt   += 1
            subdir = row['file_location']
            fn     = row['file_name']

            dst_dir = f'/_export{subdir}'
            msg     = f'export {cnt} of {copy_cnt} {subdir}/{fn}'

            self.copy_file(subdir,dst_dir,fn,msg)

        c.update_status(f'exported {cnt} images to {c.directory}/_export')
