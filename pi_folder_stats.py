'''
    Collect Stats for a folder based on a given row in a table.

    Calls include:
      - add_stats
      - get_stats
      - get_headers

'''
from __future__ import annotations

from table import Table

class FolderStats:

    headers = ['cnt','L0','L1','L2','L3','L4','L5']

    @staticmethod
    def get_headers() -> list[str]:
        return FolderStats.headers
    
    def __init__(self):
        self._cnt = 0
        self._lvl = [0]*(len(FolderStats.headers)-1)

    def add_stats(self,row:Table):
        self._cnt += 1
        row_lvl = row.get_int('rvw_lvl')
        self._lvl[row_lvl] = self._lvl[row_lvl] + 1

    def get_stats(self) -> list[any]:
        r = [self._cnt]
        r.extend(self._lvl)
        return r
