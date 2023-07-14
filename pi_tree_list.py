'''
    Display a Tree List based on data in the global config.table table
'''

import os

import PySimpleGUI as sg

import pi_config as c
from pi_element import PiElement
from pi_treedata import PiTreeData

class PiTreeList(PiElement):

    folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
    file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'

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

