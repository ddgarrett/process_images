''' General Process Image Utilities '''

import pi_config as c

def set_collection(table,directory,values):
    ''' Set global table and directory then notify 
        listeners. Values are from the event which 
        triggered the change.
    '''
    c.table = table
    c.directory = directory
    c.listeners.notify(c.EVT_TABLE_LOAD,values)


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
                if c.TRACE_EVENTS:
                    print(f"*** event {event} callback")
                callback(event,values)