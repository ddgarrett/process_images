'''
    Table Filter classes and subclasses.

    Does not affect the table being filtered.
    Instead it returns a list of rows which match the filter
    conditions.

    The review process, levels and statuses include:
    1. Initial review to filter out obvious not wanted pictures.
        - current level = '0' and status = 'tbd' 
        - if rejected, level left at 0 and status set to 'reject'
        - if accepted, level set to '1' and status left at 'tbd'

    2. Quality review to weed out images with technical issues such
       as blurry, poor composition, portraits with eyes closed.
       - current level = '1' and status = 'tbd'
       - if rejected, level left at '1' and status set to 'bad'
       - if acceptec, level set to '2' and status left at 'tbd'

    3. Duplicate Review to choose the best of multiple images that
       are duplicates or very similar.
       - current level = '2' and status = 'tbd'
       - if not chosen, level left at '2' and status set to 'dup'
       - if chosen, level set to '3' and status left at 'tbd'

    4. Selected Review to choose the pictures good enough to show
       others without boring them. Around 10% of total number of
       pictures.
       - current level = '3' and status = 'tbd'
       - if not chosen, level left at '3' and status set to 'ok'
       - if chosen, level set to '4' and status left at 'tbd'

    5. Best of Best review. These are the few (maybe 1% of total)
       that you'd show to really "wow" people. Also show people who 
       have little patience for looking at your photos.
       - current level = '4' and status = 'tbd'
       - if not chosen, level left at '4' and status set to 'good'
       - if not chosen, level set to '5' and status set to 'best'

'''
from __future__ import annotations
import os

import pi_config as c

from table import Table, Row

class Filter():
    def filter(self,rows:list[Row]):
        ''' Filter self._table  returning a list
            of rows which pass the test   '''
        return  [r for r in rows if self.test(r)]

    def test(self,row:Row):
        ''' Return True if the row passes the test. '''
        return True
    
    def get_descr(self):
        return "xxx"
    
class SelectedTreeNodesFilter(Filter):
    ''' Given the list of selected folders and rows 
        in a Tree, such as that returned by a TreeList,
        return rows which are selected
    '''
    def __init__(self,selected:list[str]):
        # Build filter conditions for collection rows.
        # Filter is for either a folder or a file
        self._filter_folders = set()
        self._filter_files = set()

        for name in selected:
            if name == "":
                self._filter_folders.add(name)
            elif os. path. isdir(f'{c.directory}{name}'):
                 self._filter_folders.add(name)
            else:
                file_loc,_,file_name = name.rpartition('/')
                self._filter_files.add((file_loc,file_name))

    def test(self,row:Row):
        file_loc = row['file_location']
        for dir in self._filter_folders:
            if file_loc.startswith(dir):
                return True
            
        file_name = row['file_name']
        return (file_loc,file_name) in self._filter_files
    
'''
    Standard Menu Filters
'''

class FilterPossibleTbd(Filter):
    ''' Filter rows which are still To Be Determined '''

    def test(self,row:Row):
        # Already set to Good or Best, or still TBD?
        if row['img_status'] == 'tbd':
            return True
        
        return False
    
    def get_descr(self):
        return "To Be Determined (TBD)"
    
class FilterPossibleGoodPlus(Filter):
    ''' Filter rows which are possibly Good or Best
        or already set to Good or Best '''

    def test(self,row:Row):
        # Already set to Good or Best, or still TBD?
        if row['rvw_lvl'] > '3' or row['img_status'] == 'tbd':
            return True
        
        return False
    
    def get_descr(self):
        return "possible Good or Best"
    
class FilterPossibleBest(Filter):
    ''' Filter rows which are possibly Good or Best
        or already set to Good or Best '''

    def test(self,row:Row):
        # Already set to Best, or still TBD?
        if row['rvw_lvl'] > '4' or row['img_status'] == 'tbd':
            return True
        
        return False
    
    def get_descr(self):
        return "possible Best"
    
'''
    Filters based on Level and Status
'''

class LevelStatusFilter(Filter):
    ''' Filter a table for a selected review level and status '''
    def __init__(self,level:str,status:str):
        self._level = level
        self._status = status

    def test(self,row:Row):
        return (row['rvw_lvl'] == self._level and
                row['img_status'] == self._status)
    
''' 
    Filter for specific status and level
'''
class InitialReviewFilter(LevelStatusFilter):
    ''' Initial review to filter out obviously not wanted pictures, 
        such as menus, or accidental shots '''
    def __init__(self,table:Table):
        super.__init__(table,"0","tbd")

class QualityReviewFilter(LevelStatusFilter):
    ''' Review for poor composition, blurry, eyes closed, etc. '''
    def __init__(self):
        super.__init__("1","tbd")

class DuplicateReviewFilter(LevelStatusFilter):
    ''' Review to select best of duplicate or very similar images. '''
    def __init__(self):
        super.__init__("2","tbd")

class GoodReviewFilter(LevelStatusFilter):
    ''' Photos good enough to show others without boring them. 
        These are probably good enough to upload to Google Photos.
        Roughly around 10% of total. '''
    def __init__(self):
        super.__init__("3","tbd")

class BestReviewFilter(LevelStatusFilter):
    ''' Best of the Best. Roughly about 1% of photos. '''
    def __init__(self):
        super.__init__("4","tbd")

''' Filters for those which have been reviewed to a certain level 
    Don't need these? 
    Shouldn't include TBD? Instead, wait until review complete for all.
    Filters are for 
    - 'reject'   - status = 'reject'
    - 'bad'      - status = 'bad'
    - 'passed'   - level >= 2 (will include duplicates), status in [tbd,dup,ok,good,best]
    - 'ok'       - level >= 3 (like 'ok' but without duplicates), status in [tbd,ok,select]
    - 'good'     - level >= 4 (good enough to show others and upload to google), status in [tbd,select,best]
    - 'best'     - level == 5 (the best of the selected), status in [best]

'''