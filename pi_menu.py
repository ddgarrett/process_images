'''
    Menu for Process Image App

'''

import os

import PySimpleGUI as sg

# from csv_table import CsvTable
from image_collection import ImageCollection
from exif_loader import ExifLoader

import pi_config as c
import pi_util as util 
from pi_element import PiElement


class PiMenu(PiElement):

    def __init__(self,key=None):
        super().__init__(key=key)

    def get_element(self) -> sg.Menu:
        ''' Return the sg.Menu element for Process Image App
        '''
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

                    ['&Show', 
                        [f'&All::{c.EVT_SHOW_ALL}',
                         f'&Duplicate or Better::{c.EVT_SHOW_DUP_PLUS}',
                         f'&Okay or Better::{c.EVT_SHOW_OK_PLUS}',
                         f'&Good or Best::{c.EVT_SHOW_GOOD_PLUS}',
                         f'&Best::{c.EVT_SHOW_BEST}'
                        ]
                    ],

                    ['&Help', f'&About...::{c.EVT_ABOUT}'], ]
        
        return sg.Menu(menu_def, )

    ''' Event Handlers '''
    # so far all are common functions