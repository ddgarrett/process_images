from csv_table import CsvTable

t = CsvTable('data.csv')

rows = t.rows()

'''
t2 = list(filter(lambda r: r['Year'] > '2002',rows))
print(len(t),len(t2))

t2 = [r for r in rows if r['Year'] > '2002']
print(len(t),len(t2))
'''

print(t)

from operator import attrgetter, itemgetter

s = sorted(rows,key=itemgetter('Price','Year'))
print(s)