''' General Process Image Utilities '''

import pi_config as c

def get_row_for_fn(filename):
    ''' given a filename which includes the "file_location + '/' + file_name"
        find the row for the file
    '''
    loc,_,name  = filename.rpartition('/') 
    for row in c.table:
        if row['file_name'] == name and row['file_location'] == loc:
            return row

    return None

def set_collection(table,directory,values):
    ''' Set global table and directory then notify 
        listeners. Values are from the event which 
        triggered the change.
    '''
    c.table = table
    c.directory = directory
    c.listeners.notify(c.EVT_TABLE_LOAD,values)


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