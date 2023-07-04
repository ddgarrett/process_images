
'''
    Defines standard set of calls for a tab.

    Events for this tab should be prefixed with the tab id string.
    Methods are defined to add and remove that prefix.

    ** TODO: put example

'''

import PySimpleGUI as sg

from pi_element import PiElement

class PiTab(PiElement):

    def __init__(self,key:str=None,name:str=None, ):
        self._name = name

        if key == None:
            self.key = name
        else:
            self.key = id

        self._selected = False
        self._event_pfx = f'{self.key}.'

    def get_element(self) -> sg.Tab:
        layout = super().get_element()
        return sg.Tab(self._name, layout, key=self.key)
    
    def _global_id(self,local_id:str):
        ''' Prefixes a local id with self.key + '.' 
            to create an ID that is unique across
            tabs
        '''
        return f'{self._event_pfx}{local_id}'
    
    def _local_id(self,global_id):
        ''' Undoes what _global_id() does
            if global_id begins with self.key.
             
            Otherwise returns the global_id unchanged.
         '''
        if global_id.startswith(self._event_pfx):
            return global_id[len(self._event_pfx):]
        
    def is_selected(self):
        return self._selected


    ''' SUBCLASSES OPTIONALLY OVERRIDE THESE METHODS '''
    
    def handle_event(self,event,values) -> bool:
        ''' Override this method in subclasses
            to handle events for which self.is_my_event() 
            has returned true.

            Call super().handle_event(event,values) to first
            check for select, deselect events:

                if super().handle_event(event,values):
                    return True

                event = self._local_id(event)

            Any local event ids should be prefixed with self.key + "."
            when the _get_layout() methods creates GUI objects.

            This can be done using self._global_id(local_id)

        '''
        if event == '-SELECT-':
            self._select(event,values)
            return True
        elif event == '-DESELECT-':
            self._deselect(event,values)
            return True
        
        return False
    
    def _select(self,event,values):
        ''' React to a select event '''
        self._select = True

    def _deselect(self,event,values):
        ''' React to deselect event '''
        self._select = False