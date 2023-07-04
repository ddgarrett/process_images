'''
    Display a Tree List based on data in the global config.table table
'''

import os

import PySimpleGUI as sg

import pi_config as c
from pi_element import PiElement

class PiTreeList(PiElement):

    folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
    file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'

    def __init__(self,key="-TREE-",events=[]):
        super().__init__(key)
        self._events = {
            "New": self.update_list,
            "Open": self.update_list,
        }

        self._tree = (
            sg.Tree(data=sg.TreeData(),
                    auto_size_columns=True,
                    select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                    num_rows=5,
                    col0_width=10,
                    key=self.key,
                    # show_expanded=False,
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    )
            )

    def get_element(self) -> sg.Tree:
        return  self._tree

    def handle_event(self,event,values) -> bool:
        if event in self._events:
            return self._events[event](event,values)
        
        return False
    
    ''' Event Handlers '''
    def update_list(self,event,values) -> bool :
        treedata = sg.TreeData()
        print(c.directory,c.directory.split('/'))
        treedata.insert("",c.directory,c.directory,values=[],icon=self.folder_icon)
        for row in c.table:
            fullname = f"{row['file_location']}/{row['file_name']}"
            treedata.Insert(c.directory, fullname, row['file_name'], values=[], icon=self.file_icon)

        c.window[self.key].update(values=treedata)

        return False

'''
def add_files_in_folder(parent, dirname):
    global image_cnt, folder_cnt
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f)
        fullname = fullname.replace('\\','/') # added: replace back slash with forward slash
        # if it's a folder, add folder and recurse
        if os.path.isdir(fullname): 
            folder_cnt += 1          
            treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
            add_files_in_folder(fullname, fullname)
        elif f.lower().endswith((".png", ".gif",".jpg","jpeg")):
            image_cnt += 1
            treedata.Insert(parent, fullname, f, values=[os.stat(fullname).st_size], icon=file_icon)
'''