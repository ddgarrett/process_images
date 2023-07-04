'''
    Process Images Element to Display Images


'''

import os
import PySimpleGUI as sg

import pi_config as c
from pi_element import PiElement
from pi_image_util import is_image_file, cnv_image

class PiImageElem(PiElement):

    def __init__(self,key="-IMAGE-",event="-TREE-"):
        super().__init__(key=key)
        self._event = event
        self._new_size = (400,400)
        self._filename = ''

    def get_element(self) -> sg.Element:
        return sg.Image(key=self.key)

    def handle_event(self, event, values) -> bool:
        if event == self._event:  
            try:
                filename = values[self._event][0]
                full_fn = f'{c.directory}{filename}'   # os.path.join(c.directory, filename)
                if is_image_file(full_fn):
                    self._filename = filename
                    self._update_image(event,values)
            except Exception as e:
                print("exception:",e)

            return False

        # if image display area resized - resize the image and redisplay
        elif event == c.WINDOW_CONFIG:  
            image_size = c.window[self.key].ParentContainer.get_size()

            # wait until resized at least 8 pixels
            if image_size != (1,1) and image_size[1] != None:
                if (abs(image_size[0] - self._new_size[0]) > 8 or
                    abs(image_size[1] - self._new_size[1]) > 8):
                
                    self._new_size = image_size
                    self._update_image(event,values)

            return False
        
    ''' private methods '''

    def _update_image(self,event,values):
        # only update if image file
        fn = f'{c.directory}{self._filename}'
        # fn = os.path.join(c.directory, self._filename)
        fn = fn.replace('\\','/')
        if not is_image_file(fn):
            # print(f"no image: {fn}")
            return
        
        ''' Update the image displayed '''
        thumb,osize = cnv_image(fn, resize=self._new_size)
        c.window[self.key].update(data=thumb)

        c.window.refresh()
        img_size = c.window[self.key].get_size()
        try:
            pct_size = int(round(img_size[0]/osize[0]*100))
            msg = f'{self._filename} at {pct_size}%'
        except Exception as e:
            msg = f'exception during calc of image size: {e}'

        self.update_status(msg)