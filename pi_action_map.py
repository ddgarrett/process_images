'''
    Create a heat map with gps locations for selected files.
    Listens for events specified when this action was created.

    Like all actions, this class has a 'handle_event(self,event,values)' method.

    When a new instance of this class is created:
        text   - menu item text to display
        rowget - method to call to get list of rows to map
        
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
from urllib.request import urlopen
from urllib.error   import URLError

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

        # dictionary mapping a URI to the hmtl for that URI
        self._page_dict = {}

        marker_html = "<a href='file://{c.directory}row'>The Presidio</a>"

        lat_lon_lst = []
        weights = []
        markers = {}
        lat = 0
        lon = 0 
        cnt = 0
        for row in rows:
            fn = row['file_name']
            sub_uri = row['img_date_time']
            sub_uri = f'{sub_uri[0:4]}/{sub_uri[5:7]}'
            lat_lon = (float(row['img_lat']),float(row['img_lon']))
            lat += lat_lon[0]
            lon += lat_lon[1]
            cnt += 1

            uri = f'{c.BLOG_URI}/{sub_uri}'
            anchor = f'{fn}'
            href_descr = self._get_href_descr(uri,anchor)
            href = f'<a href="{uri}#{anchor}" target="_blank">{row.get_readable_date()} - {href_descr}</a>'
            
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

        # free up memory
        self._page_dict = {}


    def _get_href_descr(self,uri,anchor):
        '''
            Given the URI and anchor, return the description 
            for the photo which follows the anchor. 

            The description is based on the descrition 
            that is enclosed by the tag:
                <figcaption>...</figcaption>

            which follows the anchor:
                <p id="{anchor}">
        '''
        html = self._get_html(uri)
        anchor_html = self._find_anchor(html,anchor)
        return self._get_fig_caption(anchor_html,anchor)
    
    def _get_html(self,uri):
        ''' Return the HTML for a given URI.
        
            HTML is buffered in a dictionary.
        '''
        if not uri in self._page_dict:
            try:
                with urlopen(uri) as f:
                    # html = f.read().decode('utf-8')
                    # TODO: do better than 'ignore'?
                    # utf-8 decode caused errors in mapping,
                    # such as with character: ō
                    # Below will simply drop such characters
                    html = f.read().decode("ASCII", 'ignore')

                    ''' for debugging
                    with open("Output.txt", "w") as text_file:
                        text_file.write(html)
                    '''
            except URLError:
                print("urlerror: ",uri)
                html = "link not found"

            self._page_dict[uri] = html

        return self._page_dict[uri]
    
    def _find_anchor(self,html,anchor):
        ''' Return a substring of html which 
            follows the specified anchor
        '''
        tag = f'id="{anchor}"'
        idx = html.find(tag)
        if idx < 0:
            print("tag not found:",tag)
            return None
        
        return html[idx:]

    def _get_fig_caption(self,html,default_caption):
        ''' Find the text within the <figcaption>...</figcaption> tag
        
            If no figure caption, or no html, return the default caption.
        '''
        if not html:
            print("err: html not found",default_caption)
            return default_caption
        
        idx = html.find('<figcaption>')
        if idx < 0:
            print("err: caption not found",default_caption)
            return default_caption
        
        html = html[idx+12:]
        idx2 = html.find('</figcaption>')
        if idx2 < 0:
            print("err: end caption not found",default_caption)
            return default_caption
        
        return html[0:idx2]
        

        

