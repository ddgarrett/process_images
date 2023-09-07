'''
    Create a heat map with gps locations for selected files.
    Listens for events specified when this action was created.

    Like all actions, this class has a 'handle_event(self,event,values)' method.

    When a new instance of this class is created:
    event      - event to listen for
    value_list = list of files or folers within 'values' to generate a heat map for

    To use, simply create a new instance with method to call to get
    the list of selected rows. For example, the following generates a
    menu item which will map selected rows in the Tree List:

        # set up action for Map Event and Tree List 
        PiActionMap(rowget=self.get_selected_rows).item(),
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
        Parms:
        text   - menu item text to display
        rowget - method to call to get list of rows to map

    '''

    last_id = 0  # for generating unique Event IDs

    @classmethod
    def next_id(cls):
        cls.last_id += 1
        return cls.last_id
    
    def __init__(self,text="Map",rowget=None):
        self._id = self.next_id()
        self._text = text
        self._rowget=rowget
        super().__init__(event=self._get_event())

    def _get_event(self):
        return f'-PiActionMap{self._id}-'

    def item(self):
        ''' return an item name and unique event id'''
        return f'{self._text}::{self._get_event()}'

    def handle_event(self,event,values):
        ''' Hand Map Event - get list of rows and display in map '''

        # callback row getter
        rows = self._rowget(values)

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