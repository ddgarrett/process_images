'''
    Collect Stats for a folder based on a given row in a table.

    Calls include:
      - add_stats
      - get_stats
      - get_headers

    Stats include
      - count of files at each level
      - a 'status' and 'lvl' which summarized the files. Either:
          - if any 'tbd' - the lowest level with 'tbd'
          - for others   - the highest level (best) in that folder

    Consider: 
      Simplify the reported "summary" to be either "completed" 
      or "Ln Awaiting Review"

'''
from __future__ import annotations

from table import Row

class FolderStats:

    headers = ['status','lvl','cnt','L0','L1','L2','L3','L4','L5']

    # prioritized lists of priorities with 'tbd' highest priority
    stat_priority = ['reject','dup','ok','selected','tbd']

    @staticmethod
    def get_headers() -> list[str]:
        return FolderStats.headers
    
    def __init__(self):
        self._cnt = 0
        self._lvl = [0]*(len(FolderStats.headers)-3)
        self._max_status_idx = -1
        self._min_lvl = -1

    def add_stats(self,row:Row):
        # keep lowest level for 'tbd'
        # highest level and highest status for all others
        self._cnt += 1
        row_lvl = row.get_int('rvw_lvl')
        self._lvl[row_lvl] = self._lvl[row_lvl] + 1

        status = row['img_status']
        status_idx = FolderStats.stat_priority.index(status)

        if status_idx == self._max_status_idx:
            if status == 'tbd':
                # min level for 'tbd'
                if row_lvl < self._min_lvl:
                    self._min_lvl = row_lvl
            else:
                # max level for all others
                if row_lvl > self._min_lvl:
                    self._min_lvl = row_lvl

        elif status_idx > self._max_status_idx:
            # keep highest status 
            self._max_status_idx = status_idx
            self._min_lvl = row_lvl

    def get_stats(self) -> list[any]:
        if self._max_status_idx == -1:
            r = []
        else:
            status = FolderStats.stat_priority[self._max_status_idx]
            r = [status,self._min_lvl,self._cnt]
            r.extend(self._lvl)
        return r
