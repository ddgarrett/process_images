'''
    Tabular Data with rows and columns.
    Allows access to data by row index and column name.
'''
from __future__ import annotations

class Table:
    '''
        Tabular Data defining rows and columns

        Data store is assumed to be tabular with fixed columns
        and each row containing all of the columns.
    '''

    # System field name constants
    # Use as table[Table.NAME] or table.get(Table.NAME)
    CURR_ROW    = "_curr_row"   # current row index
    COL_NAMES   = "_col_names"
    ROW_CNT     = "_row_cnt"
    COL_CNT     = "_col_cnt"

    def __init__(self,
                 cols:dict[str,Column] = {},
                 rows:list[Row] = [],
                 curr_row:int = 0) -> None:
        self._cols = cols   # dictionary of column name to column object
        self._rows = rows   # list of rows

        self._curr_row = -1 # index of current row
        self.set_cursor(curr_row)

        self._sort_by:list[tuple[str,bool]] = None

        # points to self unless this is a shallow copy of another table
        self._parent_table = self  

    def __len__(self) -> int:
        return len(self._rows)
    
    def __iter__(self) -> Table:
        t = self.copy()
        t._curr_row = -1
        return t
    
    def __next__(self) -> Table:
        self._curr_row += 1
        if self._curr_row < len(self):
            return self
        
        self._curr_row -= 1
        raise StopIteration
    
    def __getitem__(self,col_name:str) -> any:
        return self.get(col_name)
    
    def __setitem__(self,col_name,value):
        self.set(col_name,value)

    def __repr__(self):
        cols = str([c for c in self._cols])
        rows = str([r for r in self._rows])
        return f'{cols}\n{rows}'
         
    def _get_curr_row(self) -> Row:
        return self._rows[self._curr_row ]

    def reset_filters(self) -> Row:
        ''' reset the list of rows to the orignal
            unfiltered set of rows '''
        self._rows = self._get_root_table()._rows

    def _get_root_table(self):
        ''' Get the original parent table '''
        table = self
        while table != table._parent_table:
            table = table._parent_table

        return table

    ''' Used for creating an iteration object or other shallow copy
        Override IF the iteration or copy must be of same class as subclass. '''
    def copy(self) -> Table:
        t = Table(cols=self._cols,rows=self._rows,curr_row=0)
        t._parent_table = self._parent_table
        return t

    ''' Set current row '''
    def set_cursor(self,row_idx:int) -> Table:
        # just ignore if row indexes outside allowable range
        if row_idx < 0 or row_idx >= len(self._rows):
            return self
        
        self._curr_row = row_idx
        return self
    
    '''  return a column value
        for the current row '''
    def get(self,col_name:str) -> any:
        if col_name.startswith("_"):
            r = self.get_sys_value(col_name)
            # if not found, check if it's a valid column name
            if r != None:
                return r
            
        idx = self._curr_row
        try:
            return self._rows[idx]._get(col_name)
        except  IndexError:
            return None
        
    def get_int(self,col_name:str) -> int:
        try:
            return int(self.get(col_name))
        except ValueError:
            return 0
    
    ''' get system value '''
    def get_sys_value(self,name:str) -> any:
        if name == Table.CURR_ROW:
            return self._curr_row
        if name == Table.COL_NAMES:
            return list(self._cols.keys())
        if name == Table.ROW_CNT:
            return len(self._rows)
        if name == Table.COL_CNT:
            return len(self._cols)

        return None
    
    ''' Sets named column to value for the current row.
        Values are converted to string unless as_str == False.
    '''
    def set(self,col_name:str,value:any,as_str=True):
        idx = self._curr_row
        try:
            self._rows[idx]._set(col_name,value,as_str)
        except  IndexError:
            return None

    ''' append a new row with default values to the end of self._rows
        and set cursor to the new row '''
    def new_row(self):
        row = Row(self._cols,data=None)
        self._rows.append(row)
        self.set_cursor(len(self._rows)-1)

class Row:
    '''
        Loaded Data Row for a Data Store

        Cols is a dictionary of columns in the row
        Data is a simple list of column data.

    '''
    def __init__(self,cols:dict[str,Column],data:list[any]=None):
        self._cols = cols   # dictionary of column name to column object

        # If no data passed, initialize a new row
        if data == None:
            data = [c._default_value() for c in cols.values()]
            
        self._data = data   # list of column data for this row

    def __repr__(self):
        return str(self._data)
        
    def _get(self,col_name:str) -> any:
        col = self._cols.get(col_name)
        if col == None:
            return None
        return col._get(self._data)
    
    ''' TODO: keep track of original row when updates happen,
              support rollback and "updated" flag?  '''
    def _set(self,col_name:str,value:any,as_str:bool=True):
        col = self._cols.get(col_name)
        if col != None:
            col._set(self._data,value,as_str)

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
        return self._col_name
        
    def _get(self,data:list[any]) -> any:
        return data[self._col_idx]
    
    # column value is by default a string
    def _set(self,data:list[any],value,as_str:bool=True):
        if as_str:
            value = str(value)

        data[self._col_idx] = value

    # return true if current row value is equal passed value
    # override if conversion needed before compare, such as int or float
    def _is_equal(self,data:list[any],value:any):
        return data[self._col_idx] == value

    ''' initialize value in a row '''
    def _init_value(self,data:list[any]):
        data[self._col_idx] = ""

    def _default_value(self):
        return ""
    