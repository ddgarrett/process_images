'''
    Reorganize selected folders to put images in a yyyy-mm-dd subfolder
    where yyyy-mm-dd is the date the photo was taken.

    Details:
    1. pictures without a date (defaulted to "1969:12:31 16:00:00") or a "0000-00-00" date
       are moved into a "0000-00-00 NO DATE" subfolder.
    2. duplicate pictures are moved into a f'/_dup/{fn}/{date_yyyy_mm_dd}/' folder
    3. remaining folders, those without a recognized image format or empty, are
       moved to either _empty or _lost

    Listens for a unique event name generated when this action was created. 
    The unique part of the event name is generated via a class variable which
    is incremented for each instance of this class.

    Like all actions, this class has a 'handle_event(self,event,values)' method.

    When a new instance of this class is created:
        text   - menu item text to display
        dirget - method to call to get list of directories to reorganize

    To use, simply create a new instance with the name of the event
    and the key of the list within event values. For example:

        # set up action for Export Event and Tree List 
        PiActionReorgImg(dirget=self.get_selected_dir).item(),
'''
import os
from pathlib import Path
import shutil

import pi_config as c
import pi_util as util 
from pi_action import PiAction

class PiActionReorgImg(PiAction):
    '''
        Reorganize selected folders.
        Parms:
        text   - menu item text to display
        dirget - method to call to get list of directories to reorganize
    '''

    last_id = 0  # for generating unique Event IDs

    @classmethod
    def next_id(cls):
        cls.last_id += 1
        return cls.last_id
    
    @staticmethod
    def move_file(src_dir, dst_dir,fn,msg=None):
            ''' Move file name fn from source directory src_dir
                to destination directory dst_dir.
                If msg is specified show it in the status'''
            
            util.move_file(src_dir,dst_dir,fn)

            ''' This didn't seem to be working
            if msg:
                c.update_status(msg)
                c.window.Refresh()
            '''

    def __init__(self,text="&Reorg Images",dirget=None):
        self._id = self.next_id()
        self._text = text
        self._dirget=dirget
        super().__init__(event=self._get_event())

    def _get_event(self):
        return f'-PiActionReorgImg{self._id}-'

    def item(self):
        ''' return an item name and unique event id'''
        return f'{self._text}::{self._get_event()}'

    def handle_event(self,event,values):
        ''' Handle Reorg Images Event - get list of directories
            and move images within those directories or a subdirectory of 
            that directory to a subdirectory named after the date
            the image was taken: "yyyy-mm-dd" 
        '''
        directories = [""]
        if self._dirget:
            directories = self._dirget(values)

        print(f'reorging directories: {directories}')
        cnt = 0
        table = c.table

        # make sure table is NOT filtered!!!
        table.filter_rows()

        for dir in directories:

            for row in table:
                if len(dir) == 0 or row['file_location'].startswith(dir):
                    curr_file_loc = row['file_location']
                    fn = row['file_name']
                    dt  = row['img_date_time']

                    if dt[0:10] in ["0000:00:00","1969:12:31"]:
                        new_file_loc = f'{dir}/0000-00-00 NO DATE{curr_file_loc}'
                    else:
                        new_file_loc = f'{dir}/{dt[0:4]}-{dt[5:7]}-{dt[8:10]}'

                    if curr_file_loc != new_file_loc:

                        # if file already exists, move under _dup filder
                        if Path(f'{c.directory}{new_file_loc}/{fn}').exists():
                            # NOTE: currently, because the 0000-00-00 subdirectory includes the original file path
                            #       duplicates will NEVER go into the _dup subdirectory
                            if dt[0:10] in ["0000:00:00","1969:12:31"]:
                                new_file_loc = f'{dir}/_dup/{fn}/0000-00-00 NO DATE{curr_file_loc}'
                            else:
                                new_file_loc = f'{dir}/_dup/{fn}/{dt[0:4]}-{dt[5:7]}-{dt[8:10]}{curr_file_loc}'

                        msg = f'moving {fn} from {curr_file_loc} to {new_file_loc}'
                        cnt   += 1
                        self.move_file(curr_file_loc,new_file_loc,fn,msg)
                        row['file_location'] = new_file_loc

        if cnt > 0:
            table.resort()
            table.renumber()
            util.set_collection(table,c.directory,values)

        # self._move_unused()
        c.listeners.notify(c.EVT_CLEANUP_DIR,values)
        print("unused moved")
        c.update_status(f'moved {cnt} images')
