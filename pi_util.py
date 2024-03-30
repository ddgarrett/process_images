''' General Process Image Utilities '''

from pathlib import Path
import shutil
import pi_config as c

def get_row_for_fn(filename):
    ''' given a filename which includes the "file_location + '/' + file_name"
        find the row for the file
    '''
    filename = filename.replace('\\','/')
    loc,_,name  = filename.rpartition('/') 
    for row in c.table:
        if row['file_name'] == name and row['file_location'] == loc:
            return row

    return None

def dir_loaded(subdir):
    ''' return true if subdirectory already loaded '''
    loc = subdir.replace('\\','/')
    for row in c.table:
        if row['file_location'] == loc:
            return True

    return False

def dir_in_collection(dir):
    ''' return true if the directory or any subdirectories of it
        contain any images in this collection '''
    
    loc = dir.replace('\\','/')
    for row in c.table:
        if row['file_location'].startswith(loc):
            return True

    return False

def get_fn_for_row(row):
    ''' given a row, return the file name'''
    fn = f"{row['file_location']}/{row['file_name']}"
    return fn.replace('\\','/')

def set_collection(table,directory,values):
    ''' Set global table and directory then notify 
        listeners. Values are from the event which 
        triggered the change.
    '''
    c.table = table
    c.directory = directory
    c.listeners.notify(c.EVT_TABLE_LOAD,values)

def move_file(src_dir, dst_dir,fn):
    ''' Move a file from source directory to destination directory 
        creating destination directory if it doesn't exist.
    '''
    # make sure to prefix source and dest with root directory name
    src = f'{c.directory}{src_dir}/{fn}'
    dst = f'{c.directory}{dst_dir}/{fn}'

    # make sure destination directory exists
    Path(f'{c.directory}{dst_dir}').mkdir(parents=True, exist_ok=True)

    shutil.move(src,dst)
    
def move_dir(src_dir, dst_dir):
    ''' Move a directory to destination directory 
        creating destination directory if it doesn't exist.
    '''
    # make sure to prefix source and dest with root directory name
    src = f'{c.directory}{src_dir}'
    dst = f'{c.directory}{dst_dir}'

    # make sure destination directory exists
    Path(f'{dst}').mkdir(parents=True, exist_ok=True)

    shutil.move(src,dst)

''' Below should be in it's own file? Maybe Along with Events from  pi_config? '''
class EventListener:
    ''' Simple Event Listener
     
        Currently used for window events and
        table load event.

        Event listener callbacks are passed and event
        and values. Usually a string and a dictionary
        as implemented by PySimpleGUI.
    '''
    def __init__(self):
        self._events = {}

    def add(self,event,callback):
        if not event in self._events:
            self._events[event] = []
        
        self._events[event].append(callback)

    def remove(self,event,callback):
        if event in self._events:
            callbacks = event['event']
            if callback in callbacks:
                callbacks.remove(callback)

    def notify(self,event,values):
        if event in self._events:
            for callback in self._events[event]:
                if c.TRACE_EVENTS and event != c.EVT_WIN_CONFIG:
                    print(f"*** event {event} callback {callback}")
                callback(event,values)