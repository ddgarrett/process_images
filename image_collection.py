'''
    Image Collection Table

    Holds data about an image collection as defined by 
    image_collection_metadata.csv

'''
from __future__ import annotations

import PySimpleGUI as sg

import pi_config as c
from csv_table import CsvTable
from table import Row

COL_STATUS_LVL = '_imgcol_status_lvl'
COL_TOOL_TIP   = '_imgcol_tooltip'

# translate a TBD status level to a descriptive name
_tbd_lvl_translate = ('Reject?','Bad?','Dup?','Good?','Best?','???')

class ImageCollection(CsvTable):

    @staticmethod
    def translate_status_lvl(status,level):
        ''' translate status and level into something more human friendly '''
        if status == 'tbd':
            level = _tbd_lvl_translate[int(level)]
        else:
            level = ''

        return [status,level]

    def __init__(self,fn:str,metadata:CsvTable=None):
        if metadata == None:
            metadata = c.metadata

        super().__init__(fn=fn,metadata=metadata)

    def _create_row(self,cols,data=None) -> Row:
        ''' append a new row with default values to the end of self._rows
            and return the new row
        '''
        return ImgColRow(self,cols,data=data)
    
class ImgColRow(Row):

    def get(self,col_name:str) -> any:
        if col_name == COL_STATUS_LVL:
            return self.get_status_lvl()
        
        if col_name == COL_TOOL_TIP:
            return self.get_tooltip()
        
        return super().get(col_name)
    
    def get_status_lvl(self):
        ''' return human readable version of status and level'''
        status = self.get('img_status')
        lvl    = self.get('rvw_lvl')
        return ImageCollection.translate_status_lvl(status,lvl)
    
    def get_tooltip(self):
        ''' return tooltip text for row '''
        status,lvl = self.get_status_lvl()
        name = self.get('file_name')
        return f'{status} {lvl}\n{name}'
    
    def get_hyp_sq(self,row):
        ''' Return the square of the distance between two points in Euclidian geometry.
            This is faster for computer which co-ordinate to cluster a second point with
            and is accurrate for short distances. 
            
            If either row does not have GPS co-ordinates, return -1 '''
        
        s_lat = self['img_lat']
        s_lon = self['img_lon']

        r_lat = row['img_lat']
        r_lon = row['img_lon']

        if r_lat == None or s_lat == None:
            return -1

        return (r_lat-s_lat)**2+(r_lon-s_lon)**2
