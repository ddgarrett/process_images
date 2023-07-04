# img_viewer.py

''' 
    from https://realpython.com/pysimplegui-python/#creating-a-pysimplegui-image-viewer 

    Added logic to resize images and convert to png for display in PySimpleGUI.

    This includes:
    1. make file list selection "extended" mode
    2. make pane split resizable
    3. make window resizable
    4. have images resize accordingly
    5. have images resized to size of elements
    6. add status line to show image name and percent scaling
'''

import PIL.Image, PIL.ImageTk
import PySimpleGUI as sg
import os.path

def cnv_image(file, resize=None):
    ''' 
        Given a file name, path or byte string, convert the image 
        to a format suitable for Tkinter.
        Optionally resize the image. The PIL thumbnail function is used to resize 
        the image therefore the image will never be larger than its original size.
        Return Tkiner image and original size of image.
    '''
    try:
        img = PIL.Image.open(file)
        osize = img.size
        if resize:
            img.thumbnail(resize)

        return PIL.ImageTk.PhotoImage(img),osize
    except:
        return None,(0,0)


# First the window layout in 2 columns

file_list_column = [
    [
        sg.FolderBrowse(target="-FOLDER-"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-",
              expand_x=True)
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, key="-FILE LIST-", 
            # size=(40, 20)
            expand_y=True, expand_x=True, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED
        )
    ],
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
    [sg.Text('Status Bar', relief=sg.RELIEF_SUNKEN,
             size=(55, 1), pad=(0, 3), key='-STATUS-', expand_x=True),
     sg.Sizegrip(pad=(3,3))
    ]
]

window = sg.Window("Image Viewer", layout, size=(600, 400), finalize=True,
                   resizable=True, enable_window_config_events=True)

folder = None
filename = None
new_size = (400,400)
osize = (0,0)

def update_status(text):
    window['-STATUS-'].update(text)

def update_file_list(evnt,values):
    ''' Update the list of files shown after a folder is selected '''
    global filename, folder
    folder = values["-FOLDER-"]
    try:
        # Get list of files in folder
        file_list = os.listdir(folder)
    except:
        file_list = []

    fnames = [
        f
        for f in file_list
        if os.path.isfile(os.path.join(folder, f))
        and f.lower().endswith((".png", ".gif",".jpg","jpeg"))
    ]

    window["-FILE LIST-"].update(fnames)

    if len(fnames) > 0:
        filename = f'{folder}/{fnames[0]}'
        update_image(event,values)
    else:
        filename = None
        window["-IMAGE-"].update(data=None)
        update_status(f'{folder}')


def update_image(event,values):
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
        update_file_list(event,values)

    # A file was chosen from the listbox - show image
    elif event == "-FILE LIST-":  
        try:
            filename = os.path.join( values["-FOLDER-"], values["-FILE LIST-"][0])
            update_image(event,values)
        except Exception as e:
            print("exception:",e)

    # image display area resized - resize the image and redisplay
    elif event == "__WINDOW CONFIG__":  
        image_size = window["-IMGCOL-"].get_size()

        # wait until resized at least 8 pixels
        if image_size != (1,1) and image_size[1] != None:
            if (abs(image_size[0] - new_size[0]) > 8 or
                abs(image_size[1] - new_size[1]) > 8):
            
                new_size = image_size
                update_image(event,values)
    else:
        print(f"unrecognized event: {event}, values: {values}")

window.close()