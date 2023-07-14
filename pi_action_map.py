'''
    Create a heat map with gps locations for selected files.
    Listens for events specified when this action was created.

    Like all actions, this class has a 'handle_event(self,event,values)' method.

    When a new instance of this class is created:
    event      - event to listen for
    value_list = list of files or folers within 'values' to generate a heat map for

    To use, simply create a new instance with the name of the event
    and the key of the list within event values. For example:

        # set up action for Map Event and Tree List 
        PiActionMap(c.EVT_ACT_MAP,value_list=c.EVT_TREE)
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
from pi_filters import SelectedTreeNodesFilter

class PiActionMap(PiAction):
    '''
        Create a heatmap for selected files and folders.

        event      - the event which triggers this action
        value_list - the name of the list within handle_event values
                     which contains the names of selected files and folders
    '''
    def __init__(self,event,value_list:list[str]):
        super().__init__(event)
        self._value_list = value_list

    def handle_event(self,event,values):
        files_folders = values[self._value_list]
        rows = c.table.rows()
        if len(rows) == 0 or len(files_folders) == 0:
            return 
        
        ''' generate a heat map of for the folders and files specified in values '''
        filter = SelectedTreeNodesFilter(files_folders)
        rows = filter.filter(rows)

        # drop rows where latitude and longitude are '0'
        rows = [r for r in rows 
                if r['img_lat'] != '0' and r['img_lon'] != '0']

        # generate heatmap for selected_rows
        if len(rows) > 0:
            self._generate_map(rows)

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
        map_fn = c.directory + "/" + "temp_map.html"
        gmap1.draw(map_fn)

        webbrowser.open_new_tab(map_fn)