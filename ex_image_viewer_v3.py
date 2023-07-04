# img_viewer.py

''' 
    Show a hiearchical list of folders and files with images

    Based on example_image_view.py and PySimpleGUI Demo_Tree_element.py

    Replaced Listbox on left side of screen with Tree
'''

import PIL.Image, PIL.ImageTk
import PySimpleGUI as sg
import os.path

folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'


def cnv_image(file, resize=None):
    ''' Convert a file or byte stream to a Tkinter image.
        If resize value provide, resize the image.
        Return both the Tkinter image and the original image size
    '''
    try:
        img = PIL.Image.open(file)
        osize = img.size
        if resize:
            img.thumbnail(resize)

        return PIL.ImageTk.PhotoImage(img),osize
    except:
        return '',(0,0)

# Window layout in 2 columns

file_list_column = [
    [
        sg.FolderBrowse(target="-FOLDER-"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-",
              expand_x=True)
    ],
    [
        sg.Tree(   data=sg.TreeData(),
                   headings=['TBDs', ],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=5,
                   col0_width=10,
                   key='-TREE-',
                   show_expanded=False,
                   enable_events=True,
                   expand_x=True,
                   expand_y=True,
                   )
    ]
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
    # [sg.Text("Choose an image from list on left:")],
    # [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")]
]

# ----- Full layout -----
layout = [
    [sg.Pane(
        [sg.Column(file_list_column, expand_y=True),
         # sg.VSeperator(),
         sg.Column(image_viewer_column, expand_x=True, expand_y=True, key="-IMGCOL-")],
        orientation='h', relief=sg.RELIEF_SUNKEN, 
        expand_x=True, expand_y=True, k='-PANE-',
        border_width=1, background_color="white")
    ],
    [sg.Text('', relief=sg.RELIEF_SUNKEN,
             size=(55, 1), pad=(0, 3), key='-STATUS-', expand_x=True),
     sg.Sizegrip(pad=(3,3))
    ]
]

window = sg.Window("Image Viewer", layout, size=(600, 400), finalize=True,
                   resizable=True, enable_window_config_events=True)

folder = ''
filename = ''
new_size = (400,400)
osize = (0,0)

def update_status(text):
    window['-STATUS-'].update(text)
    # window.refresh()

    # print("status size:",window['-STATUS-'].get_size())

treedata = sg.TreeData()
image_cnt = 0
folder_cnt = 0

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

def is_image_file(fn):
    return (os.path.isfile(fn) and 
            fn.lower().endswith((".png", ".gif",".jpg","jpeg")))

def update_image(event,values):
    # only update if image file
    if not is_image_file(filename):
        return
    
    ''' Update the image displayed '''
    thumb,osize = cnv_image(filename, resize=new_size)
    window["-IMAGE-"].update(data=thumb)

    window.refresh()
    img_size = window["-IMAGE-"].get_size()
    try:
        pct_size = int(round(img_size[0]/osize[0]*100))
        msg = f'{filename} at {pct_size}%'
    except:
        msg = f'{folder}'

    update_status(msg)

# Run the Event Loop
while True:
    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # Folder selected, make a list of files in the folder
    if event == "-FOLDER-":
        # update_file_list(event,values)
        # print(f"event: {event}, values: {values}")
        starting_path = values['-FOLDER-']
        update_status(f"Searching for pictures in {starting_path}...")
        window.refresh()
        image_cnt = 0
        folder_cnt = 0
        treedata = sg.TreeData()
        add_files_in_folder('', starting_path)
        window['-TREE-'].update(values=treedata)
        update_status(f"loaded {image_cnt} pictures & {folder_cnt} folders from {starting_path}")

    # A file was chosen from the listbox - show image
    elif event == "-TREE-":  
        try:
            # print(f"event: {event}, values: {values}")
            fn = values['-TREE-'][0]
            if is_image_file(fn):
                filename = fn
                update_image(event,values)
        except Exception as e:
            print("exception:",e)


    # image display area resized - resize the image and redisplay
    elif event == "__WINDOW CONFIG__":  
        # image_size = window["-IMGCOL-"].get_size()
        # resize the image to the size of the parent container
        image_size = window["-IMAGE-"].ParentContainer.get_size()
        # print(f'parent=="-IMGCOL-": {window["-IMGCOL-"] == window["-IMAGE-"].ParentContainer}')

        # wait until resized at least 8 pixels
        if image_size != (1,1) and image_size[1] != None:
            if (abs(image_size[0] - new_size[0]) > 8 or
                abs(image_size[1] - new_size[1]) > 8):
            
                new_size = image_size
                update_image(event,values)

                # print(f'imgcol.size: {image_size}, parent.size: {}')
    else:
        print(f"unrecognized event: {event}, values: {values}")

window.close()