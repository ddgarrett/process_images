'''
    Data Store saved as a CSV file.

    An optional Metadata table can be passed to 
    define column names, column type and default values.
    (note: use of column type and defaults not yet implemented)

    Create a new table by passing values
'''
from __future__ import annotations
import csv
from table import  Table, Column, Row

class CsvTable(Table):

    @staticmethod
    def default_metadata(col_names:list[str]):
        ''' Build default metadata from column names '''
        col_dict = {c:Column(i,c) for i,c in enumerate(col_names)}
        return col_dict

    @staticmethod
    def verify_metadata(col_names:list[str],metadata:CsvTable):
        ''' Verify that column names match those in metadata.
            If metadata contains more columns, return an array of 
            "extended" values to be used to extend each row read
            from the file. '''
        
        if len(col_names) > len(metadata.rows()):
            raise Exception("Metadata mismatch with CSV")
        
        col_dict = {}
        extend_values = []
        for i,md in enumerate(metadata):
            name = md['col_name']
            col_dict[name] = Column(i,name)

            if i < len(col_names):
                if name != col_names[i]:
                    raise Exception("Metadata mismatch with CSV")
            else:
                extend_values.append(md['default'])

        return col_dict, extend_values
    
    @staticmethod
    def build_column_dict(metadata:CsvTable):
        col_dict = {}
        for i,md in enumerate(metadata):
            name = md['col_name']
            col_dict[name] = Column(i,name)
        return col_dict
    
    def __init__(self,fn:str,metadata:CsvTable=None,col_names:list[str]=None):
        ''' fn = csv file name '''
        self.fn = fn
        rows=[]
        col_dict = {}
        extend_values = []

        try:
            with open(fn, newline='') as csvfile:
                reader = csv.reader(csvfile)
                columns  = next(reader) # first row has column names

                if metadata == None:
                    col_dict = CsvTable.default_metadata(columns)
                else:
                    col_dict,extend_values = CsvTable.verify_metadata(columns,metadata)

                for row in reader:
                    if len(extend_values) > 0:
                        row.extend(extend_values)
                    rows.append(self._create_row(col_dict,row))

        except FileNotFoundError:
            # build a new empty table from metadata
            if metadata == None:
                if col_names == None or len(col_names) == 0:
                    raise Exception("Metadata or column names required for new empty CSV table")
                
                col_dict = CsvTable.default_metadata(col_names)
            else:
                col_dict = CsvTable.build_column_dict(metadata)

        super().__init__(col_dict,rows)

    def save(self):
        ''' Save the table to the csv file '''
        self.save_as(self.fn)

    def save_as(self,fn:str):
        with open(fn,'w',newline='') as cvsfile:
            w = csv.writer(cvsfile)
            w.writerow(list(self._cols.keys()))
            for row in self._original_rows:
                w.writerow(row._data)

        self.fn = fn
