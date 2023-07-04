'''
    General utility functions for Process Images System

'''
import os

import PIL.Image, PIL.ImageTk

def is_image_file(fn) -> bool:
    ''' Return true if the file for fn is an image file '''
    return (os.path.isfile(fn) and 
            fn.lower().endswith((".png", ".gif",".jpg","jpeg")))

def cnv_image(file, resize=None):
    ''' Convert a file or byte stream to a Tkinter image.
        If resize value provide, resize the image.
        Return both the Tkinter image and the original image size.
    '''
    try:
        img = PIL.Image.open(file)
        osize = img.size
        if resize:
            img.thumbnail(resize)

        return PIL.ImageTk.PhotoImage(img),osize
    except:
        return '',(0,0)
