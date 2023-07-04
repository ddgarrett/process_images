'''
    Table operations including sort, group and select.
'''
from __future__ import annotations
import hjson
from table import Table, Row, Column
from typing import Type

''' Table Sort class '''
class TableSort:
    def __init__(self,by:list[tuple[str,bool]]):
        self._by = by
        self.sort_cols = [None]*len(by)

    def init_sort(self,table:Type[Table]) -> Type[Table]:
        pass

    def lt(self,row:Type[Row],other:Type[Row]) -> bool:
        return False

''' Return True if the row values equal to the group values
    for the specified columns. 'group_by' is a list of columns '''
class TableGroup:
    @staticmethod
    def _in_group(group_values:list[any],row:list[any],group_by:list[Column]):
        group_idx = 0
        for c in group_by:
            if c._is_equal(row,group_values[group_idx]):
                group_idx += 1
            else:
                return False
            
        return True


    def __init__(self,group_by:list[str]):
        self._group_by = group_by

    
    def execute(self,table:Type[Table]):
        r = table.copy()
        r._rows = r._rows.copy()
        r._cols = r._cols.copy()

        # result table columns are the group by columns
        new_cols = {}
        for col in self._group_by:
            new_cols[col] = r._cols[col]

        # plus a summary column
        new_cols['count'] = Column(len(self._group_by),'count')
        
        # for each row, add it to a new list of rows or add to counter
        curr_row = [None]*len(new_cols)
        for row in table:

        

def select_rows(t:str):
    return t['file_root'] == '\\2017-11'



q = '''
   {$or: [{ file_root: '2017-11'}]}
'''

j = hjson.loads(q)

print(j)