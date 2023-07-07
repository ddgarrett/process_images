
import PySimpleGUI as sg


data = {
    'First': {
        'Title': 'an inner node',
        'data': ['some data', 'some extra info']},
    'Second': {
        'Title': 'an inner node',
        'data': ['a second piece of data', 'some more info']}
}


def build_treedata(data: dict):
    my_data = sg.TreeData()
    for item in data:
        print(data[item]['Title'])
        my_data.insert(parent='', key=f'{item}', text=item, values=[])
        my_data.insert(parent=f'{item}', key=f'{item}_title', 
                        text=data[item]['Title'], 
                        values=[data[item]['data'][0], data[item]['data'][1]])
    return my_data

def append_to_dict(data: dict, root_name: str, title: str, info: list):
    data[root_name] = {
            'Title': title,
            'data': info}
    print(data)
    return data

initial_treedata = build_treedata(data)

layout = [
    [sg.Tree(data=initial_treedata, headings=['a heading', 'another heading'], key='-TREE-')],
    [sg.Input('Third', key='-root_name-', size=(15, 1))],
    [sg.Input('I added this', key='-title-', size=(10, 1)), sg.Input('very important; info', key='-data-')],
    [sg.Button('Append new data to the Tree', key='-submit-')]
]

window = sg.Window('Try appending this tree!', layout)

while True:
    event, values = window.read()

    if event in [sg.WIN_CLOSED]:
        break

    elif event == '-submit-':
        data = append_to_dict(data, values['-root_name-'], values['-title-'], values['-data-'].split(';'))
        new_treedata = build_treedata(data)
        window['-TREE-'].update(values=new_treedata)


window.close()