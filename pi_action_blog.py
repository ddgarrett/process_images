'''
    Generate skeleton blog entries for  selected files 

    Listens for event names generated when this action was created.

    Like all actions, this class has a 'handle_event(self,event,values)' method.

    When a new instance of this class is created:
        text   - menu item text to display
        rowget - method to call to get list of rows to export

    To use, simply create a new instance with the name of the event
    and the key of the list within event values. For example:

        # set up action for Export Event and Tree List 
        PiActionBlog(rowget=self.get_selected_rows).item(),
'''
import os
from pathlib import Path
import shutil

import pi_config as c
from pi_action import PiAction

class PiActionBlog(PiAction):
    '''
        Generate skeleton blog entries for selected files and folders.
        Parms:
        text   - menu item text to display
        rowget - method to call to get list of rows to export
    '''

    last_id = 0  # for generating unique Event IDs

    @classmethod
    def next_id(cls):
        cls.last_id += 1
        return cls.last_id
    
    @staticmethod
    def get_header():
        ''' Return a string with the blog header html '''
        
        return ''' 
            <!--- intro paragraph(s)  --->
            <p>
            {intro}
            </p>
        '''
    @staticmethod
    def get_body(row):
        ''' Return the blog body for a single row '''
        return f'''
            <!----- image and paragraph(s) describing picture -->
            <p id="{row['file_name']}">
            {{image_intro_paragraph}}
            </p>
            <br>
            <div class="separator" style="clear: both; text-align: center;">
            <a href="{{album}}" target="_blank">
            <figure> 
                <!-- image height or width at 500 - manually override -->
                <!----- image {row['file_name']} -->



            <figcaption>{{image_caption}}</figcaption>
            </figure> 
            </a></div>

            <p> <!--- optional - delete if not needed -->
            {{image_extended_description}} 
            </p>
            '''

    @staticmethod
    def get_footer():
         ''' Return a string with blog footer html '''

         return '''
            <!--- final link to album --->
            <p>
            <a href="{album}" target="_blank">Click this link or one of the pictures above to see more pictures in the  {album_name} photo album</a></p>
            <br>
            '''

    def __init__(self,text="Generate Blog",rowget=None,fn="blog.html"):
        self._id = self.next_id()
        self._text = text
        self._rowget = rowget
        self._fn = fn
        super().__init__(event=self._get_event())

    def _get_event(self):
        return f'-PiActionBlog{self._id}-'

    def item(self):
        ''' return an item name and unique event id'''
        return f'{self._text}::{self._get_event()}'

    def handle_event(self,event,values):
        ''' Handle Export Event - get list of rows and copy
            those images to _export subdirectory. '''

        fn = f'{c.directory}/{self._fn}'
        print("filename: ",fn)
        with open(fn,'w',encoding="utf-8") as f:
            f.write(self.get_header())

            for row in self._rowget(values):
                f.write(self.get_body(row))

            f.write(self.get_header())