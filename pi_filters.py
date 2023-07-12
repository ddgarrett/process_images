'''
    Table Filter classes and subclasses.

    Does not affect the table being filtered.
    Instead it returns a list of rows which match the filter
    conditions.

    See below for Filers used during the review process. 
    The review process, levels and statuses include:
    1. Initial review to filter out obvious not wanted pictures.
        - current level = '0' and status = 'tbd' 
        - if rejected, level left at 0 and status set to 'reject'
        - if accepted, level set to '1' and status left at 'tbd'

    2. Quality review to weed out images with technical issues such
       as blurry, poor composition, portraits with eyes closed.
       - current level = '1' and status = 'tbd'
       - if rejected, level left at '1' and status set to 'reject'
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
       - if not chosen, level left at '4' and status set to 'select'
       - if not chosen, level set to '5' and status set to 'select'

'''
from __future__ import annotations

from table import Table, Row

class Filter():

    def __init__(self,table:Table):
        self._table = table

    def filter(self):
        ''' Filter self._table  returning a list
            of rows which pass the filter   '''
        return  [r for r in self._table if self.filter(r)]

    def test(self,row:Row):
        ''' Return True if the row passes the test. '''
        return False
    
class LevelStatusFilter(Filter):
    ''' Filter a table for a selected review level and status '''
    def __init__(self,table:Table,level:str,status:str):
        super().__init__(table)
        self._level = level
        self._status = status

    def test(self,row:Table):
        return (row['rvw_lvl'] == self._level and
                row['img_status'] == self._status)
    
''' 

'''
class InitialReviewFilter(LevelStatusFilter):
    ''' Initial review to filter out obviously not wanted pictures, 
        such as menus, or accidental shots '''
    def __init__(self,table:Table):
        super.__init__(table,"0","tbd")

class ReviewForQualityFilter(LevelStatusFilter):
    ''' Review for poor composition, blurry, eyes closed, etc. '''
    def __init__(self,table:Table):
        super.__init__(table,"1","tbd")

class ReviewDuplicatesFilter(LevelStatusFilter):
    ''' Review to select best of duplicate or very similar images. '''
    def __init__(self,table:Table):
        super.__init__(table,"2","tbd")

class ReviewForSelectedFilter(LevelStatusFilter):
    ''' Photos good enough to show others without boring them. 
        These are probably good enough to upload to Google Photos.
        Roughly around 10% of total. '''
    def __init__(self,table:Table):
        super.__init__(table,"3","tbd")

class ReviewForBestOfBestFilter(LevelStatusFilter):
    ''' Best of the Best. Roughly about 1% of photos. '''
    def __init__(self,table:Table):
        super.__init__(table,"4","tbd")

''' Filters for those which have been reviewed to a certain level 
    Filters are for 
    - 'rejected' - status = 'reject'
    - 'ok'       - level >= 2 (will include duplicates), status in [tbd,dup,ok,select]
    - 'good'     - level >= 3 (like 'ok' but without duplicates), status in [tbd,ok,select]
    - 'select'   - level >= 4 (good enough to show others and upload to google), status in [tbd,select]
    - 'best'     = level == 5 (the best of the selected), status in [select]

'''