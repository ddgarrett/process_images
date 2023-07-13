'''
from csv_table import CsvTable
md = CsvTable('image_collection_metadata.csv')
print(md._cols.keys())
print(md._cols)
for row in md:eix
    print(row)
'''
import pathlib
import pi_config as c

dir_path = pathlib.Path(c.directory)

