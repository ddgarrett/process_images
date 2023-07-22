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

    def __init__(self,key="-GALLERY-",event=c.EVT_TREE,cols=3,rows=3):
        super().__init__(key=key)
        #  self._event = event
        self._new_size = (50,50)
        self._collection_rows = [] # rows being displayed
        self._selected_rows = []   # rows selected

        self._rows = rows
        self._cols = cols
        self._page = 0

        c.listeners.add(event,self.files_selected)
        c.listeners.add(c.EVT_WIN_CONFIG,self.resize_image)

        self._pgup_key = f'{self.key}PGUP-'
        self._pgdn_key = f'{self.key}PGDN-'
        self._home_key = f'{self.key}HOME-'
        self._end_key  = f'{self.key}END-'

        c.listeners.add(self._pgdn_key,self._pgup)
        c.listeners.add(self._pgdn_key,self._pgdn)
        c.listeners.add(self._home_key,self._home)
        c.listeners.add(self._end_key,self._end)

        self._menu =  ['', 
            [ StatusMenu(self.get_rows).get_menu(),
             '---',
             PiActionMap(rowget=self.get_rows).item(),
             f'Properties::{c.EVT_FILE_PROPS}',
             'Show',['All','Reject','Bad','Duplicate','Ok','Good','Best','Filter...'],
             f'Save::{c.EVT_FILE_SAVE}',
             f'Exit::{c.EVT_EXIT}' ]]
        
        for i in range(9):
            c.listeners.add((f'{self.key}Thumbnail',i),self.thumb_selected)

    def _img_per_page(self):
        return self._rows * self._cols
    
    def _row_offset(self):
        return self._page * self._img_per_page()
    
    def get_element(self) -> sg.Element:        
        # return [[sg.Image(key=self.key,right_click_menu=self._menu)]]
    
        gap = 3
        thumbnail_width = 50
        width = height  = (thumbnail_width + 4*gap + 4) * self._cols - 4*gap
        size = (thumbnail_width, thumbnail_width)

        layout_thumbnail = []
        for j in range(self._rows):
            temp = []
            for i in range(self._cols):
                pad = ((0, gap), gap) if i == 0 else ((gap, 0), gap) if i == self._cols-1 else (gap, gap)
                frame_layout = [[sg.Image(size=size, pad=(gap, gap), key=(f'{self.key}Thumbnail', j*self._cols+i),
                                          expand_x=True, expand_y=True,enable_events=True,right_click_menu=self._menu)]]
                # frame = sg.Frame(f"{j},{i}", frame_layout,title_location='s',pad=pad, key=("border", j*cols+i), 
                #                  background_color=sg.theme_background_color(),expand_x=True, expand_y=True)
                frame = sg.Frame("", frame_layout, pad=pad, key=(f'{self.key}border', j*self._cols+i), 
                                 background_color=sg.theme_background_color(),expand_x=True, expand_y=True,
                                 element_justification="center")
                temp.append(frame)
            layout_thumbnail.append(temp)

        layout_thumbnail_frame = [
            [sg.Column(layout_thumbnail, expand_x=True, expand_y=True, pad=(0, 0))],
        ]

        layout = [
            [sg.Frame("", layout_thumbnail_frame, size=(width, height), border_width=0,expand_x=True, expand_y=True,key=f'{self.key}gallery_frame')],
            [sg.Text("Page 0", size=0, key='PAGE'), sg.Push(),
             sg.Button('PgUp',key=self._pgup_key), 
             sg.Button('PgDn',key=self._pgdn_key), 
             sg.Button('Home',key=self._home_key), 
             sg.Button('End',key=self._end_key)],
        ]

        return layout
    
    def get_rows(self,values):
        ''' Used by StatusMenu items and PiActionMap to get selected row '''
        return self._selected_rows
    
    ''' Event Handlers '''

    def thumb_selected(self,event,values):
        ''' A single thumb was click on.
            Select or deselect it
        '''
        i = event[1]
        size_img = c.window[event].Size

        frame_widget = c.window[(f'{self.key}border',event[1])].Widget
        fh = frame_widget.winfo_height()
        fw = frame_widget.winfo_width()
        frame_size = (fw,fh)

        widget = c.window[f'{self.key}gallery_frame'].Widget
        full_frame_size = (widget.winfo_width(),widget.winfo_height())

        print(f"thumbsize: {size_img}, thumb framesize: {frame_size}, full frame: {full_frame_size}")

    def _pgup(self,event,values):
        ''' move one page up'''
        if self._page == 0:
            return
        
        self._page -= 1
        self._display_pg()

    def _pgdn(self,event,values):
        ''' move one page down '''
        self._page += 1
        if (self._page-1) * self._img_per_page() > len(self._collection_rows):
            self._page -= 1
        else:
            self._display_pg()

    def _end(self,event,values):
        ''' move to last page '''
        self._page = int(len(self._collection_rows)/self._img_per_page())
        self._display_pg()

    def _home(self,event,values):
        ''' move to firrst page'''
        self._page = 0
        self._display_pg()

    ''' private routines '''
    def _display_pg(self):
        """ display the current page """
        self._update_images()


    def _get_thumb_size(self):
        ''' get thumbnails size based on size of bordering frame '''
        key=f'{self.key}gallery_frame'
        widget = c.window[(f'{self.key}border',0)].Widget

        '''
        parent_sizes = []
        while widget != None:

            parent_sizes.append((widget.winfo_height(),widget.winfo_width()))
            widget = widget.master
        '''
        # print(f"parent sizes: {parent_sizes}")

        gallery_widget = c.window[key].Widget
        fh = gallery_widget.winfo_height()
        fw = gallery_widget.winfo_width()
        pad = 8
        size = (int((fw-12)/3-pad),int((fh-36)/3-pad))
        print(f'thumb size: {size}')
        return size

    def files_selected(self,event,values):
        ''' Display a list of collection rows
         
            Get the list of rows from current table, 
            BUT - may have to make a change to get 
            a filtered list of rows instead?
        '''

        self._collection_rows = []
        self._selected_rows = []
        self._page = 0

        files_folders = values[event]
        rows = c.table.rows()
        if len(rows) > 0 and len(files_folders) > 0:
            filter = SelectedTreeNodesFilter(files_folders)
            self._collection_rows = filter.filter(rows)

        self._update_images()

    def resize_image(self,event,values):
        ''' Based on a __WINDOW CONFIG__ event, see if we need to 
            resize images 
        '''
        thumb_size = self._get_thumb_size()

        # wait until resized at least 8 pixels
        if thumb_size != (1,1) and thumb_size[1] != None:
            if (abs(thumb_size[0] - self._new_size[0]) > 8 or
                abs(thumb_size[1] - self._new_size[1]) > 8):
                print(f'current: {self._new_size}, new: {thumb_size}')
                self._new_size = thumb_size
                self._update_images()

        # report on size of all images
        '''
        thumbnail_sizes = []
        for j in range(self._rows):
            for i in range(self._cols):
                key = (f'{self.key}Thumbnail', j*self._cols+i)
                size = c.window[key].Size
                thumbnail_sizes.append(size)
        '''
        # print(f"thumb sizes: {thumbnail_sizes}")
  
    ''' private methods '''

    def _update_images(self):
        if self._new_size[0] < 16 or self._new_size[1] < 16:
            return
        
        # print(f"gallery: resize elements to {self._new_size}")

        row_nbr = 0
        col_nbr = 0
        # actual_size = []
        for i in range(self._row_offset(),len(self._collection_rows)):
            row = self._collection_rows[i]
            fn = f'{c.directory}{row["file_location"]}/{row["file_name"]}'
            fn = fn.replace('\\','/')

            rotate = int(row['img_rotate'])
            resize_size = (self._new_size[0]-3,self._new_size[1]-3,)
            thumb,osize = cnv_image(fn, resize=resize_size, rotate=rotate)

            key = (f'{self.key}Thumbnail', row_nbr*self._cols+col_nbr)
            c.window[key].update(data=thumb,size=resize_size)
            # print(f'_new_size: {self._new_size}, thumb size: {c.window[key].get_size()}')

            col_nbr += 1
            if col_nbr == self._cols:
                row_nbr += 1
                col_nbr = 0
                if row_nbr == self._rows:
                    break

        while row_nbr < self._rows:
            key = (f'{self.key}Thumbnail', row_nbr*self._cols+col_nbr)
            c.window[key].update(data=None)
            
            col_nbr += 1
            if col_nbr == self._cols:
                row_nbr += 1
                col_nbr = 0

        # magic that makes everything render properly!
        # key=f'{self.key}gallery_frame'
        # c.window[key].Widget.pack() 
        # c.window.refresh()
       