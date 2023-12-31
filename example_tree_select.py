#!/usr/bin/env python
import sys
import os
import PySimpleGUI as sg

from datetime import datetime

# sg.theme('light brown 8')
sg.theme('black')


""" Show Tree of selected files and folders.
    Allow selecting a node via its key.
    Demonstrates use of generating double click event for tree
"""

# Base64 versions of images of a folder and a file. PNG files (may not work with PySimpleGUI27, swap with GIFs)

folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'

'''
starting_path = sg.popup_get_folder('Folder to display')

if not starting_path:
    sys.exit(0)
'''

treedata = sg.TreeData()

def key_to_id(tree, key):
    """
    Convert PySimplGUI element key to tkinter widget id.
    : Parameter
      key - key of PySimpleGUI element.
    : Return
      id - int, id of tkinter widget
    """
    dictionary = {v:k for k, v in tree.IdToKey.items()}
    print("tree dict len:",len(dictionary))
    return dictionary[key] if key in dictionary else None

def select(tree, key=''):
    """
    Move the selection of node to node key.
    : Parameters
      key - str, key of node.
    """
    id_ = key_to_id(tree, key)
    if id_:
        tree.Widget.see(id_)
        tree.Widget.selection_set(id_)
    else:
        print("id not found for key ",key)

def add_files_in_folder(parent, dirname):
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f)
        fullname = fullname.replace('\\','/') # added: replace back slash with forward slash
        if os.path.isdir(fullname):            # if it's a folder, add folder and recurse
            # print(f"folder - parent:{parent}, fullname:{fullname}, f:{f}")
            treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
            add_files_in_folder(fullname, fullname)
        else:
            # print(f"file - parent:{parent}, fullname:{fullname}, f:{f}")
            treedata.Insert(parent, fullname, f, values=[os.stat(fullname).st_size], icon=file_icon)

# add_files_in_folder('', starting_path)

layout = [
          [ sg.Tree(data=treedata,
                   headings=['Size', ],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=20,
                   col0_width=40,
                   key='-TREE-',
                   show_expanded=False,
                   enable_events=True,
                   expand_x=True,
                   expand_y=True,
                   )],
          [ sg.FolderBrowse(target="-FOLDER-",button_text="Folder...",size=(8,1)),
            sg.In(size=(25, 1), enable_events=True, 
                  key="-FOLDER-", expand_x=True) ],
          [ sg.Button(key="-SELECT-",button_text="Select",size=(8,1)),
            sg.In(size=(25, 1), enable_events=False, 
                  key="-TREE-KEY-", expand_x=True) ],
          [ sg.Text('', relief=sg.RELIEF_SUNKEN,
                    size=(55, 1), pad=(0, 3), key='-STATUS-', expand_x=True),
            sg.Sizegrip(pad=(3,3)) ]
    ]

window = sg.Window('Tree Element Test', layout, resizable=True, finalize=True,
                   enable_window_config_events=True)

def update_status(text):
    window['-STATUS-'].update(text)

# Below sends a '-TREE-' event followed by a '-TREE-_double_clicked' event
window['-TREE-'].bind('<Double-Button-1>', '_double_clicked')

while True:     # Event Loop
    event, values = window.read()
    print(f'-------- event: {event}  - {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}')
    print(f'values: {values}')

    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    
    if event == '-FOLDER-':
        starting_path = values['-FOLDER-']
        treedata = sg.TreeData()
        add_files_in_folder('', starting_path)
        window['-TREE-'].update(values=treedata)
    elif event == '-SELECT-':
        select(window['-TREE-'],key=values['-TREE-KEY-'])



window.close()