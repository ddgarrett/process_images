'''
    Menu for Process Image App

'''

import os

import PySimpleGUI as sg

import pi_config as c
import pi_util as util 
from pi_element import PiElement
from status_menu import StatusMenu
from pi_action_reorg_img import PiActionReorgImg


class PiMenu(PiElement):

    def __init__(self,key=None):
        super().__init__(key=key)

    def get_element(self) -> sg.Menu:
        ''' Return the sg.Menu element for Process Image App
        '''

        # ------ Menu Definition ------ #
        menu_def = [['&File', 
                        [f'&Open::{c.EVT_FILE_NEW}', 
                         PiActionReorgImg().item(),
                         f'E&xit::{c.EVT_EXIT}' 
                        ] 
                    ],

                    ['&Help', f'&About...::{c.EVT_ABOUT}'], ]
        
        return sg.Menu(menu_def, )
