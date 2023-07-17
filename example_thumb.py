from io import BytesIO
from pathlib import Path
from PIL import Image,ImageTk
import PySimpleGUI as sg
import os

from pi_image_util import cnv_image

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
        self._size = size

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

    def _resize(self, file, size):
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

    def resize(self,file,size):
        thumb,osize = cnv_image(file, resize=size)
        return thumb

    def load_thumbnails(self):
        files = self.paths[self.page] if self.pages !=0 else []
        for i in range(self.thumbnails):
            if i < len(files):
                # data, color = self.resize(files[i][0], self._size[0]), bg[files[i][1]]
                data, color = self.resize(files[i][0], self._size), bg[files[i][1]]
            else:
                data, color = '', bg[False]

            self.window[("Thumbnail", i)].update(data=data, size=self._size)
            # fn = files[i][0].replace('\\','/')
            # _,_,fn = fn.rpartition('/')
            # self.window[("border", i)].Widget.configure(text=fn)
            # self.window[("border", i)].Widget.configure(bg=color)

    def resize_view(self,event,values):
        ''' Calculate thumb size then load thumbnails '''
        parent = self.window[("Thumbnail", 0)].ParentContainer
        image_size = parent.get_size()
        parent_parent = parent.ParentContainer
        pp_size = parent_parent.get_size()

        parent_max = (int((pp_size[0]-6)/3),int((pp_size[1]-6)/3))
        if parent_max[0] > 0 and parent_max[1] > 0:
            if image_size[0] > parent_max[0] or image_size[1] > parent_max[1]:
                print(f'adjusting image size from {image_size} to {parent_max}')
                # image_size = parent_max
                image_size = (parent_max[0],parent_max[1])

        # print(f'my size: {self._size}, parent: {image_size} ({type(parent)}), parent parent: {pp_size} ({type(parent_parent)})')

        max_parent = parent_parent
        # wait until resized at least 8 pixels
        if image_size != (1,1) and image_size[1] != None:
            if (abs(image_size[0] - self._size[0]) > 16 or
                abs(image_size[1] - self._size[1]) > 16):
                print(f'parent size: {image_size}, my size: {self._size}')
                self._size = (image_size[0] - 10, image_size[1] - 10)
                self.load_thumbnails()


font = ("Courier New", 11)
# sg.theme("DarkBlue3")
sg.theme("black")
# sg.set_options(font=font, dpi_awareness=True)

gap = 3
cols = rows = 3
thumbnail_width = 150
width = height  = (thumbnail_width + 4*gap + 4) * cols - 4*gap
size = (thumbnail_width, thumbnail_width)
bg = {True:'yellow', False:sg.theme_background_color()}
default_folder = r'C:\Users\doug\Documents\projects\img\2023-05-17'

layout_thumbnail = []
for j in range(rows):
    temp = []
    for i in range(cols):
        pad = ((0, gap), gap) if i == 0 else ((gap, 0), gap) if i == cols-1 else (gap, gap)
        frame_layout = [[sg.Image(size=size, pad=(gap, gap), key=("Thumbnail", j*cols+i),expand_x=True, expand_y=True,enable_events=True)]]
        # frame = sg.Frame(f"{j},{i}", frame_layout,title_location='s',pad=pad, key=("border", j*cols+i), background_color=sg.theme_background_color(),expand_x=True, expand_y=True)
        frame = sg.Frame("", frame_layout, title_location='s', pad=pad, key=("border", j*cols+i), background_color=sg.theme_background_color(),expand_x=True, expand_y=True)
        temp.append(frame)
    layout_thumbnail.append(temp)

layout_thumbnail_frame = [
    [sg.Column(layout_thumbnail, expand_x=True, expand_y=True, pad=(0, 0))],
]

layout = [
    [sg.Input(default_folder, size=10, disabled=True, expand_x=True, key='Directory'),
     sg.Button('Browse')],
    [sg.Frame("", layout_thumbnail_frame, size=(width, height), border_width=0,expand_x=True, expand_y=True)],
    [sg.Text("Page 0", size=0, key='PAGE'), sg.Push(),
     sg.Button('PgUp'), sg.Button('PgDn'), sg.Button('Home'), sg.Button('End'),sg.Sizegrip(pad=(3,3))],
]

window = sg.Window('PNG Thumbnail Viewer', layout, finalize=True,resizable=True, 
                   enable_window_config_events=True, return_keyboard_events=True)

view = View(window, cols, rows)
view.load_files(default_folder)
view.load_thumbnails()

window.bind("<Control-KeyPress>",'-CTRL_DOWN-')

default_bg =  window[('Thumbnail',0)].Widget.cget('bg')
print(f'bg: {type(default_bg)}')

while True:

    event, values = window.read()
    el_focus = window.find_element_with_focus()
    if el_focus != None:
        el_focus = el_focus.Key
    print(f'focus: {el_focus}, event: {event}, values: {values}')
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
    elif event == '__WINDOW CONFIG__':
        view.resize_view(event,values)
    elif type(event) == tuple and event[0] == 'Thumbnail':
        # set focus to a thumbnail image
        widget = window[event].Widget
        window[event].set_focus()
        # widget.focus_set()
        bg = widget.cget('bg')
        if bg == default_bg :
            bg = '#FFFFFF'
        else:
            bg = default_bg

        window[event].Widget.config(bg=bg)
        parent = window[event].ParentContainer
        print(type(parent.Widget))
        # parent.Widget.config(bg=bg)

    
    window['PAGE'].update(f'Page {view.page}')

window.close()