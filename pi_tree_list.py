'''
    Display a Tree List based on data in the global config.table table
'''

import os

import PySimpleGUI as sg

import pi_config as c
from pi_element import PiElement
from pi_treedata import PiTreeData

class PiTreeList(PiElement):

    def __init__(self,key="-TREE-",headings=[],events=[]):
        super().__init__(key)

        c.listeners.add(c.EVT_TABLE_LOAD,self.update_list)
        c.listeners.add(c.EVT_TABLE_ROW_CHG,self.update_rows)

        menu = ['', 
            [f'Map::{c.EVT_ACT_MAP}', 
             'Properties', 
             'Review',['Initial', 'Quality','Duplicate','Selected','Best'],
             'Show',['All','Reject','Bad','Duplicate','Ok','Good','Best','Filter...'],
             'Save',
             'Exit' ]]

        self._tree_data = PiTreeData(c.table)
        self._tree = (
            sg.Tree(data=self._tree_data,
                    headings=headings,
                    auto_size_columns=True,
                    select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                    num_rows=5,
                    col0_width=25,
                    key=self.key,
                    # show_expanded=False,
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    right_click_menu=menu
                    )
            )
        
        self._key_id_dict = {}

    def get_element(self) -> sg.Tree:
        return  self._tree
    
    ''' Event Handlers '''
    def update_list(self,event,values):
        ''' Update the tree data after a table is loaded or filtered '''
        self._tree_data = PiTreeData(c.table.rows())
        c.window[self.key].update(values=self._tree_data)
        self._key_id_dict = {v:k for k, v in self._tree.IdToKey.items()}

    def update_rows(self,event,values):
        ''' update display after row value changes '''
        rows = values[c.EVT_TABLE_ROW_CHG]
        self._tree_data._update_rows(self._tree,self._key_id_dict,rows)

