
import sys
import os

import PySimpleGUI as sg
from csv_table import CsvTable

def add_path(dict,nodes,idx):
    ''' if idx < len(nodes), 
           - ensure nodes[idx] is in the dictionary
           - recursive call to insure remaining nodes also in dictionary

        return the dictionary for the last node
    '''
    if idx >= len(nodes):
        return dict
    
    key = nodes[idx]
    if not key in dict:
        # d = {"":[]}
        # dict[key] = d
        dict[key] = {}

    idx += 1
    return add_path(dict[key],nodes,idx)


def add_file(row,data):
    loc = row['file_location']
    name = row['file_name']

    nodes = loc.split('/')

    # print(nodes)
    fnode = add_path(data,nodes,1) # skip first node - it's just an empty string
    '''
    if not '' in fnode:
        fnode[''] = [name]
    else:
        fnode[''].append(name)
    '''


''' Add all rows in the collection to the dictionary '''
fn = sg.popup_get_file('Select Collection CSV File')
dir = os.path.dirname(fn)

if not fn:
    sys.exit(0)

print(fn)
# collection = CsvTable('C:/Users/doug/Documents/projects/img/image_collection.csv')
collection = CsvTable(fn)
data = {}
for row in collection:
    add_file(row,data)

folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'

def traverse_dict(key,value,indent,parent):
    ''' traverse a dictionary printing an indented
        representation 
    '''
    indent += 4
    if key == '':
        for v in value:
            # print(f"parent:{parent}, fullname:{parent}/{v}, f:{v}")
            treedata.insert(parent, f'{parent}/{v}',v,values=[], icon=file_icon)
            # print(' '*indent,v)
    else:
        # print(' '*indent,key)
        # print(f"parent:{parent}, fullname:{parent}/{key}, f:{key}")
        # print(f"insert: {parent}, '{parent}/{key}, {key}")
        treedata.insert(parent,f'{parent}/{key}',key,values=[], icon=folder_icon)
        for k,v in value.items():
            traverse_dict(k,v,indent,f'{parent}/{key}')

treedata = sg.TreeData()
# treedata.insert("",dir,"collection",values=[],icon=folder_icon)

# insert data in treedata
for k,v in data.items():
    traverse_dict(k,v,-4,"")

# now insert images in treedata
for row in collection:
    parent = row['file_location']
    v      = row['file_name']
    treedata.insert(parent, f'{parent}/{v}',v,values=[], icon=file_icon)

print(treedata)