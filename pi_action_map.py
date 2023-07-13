'''
    Create a heat map with gps locations for selected files.
    Listens for events specified when action was created.

    value_list = list of files or folers to generate a heat map for.

'''
import os

from my_secrets import apikey
# ******************* CRITICAL *************
# if the generated map will be used uploaded to github
# comment out line below
from my_secrets import local_api_key as apikey
    
import webbrowser
import gmplot

import pi_config as c
from pi_action import PiAction

class PiActionMap(PiAction):
    '''
        Create a heatmap for selected files and folders.
    '''

    def __init__(self,event,value_list:list[str]):
        super().__init__(event)
        self._value_list = value_list

    def handle_event(self,event,values):
        if len(c.table.rows()) == 0:
            return 
        
        ''' generate a heat map of for the folders and files specified in values '''
        files_folders = values[self._value_list]

        # Build filter conditions for collection rows.
        # Filter is for either a folder or a file
        self._filter_folders = set()
        self._filter_files = set()

        for name in files_folders:
            if name == "":
                self._filter_folders.add(name)
            elif os. path. isdir(f'{c.directory}{name}'):
                 self._filter_folders.add(name)
            else:
                self._filter_files.add(name)

        selected_rows = [r for r in c.table.rows() if self._filter_row(r)]

        # generate heatmap for selected_rows
        if len(selected_rows) > 0:
            self._generate_map(selected_rows)

    def _filter_row(self,row):
        # reject the row if no latitude and longitude values
        if row['img_lat'] == '0' and row['img_lon'] == '0':
            return False
        
        file_loc = row['file_location']
        if f'{file_loc}/{row["file_name"]}' in self._filter_files:
            return True
        
        for dir in self._filter_folders:
            if file_loc.startswith(dir):
                return True
            
        return False
    
    def _generate_map(self,rows):
        ''' generate a google maps heatmap for list of rows '''
        marker_html = "<a href='file://{c.directory}row'>The Presidio</a>"

        lat_lon_lst = []
        weights = []
        markers = {}
        lat = 0
        lon = 0 
        cnt = 0
        for row in rows:
            fn = f"{row['file_location']}/{row['file_name']}"
            lat_lon = (float(row['img_lat']),float(row['img_lon']))
            lat += lat_lon[0]
            lon += lat_lon[1]
            cnt += 1
            href = f'<a href="file://{c.directory}{fn}" target="_blank">- {fn}</a>'
            try:
                idx = lat_lon_lst.index(lat_lon)
                weights[idx] = weights[idx] + 1
                markers[lat_lon] = f'{markers[lat_lon]}<BR>{href}' 
            except ValueError:
                lat_lon_lst.append(lat_lon)
                weights.append(1)
                markers[lat_lon] = href

        # print(lat_lon_lst,weights)
        
        lat = lat / cnt
        lon = lon / cnt

        gmap1 = gmplot.GoogleMapPlotter(lat,lon,13,apikey=apikey)

        pts = zip(*lat_lon_lst)

        for k,v in markers.items():
            gmap1.marker(k[0],k[1], label='I', info_window=v)

        gmap1.heatmap(
            *pts,
            radius=40,
            weights=weights,
            # gradient=[(0, 0, 255, 0), (0, 255, 0, 0.9), (255, 0, 0, 1)]
        )

        # Pass the absolute path
        map_fn = os.getcwd() + "/" + "temp_map.html"
        gmap1.draw(map_fn)

        webbrowser.open_new_tab(map_fn)