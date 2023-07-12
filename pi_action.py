
'''
    Base Class for other Process Image Actions.

    Actions are usually created in response to an event such
    as one generated from a Menu Selection.

    Actions set themselves up as a listener when created and contain a
    callback to handle the event.

    Subclasses generally only need to override the handle_event methods.

'''

import pi_config as c  # configuration/globals singleton

class PiAction:

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