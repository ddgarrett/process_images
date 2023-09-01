'''
    Tabular Data with rows and columns.
    Allows access to data by row index and column name.
'''
from __future__ import annotations
from typing import Iterator

class Table:
    '''
        Tabular Data defining rows and columns

        Data store is assumed to be tabular with fixed columns
        and each row containing all of the columns.
    '''

    def __init__(self,
                 cols:dict[str,Column] = {},
                 rows:list[Row] = []) -> None:
        self._cols = cols   # dictionary of column name to column object
        self._rows = rows   # list of rows

    def __iter__(self) -> Iterator[Row]:
        return iter(self._rows)

    def __repr__(self):
        cols = str([c for c in self._cols])
        rows = str([r for r in self._rows])
        return f'{cols}\n{rows}'

    def rows(self):
        ''' return the underlying rows list '''
        return self._rows

    def new_row(self) -> Row:
        ''' append a new row with default values to the end of self._rows
            and return the new row
        '''
        row = self._create_row(self._cols,data=None)  # Row(self,self._cols,data=None)
        self._rows.append(row)
        return row
    
    def _create_row(self,cols,data=None):
        ''' Create a row without appending it. 
            Allows subclasses to use Row subclass.
        '''
        return Row(self,cols,data)

class Row:
    '''
        Loaded Data Row for a Data Store

        table is the Table this row was originally created for
        cols is a dictionary of columns in the row
        data is a simple list of column data.

    '''
    def __init__(self,table:Table,cols:dict[str,Column],data:list[any]=None):
        self._table = table
        self._cols = cols   # dictionary of column name to column object

        # If no data passed, initialize a new row
        # That is needed if builtin python sort is used.
        # Will also make selects of non-equal value better as well.
        if data == None:
            data = [c._default_value() for c in cols.values()]
            
        # CONSIDER: use Column to convert string to native object?
        self._data = data   # list of column data for this row

    def __repr__(self):
        return str(self._data)
    
    def __getitem__(self,col_name:str) -> any:
        return self.get(col_name)
    
    def __setitem__(self,col_name,value):
        # print('in __setitem__')
        self.set(col_name,value)

    def __lt__(self, other):
        for c in self._cols.values():
            other_value = other[c._col_name]
            r = c._compare(self._data,other_value)
            if r < 0:
                return True
            if r > 0:
                return False
        
        return False
        
    def get(self,col_name:str) -> any:
        col = self._cols.get(col_name)
        if col == None:
            return None
        return col._get(self._data)
    
    ''' TODO: keep track of original row when updates happen,
              support rollback and "updated" flag?  '''
    def set(self,col_name:str,value:any,as_str:bool=True):
        col = self._cols.get(col_name)
        if col != None:
            col._set(self._data,value,as_str)

    def get_int(self,col_name:str) -> int:
        try:
            return int(self.get(col_name))
        except ValueError:
            return 0
        
class Column:
    '''
        Data Column for a Data Store

        Defines the data in a single column for a data store.

        At a minimum defines the name and column number for a data column.
        Future (subclass?) versions may define field type, format and editing.
    '''

    def __init__(self,col_idx:int,col_name:str):
        self._col_idx = col_idx
        self._col_name = col_name

    def __repr__(self):
        return f'<Column {self._col_name} @ {self._col_idx}>'
        
    # Compare another value to the current value in data for this column.
    # Return an int which will be the sign equivalent of data[this] - value.
    #  - Negative if data[this] < value
    #  - Positive if data[this] > value
    #  - Zero     if data[this] == value
    # Override if conversion needed before compare, such as int or float
    def _compare(self,data:list[any],value:any) -> int:
        this_value = self._get(data)
        if this_value < value:
            return -1
        if this_value > value:
            return 1
        return 0

    def _get(self,data:list[any]) -> any:
        return data[self._col_idx]
    
    # column value is by default a string
    def _set(self,data:list[any],value,as_str:bool=True):
        if as_str:
            value = str(value)

        data[self._col_idx] = value

    # return true if current row value is equal passed value
    # override if conversion needed before compare, such as int or float
    def _equal(self,data:list[any],value:any):
        return data[self._col_idx] == value

    ''' initialize value in a row '''
    def _init_value(self,data:list[any]):
        data[self._col_idx] = ""

    def _default_value(self):
        return ""
    