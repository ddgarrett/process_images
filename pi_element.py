
'''
    Base Class for other Process Image App Element Type Classes
    such as Menus and Tabs which include both display and
    event handling.

'''

import PySimpleGUI as sg

import pi_config as c  # configuration/globals singleton

class PiElement:

    def __init__(self,key=None):
        self.key=key

    def get_element(self) -> sg.Element:
        ''' Return new instance of a PySimpleGUI element or element subclass
            Subclasses should override this method. 
            If they don't, calls will get a Text with the "not yet implmented" message '''
        [[sg.Text(f'{self.__class__.__name__} not yet implemented')]]
    
    def handle_event(self,event,values) -> bool:
        ''' Return true if this object handled the event and 
            no other handlers need to worry about it. '''        
        return False

    def _nop(self,event,values) -> bool:
        ''' Convenience event handler for not yet implemented functions '''
        msg = f'event {event} not yet implemented in class {self.__class__.__name__}'
        print(msg)
        print(f'    values: {values}')
        c.update_status(msg)
        return True

