'''
    Process Images Element to Display a Gallery of Images


'''

import os
import PySimpleGUI as sg
from pi_action_map import PiActionMap

import pi_config as c
from pi_element import PiElement
from pi_filters import SelectedTreeNodesFilter
from pi_image_util import is_image_file, cnv_image
from status_menu import StatusMenu
from status_menu_item import StatusMenuItem
from pi_util import get_row_for_fn

class PiGalleryElem(PiElement):

    def __init__(self,key="-IMAGE-",event=c.EVT_TREE,cols=3,rows=3):
        super().__init__(key=key)
        #  self._event = event
        self._new_size = (400,400)
        self._collection_rows = []
        self._selected_rows = []

        self._rows = rows
        self._cols = cols

        c.listeners.add(event,self.files_selected)
        c.listeners.add(c.EVT_WIN_CONFIG,self.resize_image)

        self._menu =  ['', 
            [ StatusMenu(self.get_rows).get_menu(),
             '---',
             PiActionMap(rowget=self.get_rows).item(),
             f'Properties::{c.EVT_FILE_PROPS}',
             'Show',['All','Reject','Bad','Duplicate','Ok','Good','Best','Filter...'],
             f'Save::{c.EVT_FILE_SAVE}',
             f'Exit::{c.EVT_EXIT}' ]]

    def get_element(self) -> sg.Element:        
        # return [[sg.Image(key=self.key,right_click_menu=self._menu)]]
    
        gap = 3
        thumbnail_width = 50
        width = height  = (thumbnail_width + 4*gap + 4) * self._cols - 4*gap
        size = (thumbnail_width, thumbnail_width)
        bg = {True:'yellow', False:sg.theme_background_color()}

        layout_thumbnail = []
        for j in range(self._rows):
            temp = []
            for i in range(self._cols):
                pad = ((0, gap), gap) if i == 0 else ((gap, 0), gap) if i == self._cols-1 else (gap, gap)
                frame_layout = [[sg.Image(size=size, pad=(gap, gap), key=("Thumbnail", j*self._cols+i),
                                          expand_x=True, expand_y=True,enable_events=True,right_click_menu=self._menu)]]
                # frame = sg.Frame(f"{j},{i}", frame_layout,title_location='s',pad=pad, key=("border", j*cols+i), 
                #                  background_color=sg.theme_background_color(),expand_x=True, expand_y=True)
                frame = sg.Frame("", frame_layout, title_location='s', pad=pad, key=("border", j*self._cols+i), 
                                 background_color=sg.theme_background_color(),expand_x=True, expand_y=True)
                temp.append(frame)
            layout_thumbnail.append(temp)

        layout_thumbnail_frame = [
            [sg.Column(layout_thumbnail, expand_x=True, expand_y=True, pad=(0, 0))],
        ]

        layout = [
            [sg.Frame("", layout_thumbnail_frame, size=(width, height), border_width=0,expand_x=True, expand_y=True)],
            [sg.Text("Page 0", size=0, key='PAGE'), sg.Push(),
             sg.Button('PgUp'), sg.Button('PgDn'), sg.Button('Home'), sg.Button('End')],
        ]

        return layout
    
    def get_rows(self,values):
        ''' Used by StatusMenu items and PiActionMap to get selected row '''
        return self._selected_rows
    
    ''' Event Handlers '''

    def files_selected(self,event,values):
        ''' Display a list of selected table rows
         
            Get the list of rows from current table, 
            BUT - may have to make a change to get 
            a filtered list of rows instead?
        '''

        self._collection_rows = []
        self._selected_rows = []
        self._current_page = 0

        files_folders = values[event]
        rows = c.table.rows()
        if len(rows) == 0 or len(files_folders) == 0:
            return
        
        filter = SelectedTreeNodesFilter(files_folders)
        self._collection_rows = filter.filter(rows)
        self._update_images()

    def resize_image(self,event,values):
        ''' Resize image based on parent size '''
        image_size = c.window[self.key].ParentContainer.get_size()

        # wait until resized at least 8 pixels
        if image_size != (1,1) and image_size[1] != None:
            if (abs(image_size[0] - self._new_size[0]) > 8 or
                abs(image_size[1] - self._new_size[1]) > 8):
                self._new_size = image_size
                self._update_images()
  
    ''' private methods '''

    def _update_images(self):
        print(f"gallery: resize elements to {self._new_size}")
        return
        if not self._filename:
            c.window[self.key].update(data=None)
            c.window.refresh()
            return
    
        fn = f'{c.directory}{self._filename}'
        fn = fn.replace('\\','/')

        ''' Update the image displayed '''
        rotate = int(self._collection_row['img_rotate'])
        thumb,osize = cnv_image(fn, resize=self._new_size, rotate=rotate)
        c.window[self.key].update(data=thumb)
        c.window.refresh()

        img_size = c.window[self.key].get_size()
        try:
            pct_size = int(round(img_size[0]/osize[0]*100))
            msg = f'{self._filename} at {pct_size}%'
        except Exception as e:
            msg = f'exception during calc of image size: {e}'

        c.update_status(msg)

        