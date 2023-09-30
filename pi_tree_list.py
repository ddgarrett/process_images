'''
    Display a Tree List based on data in the global config.table table
'''

import os

import PySimpleGUI as sg
from pi_action_export import PiActionExport
from pi_action_map import PiActionMap
from pi_action_blog import PiActionBlog

import pi_config as c
from pi_element import PiElement
from pi_filters import SelectedTreeNodesFilter
from pi_treedata import PiTreeData
from status_menu import StatusMenu

class PiTreeList(PiElement):

    def __init__(self,key="-TREE-",headings=[],events=[]):
        super().__init__(key)

        c.listeners.add(c.EVT_TABLE_LOAD,self.update_list)
        c.listeners.add(c.EVT_TABLE_ROW_CHG,self.update_rows)

        status_menu = StatusMenu(self.get_selected_rows)

        menu = ['',
           [ status_menu.get_set_menu(),
             '---',
             PiActionMap(rowget=self.get_selected_rows).item(), 
             PiActionExport(rowget=self.get_selected_rows).item(), 
             PiActionBlog(rowget=self.get_selected_rows).item(),
             f'Properties::{c.EVT_FILE_PROPS}',

             'S&how', status_menu.get_show_submenu(),

             f'&Save::{c.EVT_FILE_SAVE}',
             f'E&xit::{c.EVT_EXIT}' ]]

        self._tree_data = PiTreeData(c.table.rows())
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
    
    def get_selected_rows(self,values):
        ''' Return a list of selected rows. 
            A selected folder returns all of the rows in the folder.
            Values is the values returned by window.read().
            Therefore we extract the list of selected
            files and folders via our own key.
        '''
        files_folders = values[self.key]
        rows = self._tree_data.rows
        if len(rows) == 0 or len(files_folders) == 0:
            return []
        
        filter = SelectedTreeNodesFilter(files_folders)
        rows = filter.filter(rows)
        # print(f'{len(rows)} rows selected')
        return rows

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

