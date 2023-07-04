
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
        d = {"":[]}
        dict[key] = d

    idx += 1
    return add_path(dict[key],nodes,idx)


def add_file(row,data):
    loc = row['file_location']
    name = row['file_name']

    nodes = loc.split('/')

    # print(nodes)
    fnode = add_path(data,nodes,1) # skip first node - it's just an empty string
    if not '' in fnode:
        fnode[''] = [name]
    else:
        fnode[''].append(name)


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


def traverse_dict(key,value,indent,parent):
    ''' traverse a dictionary printing an indented
        representation 
    '''
    indent += 4
    if key == '':
        for v in value:
            print(f"parent:{parent}, fullname:{parent}/{v}, f:{v}")
            # print(' '*indent,v)
    else:
        # print(' '*indent,key)
        print(f"parent:{parent}, fullname:{parent}/{key}, f:{key}")
        for k,v in value.items():
            traverse_dict(k,v,indent,f'{parent}/{key}')

for k,v in data.items():
    traverse_dict(k,v,-4,dir)

# print(data)