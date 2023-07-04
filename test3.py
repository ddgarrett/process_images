
import sys
import os

import PySimpleGUI as sg
from csv_table import CsvTable

def add_path(dict,nodes,idx):
    ''' Add the indexed node to the dictionary
        then recurse to add children nodes under that node
        in the dictionary
    '''
    if idx >= len(nodes):
        # all done
        return 
        
    key = nodes[idx]
    if not key in dict:
        dict[key] = {}

    idx += 1
    return add_path(dict[key],nodes,idx)


def add_folder(row,dict):
    ''' ensure that all of the file location folders are in the dictionary '''
    loc = row['file_location']
    nodes = loc.split('/')
    add_path(dict,nodes,1) # skip first node - it's just an empty string


# get name of collection csv file
fn = sg.popup_get_file('Select Collection CSV File')
dir = os.path.dirname(fn)

if not fn:
    sys.exit(0)

# load collection csv table
collection = CsvTable(fn)

# add all folder nodes to the dictionary
dict = {}
prev_folder = ""
for row in collection:
    if row['file_location'] != prev_folder:
        add_folder(row,dict)

# create Treedata
folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'

def insert_folder(key,value,parent):
    ''' traverse hierarchical dictionary 
        inserting a treedata node for each entry '''
    treedata.insert(parent,f'{parent}/{key}',key,values=[], icon=folder_icon)
    for k,v in value.items():
        insert_folder(k,v,f'{parent}/{key}')

treedata = sg.TreeData()

# insert dictionary with folders into treedata
for k,v in dict.items():
    insert_folder(k,v,"")

# now insert images in treedata
for row in collection:
    parent = row['file_location']
    v      = row['file_name']
    treedata.insert(parent, f'{parent}/{v}',v,values=[], icon=file_icon)

print(treedata)