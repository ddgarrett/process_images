'''
    Exif Loader

    Load Exif information from image files into a Table object.
    Data to be populated is defined in a metadata Table such as the 
    one defined in "image_collection_metadata.csv"
'''

from __future__ import annotations
import os
import pathlib
import exifread
import hjson  # NOTE: uses hjson instead of json for easier reading json

import PySimpleGUI as sg

from table import Table
from image_collection import ImageCollection
import pi_config as c 
import pi_util as util

class ExifLoader:

    '''
        data_table = table to load exif information into
        metadata   = table columns that are loaded and how to set them
        file_suffix = suffix of files to load
    '''

    @staticmethod
    def new_collection():
        ''' Define a new collection by adding images from a selected 
            directory and its subdirectories.
        '''

        # select directory
        d = sg.popup_get_folder('',no_window=True)
        if not d:
            return None,None

        # don't load if image_collection.csv already exists
        collection_fn = os.path.join(d, "image_collection.csv")
        if os.path.exists(collection_fn):
            msg = f'''
                Collection file already exists: \n 
                "{collection_fn}"\n
                Delete file then retry.
            '''
            sg.popup(msg)
            return None,None

        # load all images in the directory and its subdirectories
        c.status.update(f"Searching for pictures in {d}...")
        c.window.refresh()
        
        table  = ImageCollection(collection_fn)
        loader = ExifLoader(table,c.metadata)
        loader.load_dir(d)

        return table,d

    @staticmethod
    def add_folders():
        ''' Add images to an existing collection,
            searching for new subdirectories of the main directory
            for the currently loaded image collection.
        '''

        # verify that we have a collection loaded
        if c.directory == "":
            msg = f'''
                Collection not yet opened.
            '''
            sg.popup(msg)
            return None,None

        d = c.directory
        c.status.update(f"Searching for new folders in {d}...")
        c.window.refresh()
        
        # collection_fn = os.path.join(d, "image_collection.csv")
        # table  = ImageCollection(collection_fn)
        table = c.table

        # Remove any table filters
        table.filter_rows()

        loader = ExifLoader(table,c.metadata)
        loader.load_dir(d)

        return table,d

    def __init__(self,data_table:Table, metadata_table:Table, 
                 first_file_id:int=1000):
        self._data = data_table
        self._new_row = None
        self._meta = metadata_table

        # IF data_table has rows, set first file ID to highest ID In table
        self._last_fid = first_file_id-1
        rows = data_table.rows()
        if len(rows) > 0:
            last_row = rows[len(rows)-1]
            self._last_fid = last_row.get_int('file_id')

        # convert any array values in exif_tags to arrays
        for row in metadata_table:
            v = row['exif_tags']
            if type(v) == str and v.startswith('['):
                v = hjson.loads(v)
                row.set('exif_tags',v,as_str=False)

    ''' load starting at a directory and traversing all subdirectories  '''
    def load_dir(self,startpath:str):

        adding_dir = False
        if len(self._data.rows()) > 0:
            adding_dir = True

        for root, dirs, files in os.walk(startpath):
            subdir = root.replace(startpath, '')
            dir_path = pathlib.Path(root)
            subdir = subdir.replace('\\','/')

            # skip directories begining with '_'
            if subdir.startswith('/_') or subdir.startswith('$') :
                continue

            # skip if subdir already loaded
            if adding_dir and util.dir_loaded(subdir):
                continue

            for fn in files:
                file_path = dir_path.joinpath(fn)
                sfx = file_path.suffix
                if sfx.lower() in c.IMG_FILE_TYPES:

                    # read the file exif info
                    f = open(file_path, 'rb')
                    tags = exifread.process_file(f, details=False)
                    f.close()

                    if tags == {}:
                        print(f'error reading {f}')

                    # add a few fields of our own
                    self._last_fid += 1
                    tags['sys.next_id']   = self._last_fid
                    tags['sys.subdir']    = subdir
                    tags['sys.file_name'] = fn
                    tags['sys.file_size'] = os.path.getsize(file_path)

                    # load a new row
                    self._new_row = self._data.new_row()
                    self._load_exif(tags)

    ''' load the tag info for one field into the data table
        using load function defined in metadata '''
    def _load_exif(self,tags:dict[str,any]):
        # each row in metadata defines how to extract info
        # from tags and put in data table
        for meta in self._meta:
            col_name  = meta['col_name']
            load_func = meta['load_func']
            exif_tags = meta['exif_tags']
            default   = meta['default']

            data = self._get_exif_data(tags,load_func,exif_tags,default=default)
            self._new_row[col_name] = data

    def _get_exif_data(self,tags:dict[str,any],load_func:str,
                       exif_tags:any,default:str):
        
        load = self._get_default
        if load_func == 'get_key':
            load =  self._get_key
        elif load_func == 'get_lat_lon':
            load = self._get_lat_lon
        elif load_func == 'get_key_value':
            load = self._get_key_value


        return load(tags,exif_tags,default)

    ''' Load Functions '''
    def _get_default(self,tags:dict[str,any],exif_tags:any,default:any):
        return default
    
    ''' if exif_tags is a list, try each tag name in the list  '''
    def _get_key(self,tags:dict[str,any],exif_tags:any,default:any):
        if type(exif_tags) == str:
            return tags.get(exif_tags,default)
        
        for tag in exif_tags:
            if tag in tags:
                return tags[tag]
            
        return default
        
    ''' like _get_key but returns the value instead.
        if exif_tags is a list, try each tag name in the list  '''
    def _get_key_value(self,tags:dict[str,any],exif_tags:any,default:any):
        value = default
        if type(exif_tags) == str:
            value = tags.get(exif_tags,default)
            if value != default:
                value = value.values

        else:    
            for tag in exif_tags:
                if tag in tags:
                    value =  tags[tag].values
                    break
            
        if value != default:
            if type(value) == list and len(value) == 1:
                value = value[0]

        return value
        
    # Get either latitude or longitude.
    # The conversion formula is the same regardless.
    # If the GPS reference is either "S" or "W" we negate the value.
    def _get_lat_lon(self,tags:dict[str,any],exif_tags:list[str],default:any):
        try:
            lat_lon = tags[exif_tags[0]].values
            ref = tags[exif_tags[1]].values

            dec_val = lat_lon[0] + lat_lon[1]/60 + lat_lon[2]/3600
            if ref in ['S','W']:
                dec_val = -dec_val

            return round(float(dec_val),6)
        except KeyError:
            return default
    
if __name__ == "__main__":
    table,d = ExifLoader.new_collection()

    if table:
        table.save()
        sg.popup(f"Table with {len(table)} rows\nsaved at {d}")