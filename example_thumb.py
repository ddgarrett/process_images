from io import BytesIO
from pathlib import Path
from PIL import Image
import PySimpleGUI as sg
import os

EXTS = ('png', 'jpg', 'jpeg', 'gif')

class View():

    def __init__(self, window, cols, rows):
        self.window = window
        self.path = None
        self.cols = 6
        self.rows = 6
        self.thumbnails = cols * rows
        self.pathes = []
        self.pages = 0
        self.page = 0

    def load_files(self, folder, pattern='*.png'):
        path = Path(folder)
        if folder and path.is_dir():
            files = [os.path.join(folder, f) for f in os.listdir(folder) if True in [f.lower().endswith(e) for e in EXTS]]
            files.sort()
            # files = list(map(lambda file:str(file), path.glob(pattern)))
        else:
            files = []
        self.paths, temp = [], []
        self.images = len(files)
        for i, filename in enumerate(files):
            temp.append((filename, False))
            if (i % self.thumbnails == self.thumbnails-1) or (i == self.images - 1):
                    self.paths.append(temp)
                    temp = []
        self.folder = folder
        self.pages = len(self.paths)
        self.page = 0

    def resize(self, file, size):
        #try:
        im = Image.open(file)
        w, h = im.size
        if w >= h:
            new_size = (size, int(size/w*h))
        else:
            new_size = (int(size/h*w), size)
        new_im = im.resize(new_size)
        with BytesIO() as buffer:
            if new_im.mode == 'RGBA':
                new_im.save(buffer, format="ppm")
            else:
                new_im.save(buffer, format="png")
            data = buffer.getvalue()
        #except:
        #    data = None
        return data

    def load_thumbnails(self):
        files = self.paths[self.page] if self.pages !=0 else []
        for i in range(self.thumbnails):
            if i < len(files):
                data, color = self.resize(files[i][0], thumbnail_width), bg[files[i][1]]
            else:
                data, color = '', bg[False]
            self.window[("Thumbnail", i)].update(data=data, size=size)
            self.window[("border", i)].Widget.configure(bg=color)

font = ("Courier New", 11)
# sg.theme("DarkBlue3")
sg.theme("black")
# sg.set_options(font=font, dpi_awareness=True)

gap = 3
cols = rows = 4
thumbnail_width = 90
width = height  = (thumbnail_width + 4*gap + 4) * cols - 4*gap
size = (thumbnail_width, thumbnail_width)
bg = {True:'yellow', False:sg.theme_background_color()}
default_folder = r'C:\Users\doug\Documents\projects\img\2023-05-17'

layout_thumbnail = []
for j in range(rows):
    temp = []
    for i in range(cols):
        pad = ((0, gap), gap) if i == 0 else ((gap, 0), gap) if i == cols-1 else (gap, gap)
        frame_layout = [[sg.Image(size=size, pad=(gap, gap), key=("Thumbnail", j*cols+i))]]
        frame = sg.Frame("", frame_layout, pad=pad, key=("border", j*cols+i), background_color=sg.theme_background_color())
        temp.append(frame)
    layout_thumbnail.append(temp)

layout_thumbnail_frame = [
    [sg.Column(layout_thumbnail, expand_x=True, expand_y=True, pad=(0, 0))],
]

layout = [
    [sg.Input(default_folder, size=10, disabled=True, expand_x=True, key='Directory'),
     sg.Button('Browse')],
    [sg.Frame("", layout_thumbnail_frame, size=(width, height), border_width=0)],
    [sg.Text("Page 0", size=0, key='PAGE'), sg.Push(),
     sg.Button('PgUp'), sg.Button('PgDn'), sg.Button('Home'), sg.Button('End'),],
]

window = sg.Window('PNG Thumbnail Viewer', layout, finalize=True)

view = View(window, cols, rows)
view.load_files(default_folder)
view.load_thumbnails()

while True:

    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'PgDn':
        if view.page < view.pages - 1:
            view.page += 1
            view.load_thumbnails()
    elif event == 'PgUp':
        if view.page > 0:
            view.page -= 1
            view.load_thumbnails()
    elif event == 'Home':
        if view.page != 0:
            view.page = 0
            view.load_thumbnails()
    elif event == 'End':
        if view.page != view.pages - 1:
            view.page = view.pages - 1
            view.load_thumbnails()
    elif event == 'Browse':
        folder = sg.popup_get_folder('', no_window=True, modal=True)
        if folder:
            view.load_files(folder)
            view.load_thumbnails()
    window['PAGE'].update(f'Page {view.page}')

window.close()