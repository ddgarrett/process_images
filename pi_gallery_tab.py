'''
    Tab subclass which supports display of a list of photos.

    Checks for event == "-TREE-"
    Then gets the photo names from values['-TREE-']

'''
from pi_tab import PiTab
from pi_config import window
from pi_image_util import is_image_file, cnv_image


class GalleryTab(PiTab):
    ''' Tab to show a list of images
      
        List can be a list of selected images
        or a directory with one or more images

        TODO: add parms for number across, so gallery can be enlarged.
    '''

    ''' Overridden methods '''
    def __init__(self, **kwargs):
        self._file_names = []

    def handle_event(self,event,values) -> bool:

        if super().handle_event(event,values):
            return True
        
        if event == "-TREE-":
            self._file_names = values['-TREE-']
            self._update_gallery()
        
        return False

    def _select(self,event,values):
        ''' React to a select event '''
        super().select(event,values)

        # double check that superclass did set selected
        # and we have an image file
        if self.is_selected():
            self._update_gallery()
            
    def _update_gallery(self):
        if self.is_selected():
            print("update gallery goes here...")