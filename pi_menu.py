'''
    Menu for Process Image App

'''

import os

import PySimpleGUI as sg

import pi_config as c
import pi_util as util 
from pi_element import PiElement
from status_menu import StatusMenu

class PiMenu(PiElement):

    def __init__(self,key=None):
        super().__init__(key=key)

    def get_element(self) -> sg.Menu:
        ''' Return the sg.Menu element for Process Image App
        '''

        status_menu = StatusMenu()

        # ------ Menu Definition ------ #
        menu_def = [['&File', 
                        [f'&New::{c.EVT_FILE_NEW}',
                         f'&Open::{c.EVT_FILE_OPEN}', 
                         f'&Save::{c.EVT_FILE_SAVE}', 
                         f'&Properties::{c.EVT_FILE_PROPS}', 
                         f'E&xit::{c.EVT_EXIT}' 
                        ] 
                    ],
                    ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],

                    ['&Show', status_menu.get_show_submenu()],

                    ['&Help', f'&About...::{c.EVT_ABOUT}'], ]
        
        return sg.Menu(menu_def, )
