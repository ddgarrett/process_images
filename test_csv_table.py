
''' test basic load and save CSV Table '''
import csv_table
t = csv_table.CsvTable('data.csv')
row = t.rows()[0]
row['Year'] = "2021"
print("saving data.csv as data_v2.csv with first 'Year' changed to 2021")

import os
os.remove('data_v2.csv')
t.save_as('data_v2.csv')

''' test loading data from other source'''
import csv_table
col_names = ['c1','c2','column 3']
rows = [['row 1','r1 c2','r1,c3'],
     ['row 2','r2 c2','r2,c3'],
     ['row 3','r3 c2','r3,c3']]

table = csv_table.CsvTable('mock_data.csv',col_names=col_names)
for r in rows:
    row = table.new_row()
    for i,col in enumerate(col_names):
        row[col] = r[i]

table.save()

from csv_table import CsvTable
t = CsvTable('mock_data.csv')
print(t)

import os
os.remove('mock_data.csv')

''' test metadata '''
from csv_table import CsvTable
md = CsvTable('image_collection_metadata.csv')
print(md._cols.keys())
for row in md:
    print(row)



