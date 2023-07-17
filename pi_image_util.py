'''
    General utility functions for Process Images System

'''
import os

import PIL.Image, PIL.ImageTk

def is_image_file(fn) -> bool:
    ''' Return true if the file for fn is an image file '''
    if fn:
        return (os.path.isfile(fn) and 
                fn.lower().endswith((".png", ".gif",".jpg","jpeg")))
    return False

def cnv_image(file, resize=None, rotate=1):
    ''' Convert a file or byte stream to a Tkinter image.
        If resize value provide, resize the image.
        Return both the Tkinter image and the original image size.
    '''
    try:
        img = PIL.Image.open(file)

        if rotate > 1:
            if rotate == 3:
                img=img.rotate(180, expand=True)
            elif rotate == 6:
                img=img.rotate(270, expand=True)
            elif rotate == 8:
                img=img.rotate(90, expand=True)
    
        osize = img.size
        if resize:
            img.thumbnail(resize)

        return PIL.ImageTk.PhotoImage(img),osize
    except Exception as e:
        print(f"image util exception: {e}")
        return '',(0,0)
