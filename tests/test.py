import PySimpleGUI as sg

def key_to_id(tree, key):
    """
    Convert PySimplGUI element key to tkinter widget id.
    : Parameter
      key - key of PySimpleGUI element.
    : Return
      id - int, id of tkinter widget
    """
    dictionary = {v:k for k, v in tree.IdToKey.items()}
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

def increment(tree,key):
    id_ = key_to_id(tree, key)
    if id_:
      v = int(tree.Widget.set(id_, '#1'))
      v += 1
      tree.Widget.set(id_, '#1',str(v))

treedata = sg.TreeData()
treedata.Insert("","_A_","A",[1])
treedata.Insert("","_B_","B",[2])

layout = [[sg.Text('Very Small Tree')],
          [sg.Tree(data=treedata, headings=['Size', ], key='-TREE-')],
          [sg.Button('Ok'), sg.Button('Cancel')]]

window = sg.Window('Tree Element Test', layout, finalize=True)
tree = window['-TREE-']
select(tree, "_B_")
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    
    increment(tree,values['-TREE-'][0])
    print(event, values)

window.close()