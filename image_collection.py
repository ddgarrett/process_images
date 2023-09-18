'''
    Image Collection Table

    Holds data about an image collection as defined by 
    image_collection_metadata.csv

'''
from __future__ import annotations

from operator import itemgetter

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

    def __init__(self,fn:str,metadata:CsvTable=None,
                 renumber=False,audit_folder=False,parent_folder='{dt[0]}-{dt[1]}-{dt[2]}'):
        '''
            Sometimes images do not load in date,time sequence or may have been placed in the wrong 
            parent folder. This is better fixed during the load, but for now these "hacks" have 
            been added. They allow you to resort and renumber the image csv and to test for images 
            in an improper parent folder. NOT IMPLEMENTED is moving images to the proper parent folder.

            Note that the date and time used to create image name on Pixel (Android?) phones is based
            on UTC. Therefore some pictures near begining or end of day may appear as taken on a 
            different day.

            Additional optional parameters:
            renumber - if True, will resort by file_location, img_date_time 
                       then recalculate the file_id (primary key)
            audit_folder - if True will confirm that the parent folder name (file_location)
                       starts with a given pattern. 
            parent_folder - if audit_folder is true, this is the pattern to use in 
                       testing parent folder name. Default is yyyy-mm-dd but for some collections
                       you may want to use parent_folder='{dt[0]}-{dt[1]}' for yyyy-mm groupings
        '''
        if metadata == None:
            metadata = c.metadata

        super().__init__(fn=fn,metadata=metadata)

        # Note any images that are NOT in their correct folder
        # based on parent folder starts with yyyy-mm-dd
        # NOTE: Adjust if parent folder starts with yyyy-mm
        if audit_folder:
            for r in self:
                dt = r['img_date_time']
                loc = r['file_location']

                dt = dt.split(' ')               # [date,time]
                dt = dt[0].split(':')            # [yyyy,mm,dd]
                dt = f'{dt[0]}-{dt[1]}-{dt[2]}'  # 'yyyy-mm-dd'
                loc = loc.split('/')[-1]         # parent folder name
                correct = loc.startswith(dt)

                if not correct:
                    print(loc,dt,r['file_name'])
        
        # Sort by file location and image date time then renumber rows
        if renumber:
            self._rows =  sorted(self._rows,key=itemgetter('file_location','img_date_time'))
            self._original_rows = self._rows

            # now renumber rows
            file_id = 1000
            for row in self:
                row['file_id'] = file_id
                file_id += 1

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
