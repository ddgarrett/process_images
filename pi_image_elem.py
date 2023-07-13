'''
    Process Images Element to Display Images


'''

import os
import PySimpleGUI as sg

import pi_config as c
from pi_element import PiElement
from pi_image_util import is_image_file, cnv_image
from status_menu_item import StatusMenuItem
from pi_util import get_row_for_fn

class PiImageElem(PiElement):

    def __init__(self,key="-IMAGE-",event=c.EVT_TREE):
        super().__init__(key=key)
        # self._event = event
        self._new_size = (400,400)
        self._filename = ''
        self._collection_row = None

        c.listeners.add(event,self.file_selected)
        c.listeners.add(c.EVT_WIN_CONFIG,self.resize_image)

    def get_element(self) -> sg.Element:
        menu = ['', 
            [f'Map::{c.EVT_ACT_MAP}', 
             'Review As...',[
                 StatusMenuItem('Reject',c.STAT_REJECT,c.LVL_INITIAL,self.get_row).item(), 
                 StatusMenuItem('Bad Quality',c.STAT_QUAL_BAD,c.LVL_QUAL,self.get_row).item(),
                 StatusMenuItem('Duplicate',c.STAT_DUP,c.LVL_DUP,self.get_row).item(),
                 StatusMenuItem('Just Okay',c.STAT_OK,c.LVL_OK,self.get_row).item(),
                 StatusMenuItem('Good',c.STAT_GOOD,c.LVL_GOOD,self.get_row).item(),
                 StatusMenuItem('Best!',c.STAT_BEST,c.LVL_BEST,self.get_row).item()],
             'TBD - Possible...',[
                 StatusMenuItem('Reject',c.STAT_TBD,c.LVL_INITIAL,self.get_row).item(),
                 StatusMenuItem('Bad Quality',c.STAT_TBD,c.LVL_QUAL,self.get_row).item(),
                 StatusMenuItem('Duplicate',c.STAT_TBD,c.LVL_DUP,self.get_row).item(),
                 StatusMenuItem('Ok Good Best',c.STAT_TBD,c.LVL_OK,self.get_row).item(),
                 StatusMenuItem('Good or Best',c.STAT_TBD,c.LVL_GOOD,self.get_row).item()
                 ],
            ]]
        return [[sg.Image(key=self.key,right_click_menu=menu)]]
    
    def get_row(self,values):
        return [self._collection_row]
    
    ''' Event Handlers '''

    def file_selected(self,event,values):
        fn_list = values[event]
        if len(fn_list) == 0:
            fn = None
        else:
            fn = values[event][-1]
            full_fn = f'{c.directory}{fn}'
            if not is_image_file(full_fn):
                fn = None

        self._filename = fn
        if fn:
            self._collection_row = get_row_for_fn(fn)
        else:
            self._collection_row = None
            
        self._update_image()

    def resize_image(self,event,values):
        image_size = c.window[self.key].ParentContainer.get_size()

        # wait until resized at least 8 pixels
        if image_size != (1,1) and image_size[1] != None:
            if (abs(image_size[0] - self._new_size[0]) > 8 or
                abs(image_size[1] - self._new_size[1]) > 8):
                self._new_size = image_size
                self._update_image()
  
    ''' private methods '''

    def _update_image(self):
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

        self.update_status(msg)

        