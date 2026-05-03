'''
    Menu for Process Image App
'''

import FreeSimpleGUI as sg

import pi_config as c
from pi_element import PiElement
from status_menu import StatusMenu
from pi_action_reorg_img import PiActionReorgImg


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
                         '&Open',
                         [
                             f'&Folder::{c.EVT_FILE_OPEN_FOLDER}',
                             f'CSV &file::{c.EVT_FILE_OPEN_CSV}',
                         ],
                         f'&Save::{c.EVT_FILE_SAVE}', 
                         f'&Add Folders::{c.EVT_ADD_FOLDERS}',
                         PiActionReorgImg().item(),
                         f'E&xit::{c.EVT_EXIT}' 
                        ] 
                    ],
                    ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],

                    ['S&how', status_menu.get_show_submenu()],

                    ['&Help', f'&About...::{c.EVT_ABOUT}'], ]
        
        return sg.Menu(menu_def, )
