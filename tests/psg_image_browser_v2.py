# image_browser.py

import glob
import PySimpleGUI as sg

from PIL import Image, ImageTk


def parse_folder(path):
    images = glob.glob(f'{path}/*.jpg') + glob.glob(f'{path}/*.png')
    return images

def load_image(path, window):
    try:
        image = Image.open(path)
        image.thumbnail((600, 600)) # originally 400
        photo_img = ImageTk.PhotoImage(image)
        window["image"].update(data=photo_img)
    except:
        print(f"Unable to open {path}!")
        

def main():
    sg.theme('Topanga') # added
    # print( sg.theme_list())
    elements = [
        [
            sg.Text("Image File"),
            sg.Input(size=(25, 1), enable_events=True, key="file"),
            sg.FolderBrowse(),
            sg.Text("       "),
            sg.Button("Prev"),
            sg.Button("Next")        
        ],

        [sg.Image(key="image")]

    ]

    window = sg.Window("Image Viewer", elements, size=(675, 640)) # originally 475
    images = []
    location = 0

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "file":
            images = parse_folder(values["file"])
            if images:
                load_image(images[0], window)
        if event == "Next" and images:
            if location == len(images) - 1:
                location = 0
            else:
                location += 1
            load_image(images[location], window)
        if event == "Prev" and images:
            if location == 0:
                location = len(images) - 1
            else:
                location -= 1
            load_image(images[location], window)

    window.close()


if __name__ == "__main__":
    main()