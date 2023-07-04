'''
    Tab subclass which supports display of single photo.

    Checks for event == "-TREE-"
    Then gets the photo hame from values['-TREE-'][0]

    TODO: add zoom in and zoom out?

'''
import PySimpleGUI as sg

from pi_tab import PiTab
from pi_config import window
import pi_image_util as util


class PhotoTab(PiTab):
    ''' Tab to show a single image  '''

    ''' Overridden methods '''
    def __init__(self, **kwargs):
        self._filename = None

        self._folder = "TODO: set folder value"

    def handle_event(self,event,values) -> bool:

        if super().handle_event(event,values):
            return True
        
        if event == "-TREE-":
            fn = values['-TREE-'][0]
            if util.is_image_file(fn):
                self._filename = fn
                if self.is_selected():
                    self._update_image(fn)
        
        return False

    def _select(self,event,values):
        ''' React to a select event '''
        super().select(event,values)

        # double check that superclass did set selected
        # and we have an image file
        if self.is_selected() and util.is_image_file(self._filename):
            self._update_image()
            
    def get_element(self):
        return [sg.Image(key=self._global_id("-IMAGE-"))]
    
    ''' Class Specific Methods '''
    def _update_image(self):
        if not self.is_selected():
            return
        
        ''' Update the image displayed '''
        thumb,osize = util.cnv_image(self._filename, resize=(100,100))
        window[self._global_id("-IMAGE-")].update(data=thumb)

        window.refresh()
        img_size = window["-IMAGE-"].get_size()
        try:
            pct_size = int(round(img_size[0]/osize[0]*100))
            msg = f'{self._filename} at {pct_size}%'
        except:
            msg = f'{self._folder}'

        # update_status(msg)