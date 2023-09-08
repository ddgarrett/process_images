''' Implement action to display and update properties '''

import PySimpleGUI as sg

from pi_action import PiAction

class PiFileProperties(PiAction):
    def handle_event(self,event,values):
        layout = [[sg.Text(f'Properties Window \nEvent: {event}\nValues: {values}')],
                 [sg.OK()]]

        window = sg.Window('Second Form', layout)
        window.read() # wait for any event
        window.close()