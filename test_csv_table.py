
''' test basic load and save CSV Table '''
import csv_table
t = csv_table.CsvTable('data.csv')
t.set_cursor(1)
t['Year'] = "2021"
t.save_as('data_v2.csv')

''' test loading data from other source'''
import csv_table
col_names = ['c1','c2','column 3']
rows = [['row 1','r1 c2','r1,c3'],
     ['row 2','r2 c2','r2,c3'],
     ['row 3','r3 c2','r3,c3']]

table = csv_table.CsvTable('mock_data.csv',col_names=col_names)
for row in rows:
    row = table.new_row()
    for i,col in enumerate(col_names):
        row[col] = row[i]

table.save()

from csv_table import CsvTable
t = CsvTable('mock_data.csv')
print(t)

''' test metadata '''
from csv_table import CsvTable
md = CsvTable('image_collection_metadata.csv')
print(md._cols)
for i in range(len(md)):
    print(md._rows[i])



