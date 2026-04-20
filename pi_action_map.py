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
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

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

# Max CSS width (px) for blog image in each map marker info window.
MAP_INFO_THUMB_MAX_PX = 120


def _open_local_html(map_path: str) -> None:
    '''Open a local HTML file in the system default GUI browser.

    Avoids webbrowser on Unix falling through to Lynx/w3m (blocking P_WAIT, no JS maps).
    '''
    path = Path(map_path).resolve()
    if sys.platform == 'darwin':
        subprocess.Popen(
            ['open', str(path)],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    elif sys.platform == 'win32':
        os.startfile(str(path))
    else:
        opener = shutil.which('xdg-open')
        if opener:
            subprocess.Popen(
                [opener, str(path)],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            webbrowser.open_new_tab(path.as_uri())


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
            lat_lon = (float(row['img_lat']),float(row['img_lon']))
            lat += lat_lon[0]
            lon += lat_lon[1]
            cnt += 1

            anchor = f'{fn}'
            uri, href_descr, img_src = self._resolve_blog_link(row['img_date_time'], anchor)
            href = f'<a href="{uri}#{anchor}" target="_blank">{row.get_readable_date()} - {href_descr}</a>'
            if img_src:
                safe_src = html.escape(img_src, quote=True)
                thumb = (
                    f'<img src="{safe_src}" alt="" '
                    f'style="max-width:{MAP_INFO_THUMB_MAX_PX}px;height:auto;'
                    'display:block;margin:0 auto 8px;">'
                )
                block = f'{thumb}{href}'
            else:
                block = href
            
            try:
                idx = lat_lon_lst.index(lat_lon)
                weights[idx] = weights[idx] + 1
                markers[lat_lon] = f'{markers[lat_lon]}<BR>{block}'
            except ValueError:
                lat_lon_lst.append(lat_lon)
                weights.append(1)
                markers[lat_lon] = block

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

        _open_local_html(map_fn)

        # free up memory
        self._page_dict = {}
        del gmap1


    @staticmethod
    def _blog_uri_for_month(year: int, month: int) -> str:
        return f'{c.BLOG_URI}/{year}/{month:02d}'

    @staticmethod
    def _next_calendar_month(year: int, month: int) -> tuple:
        if month == 12:
            return year + 1, 1
        return year, month + 1

    def _resolve_blog_link(self, img_date_time: str, anchor: str) -> tuple:
        '''
            Find blog page URI, figcaption, and figure image URL for anchor.

            Tries year/month from img_date_time, then the following month only.
            Returns (uri, description, img_src_or_none). URI is the page where the
            anchor was found, or the photo month URI if not found in either month.
        '''
        year = int(img_date_time[0:4])
        month = int(img_date_time[5:7])
        uri_photo_month = self._blog_uri_for_month(year, month)

        for uri in (uri_photo_month, self._blog_uri_for_month(*self._next_calendar_month(year, month))):
            page_html = self._get_html(uri)
            anchor_html = self._find_anchor(page_html, anchor)
            if anchor_html is not None:
                caption = self._get_fig_caption(anchor_html, anchor)
                img_src = self._get_figure_image_src(anchor_html)
                return uri, caption, img_src

        print('tag not found:', f'id="{anchor}"')
        return uri_photo_month, anchor, None
    
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
    
    def _find_anchor(self, html, anchor):
        ''' Return a substring of html which 
            follows the specified anchor
        '''
        tag = f'id="{anchor}"'
        idx = html.find(tag)
        if idx < 0:
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

    _IMG_SRC_RE = re.compile(
        r'<img\b[^>]*\bsrc\s*=\s*([\'"])(?P<src>.*?)\1',
        re.IGNORECASE | re.DOTALL,
    )

    @classmethod
    def _get_figure_image_src(cls, anchor_html: str):
        '''First <img src="..."> after the anchor and before <figcaption>, if any.'''
        if not anchor_html:
            return None
        low = anchor_html.lower()
        fc = low.find('<figcaption>')
        head = anchor_html[:fc] if fc >= 0 else anchor_html
        m = cls._IMG_SRC_RE.search(head)
        if not m:
            return None
        src = m.group('src').strip()
        return src or None

