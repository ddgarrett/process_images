'''
    Process Images Element to Display a Gallery of Images


'''

import os
import FreeSimpleGUI as sg
from pi_action_map import PiActionMap

import pi_config as c
from pi_element import PiElement
from pi_filters import SelectedTreeNodesFilter
from pi_image_util import cnv_image
from status_menu import StatusMenu
from pi_util import get_fn_for_row

# Slider min: at this value (and only this step) no MUSIQ filter is applied.
MUSIQ_SLIDER_MIN_NO_FILTER = 3.0


def _musiq_cell_strictly_above_threshold(cell, thr: float) -> bool:
    """True if cell is d.ddd (one digit, dot, three digits) and score > floor string.

    thr is a step on (MUSIQ_SLIDER_MIN_NO_FILTER, 6.0]; formatted to one decimal as d.ddd.
    Assumes real scores are 1.000-9.999 so len-5 lexicographic compare matches numeric.
    Blank or bad shape is False (hidden when filter is on).
    """
    if cell is None:
        return False
    s = str(cell).strip()
    if len(s) != 5 or s[1] != ".":
        return False
    if not all(ch.isdigit() for ch in (s[0], s[2], s[3], s[4])):
        return False
    floor_s = f"{round(thr, 1):.3f}"
    return s > floor_s


class PiGalleryElem(PiElement):

    def __init__(self, key="-GALLERY-", events=None, cols=3, rows=3):
        super().__init__(key=key)
        self._new_size = (50,50)
        self._collection_rows = [] # rows being displayed
        self._base_collection_rows = []  # after tree/dup filter, before musiq filter
        self._selected_rows = []   # rows selected

        self._rows = rows
        self._cols = cols
        self._page = 0

        if events is None:
            events = []
        for e in events:
            c.listeners.add(e, self.files_selected)
        c.listeners.add(c.EVT_WIN_CONFIG,self.resize_image)
        c.listeners.add(c.EVT_TABLE_ROW_CHG,self.deselect_all)

        self._pgup_key = f'{self.key}PGUP-'
        self._pgdn_key = f'{self.key}PGDN-'
        self._home_key = f'{self.key}HOME-'
        self._end_key  = f'{self.key}END-'

        self._pgnbr_key  = f'{self.key}PGNBR-'
        self._musiq_slider_key = f'{self.key}MUSIQ-'

        c.listeners.add(self._pgdn_key,self._pgdn)
        c.listeners.add(self._pgup_key,self._pgup)
        c.listeners.add(self._home_key,self._home)
        c.listeners.add(self._end_key,self._end)
        c.listeners.add(self._musiq_slider_key, self._musiq_slider_changed)

        self._menu = None
        
        if c.app_function == c.APP_RVW_IMG:
            status_menu = StatusMenu()

            self._menu =  ['', 
                [ status_menu.get_set_menu(),
                '---',
                PiActionMap(rowget=self.get_rows).item(),
                f'&Properties::{c.EVT_FILE_PROPS}',
                'S&how', status_menu.get_show_submenu(),
                f'&Save::{c.EVT_FILE_SAVE}',
                f'E&xit::{c.EVT_EXIT}' ]]
            
        for i in range(9):
            c.listeners.add((f'{self.key}Thumbnail',i),self.thumb_selected)

    def _img_per_page(self):
        return self._rows * self._cols
    
    def _row_offset(self):
        return self._page * self._img_per_page()
    
    def _last_page(self):
        return int((len(self._collection_rows)-1)/self._img_per_page())
    
    def get_element(self) -> sg.Element:
        ''' return the PySimpleGUI Element to display a Gallery of Images '''
        gap = 3
        thumbnail_width = 50
        width = height  = (thumbnail_width + 4*gap + 4) * self._cols - 4*gap
        size = (thumbnail_width, thumbnail_width)

        layout_thumbnail = []
        for j in range(self._rows):
            temp = []
            for i in range(self._cols):
                pad = ((0, gap), gap) if i == 0 else ((gap, 0), gap) if i == self._cols-1 else (gap, gap)
                frame_layout = [[sg.Image(size=size, pad=(gap, gap), key=(f'{self.key}Thumbnail', j*self._cols+i),
                                          expand_x=True, expand_y=True,enable_events=True,right_click_menu=self._menu)]]
                # frame = sg.Frame(f"{j},{i}", frame_layout,title_location='s',pad=pad, key=("border", j*cols+i), 
                #                  background_color=sg.theme_background_color(),expand_x=True, expand_y=True)
                frame = sg.Frame("", frame_layout, pad=pad, key=(f'{self.key}border', j*self._cols+i), 
                                 background_color=sg.theme_background_color(),expand_x=True, expand_y=True,
                                 element_justification="center")
                temp.append(frame)
            layout_thumbnail.append(temp)

        layout_thumbnail_frame = [
            [sg.Column(layout_thumbnail, expand_x=True, expand_y=True, pad=(0, 0))],
        ]

        layout = [
            [sg.Frame("", layout_thumbnail_frame, size=(width, height), border_width=0,expand_x=True, expand_y=True,key=f'{self.key}gallery_frame')],
            [sg.Text("Page            ", size=0, key=self._pgnbr_key),
             sg.Push(),
             sg.Slider(
                 (MUSIQ_SLIDER_MIN_NO_FILTER, 6.0),
                 default_value=MUSIQ_SLIDER_MIN_NO_FILTER,
                 orientation="h",
                 resolution=0.1,
                 enable_events=True,
                 key=self._musiq_slider_key,
                 size=(36, 18),
                 pad=((8, 8), (0, 0)),
             ),
             sg.Push(),
             sg.Button('PgUp',key=self._pgup_key),
             sg.Button('PgDn',key=self._pgdn_key),
             sg.Button('Home',key=self._home_key),
             sg.Button('End',key=self._end_key)],
        ]

        return layout
    
    def get_rows(self,values):
        ''' Used by StatusMenu items and PiActionMap to get selected row '''
        return self._selected_rows
    
    ''' Event Handlers '''

    def files_selected(self,event,values):
        ''' Display a new list of collection rows
         
            Get the list of rows from current table, 
            BUT - in future may have to make a change to get 
            a filtered list of rows instead?
        '''

        self._base_collection_rows = []
        self._collection_rows = []
        self._selected_rows = []
        self._page = 0

        files_folders = values[event] # files and folders to display
        rows = c.table.rows()
        if len(rows) > 0 and len(files_folders) > 0:
            filter = SelectedTreeNodesFilter(files_folders)
            self._base_collection_rows = filter.filter(rows)

        self._apply_musiq_filter(values)
        self._display_pg()

    def resize_image(self,event,values):
        ''' Based on a __WINDOW CONFIG__ event, see if we need to 
            resize images 
        '''
        thumb_size = self._get_thumb_size()

        # wait until resized at least 8 pixels
        if thumb_size != (1,1) and thumb_size[1] != None:
            if (abs(thumb_size[0] - self._new_size[0]) > 8 or
                abs(thumb_size[1] - self._new_size[1]) > 8):
                self._new_size = thumb_size
                self._update_images()

    def deselect_all(self,event,values):
        ''' Deselect all selected thumbs
        '''
        self._selected_rows = []
        self._display_pg()

    def thumb_selected(self,event,values):
        ''' A single thumb was clicked.
            Select or deselect it.
        '''
        i = event[1]   # get displayed thumb number
        i += self._row_offset()  # get collection row number

        # ignore if after last row
        if i >= len(self._collection_rows):
            return 
        
        # add or remove collection row from selected rows
        row = self._collection_rows[i]
        if row in self._selected_rows:
            self._selected_rows.remove(row)
            bg = '#000000'
        else:
            self._selected_rows.append(row)
            bg = '#FFFFFF'

        c.window[event].Widget.config(bg=bg)

        # notify Image Select listeners of a new selected image
        if len(self._selected_rows) > 0:
            filename = get_fn_for_row(self._selected_rows[-1])
            values = {c.EVT_IMG_SELECT:[filename]}
            c.listeners.notify(c.EVT_IMG_SELECT,values)

    def _musiq_slider_changed(self, event, values):
        if c.syncing_from_tree:
            return
        self._selected_rows = []
        self._apply_musiq_filter(values)
        self._display_pg()

    def _musiq_threshold(self, values):
        # Listeners sometimes pass a partial values dict (e.g. EVT_IMG_SELECT only).
        # Merge last full window.read() snapshot so slider keys stay available.
        base = c.last_window_values if c.last_window_values is not None else {}
        overlay = values if values is not None else {}
        merged = {**base, **overlay}
        try:
            return float(merged.get(self._musiq_slider_key, MUSIQ_SLIDER_MIN_NO_FILTER))
        except (TypeError, ValueError):
            return MUSIQ_SLIDER_MIN_NO_FILTER

    def _apply_musiq_filter(self, values):
        thr = self._musiq_threshold(values)
        if round(thr, 1) == MUSIQ_SLIDER_MIN_NO_FILTER:
            self._collection_rows = list(self._base_collection_rows)
        else:
            self._collection_rows = []
            for row in self._base_collection_rows:
                if _musiq_cell_strictly_above_threshold(row.get("musiq_score"), thr):
                    self._collection_rows.append(row)
        self._clamp_page_to_last()

    def _clamp_page_to_last(self):
        last = self._last_page()
        if self._page > last:
            self._page = last
        if self._page < 0:
            self._page = 0

    def _pgup(self,event,values):
        ''' move one page up'''
        if self._page == 0:
            return
        
        self._page -= 1
        self.deselect_all(event,values)
        self._display_pg()

    def _pgdn(self,event,values):
        ''' move one page down '''
        if self._page == self._last_page():
            return 
        
        self._page += 1
        self.deselect_all(event,values)
        self._display_pg()

    def _end(self,event,values):
        ''' move to last page '''
        self._page = self._last_page()
        self.deselect_all(event,values)
        self._display_pg()

    def _home(self,event,values):
        ''' move to first page'''
        self._page = 0
        self.deselect_all(event,values)
        self._display_pg()

    ''' private methods '''

    def _display_pg(self):
        """ display the current page """
        pnbr = f'Page {self._page+1} of {self._last_page()+1}'
        c.window[self._pgnbr_key].update(value=pnbr)
        self._update_images()

    def _get_thumb_size(self):
        ''' get thumbnails size based on size of bordering frame '''
        key=f'{self.key}gallery_frame'
        gallery_widget = c.window[key].Widget
        fh = gallery_widget.winfo_height()
        fw = gallery_widget.winfo_width()
        pad = 8
        size = (int((fw-12)/3-pad),int((fh-36)/3-pad))
        return size

    def _update_images(self):
        # ignore if new size height or width < 16
        if self._new_size[0] < 16 or self._new_size[1] < 16:
            return

        row_nbr = 0
        col_nbr = 0
 
        i = 0
        for i in range(self._row_offset(),len(self._collection_rows)):
            row = self._collection_rows[i]
            fn = f'{c.directory}{row["file_location"]}/{row["file_name"]}'
            fn = fn.replace('\\','/')

            rotate = int(row['img_rotate'])
            resize_size = (self._new_size[0]-3,self._new_size[1]-3,)
            show_badge = row.get('dup_target') == 'T'
            thumb, osize = cnv_image(
                fn,
                resize=resize_size,
                rotate=rotate,
                dup_target_badge=show_badge,
                badge_for_gallery=True,
                overlay_text=row.get_overlay_text(),
                overlay_text_right=row.get_cosine_overlay_text(),
            )

            # key = (f'{self.key}Thumbnail', row_nbr*self._cols+col_nbr)
            key = self._thumb_key(row_nbr,col_nbr)
            c.window[key].update(data=thumb,size=resize_size)
            c.window[key].set_tooltip(row.get_tooltip_filename())
            self._set_bg_color(i,key)

            col_nbr += 1
            if col_nbr == self._cols:
                row_nbr += 1
                col_nbr = 0
                if row_nbr == self._rows:
                    break

        while row_nbr < self._rows:
            # key = (f'{self.key}Thumbnail', row_nbr*self._cols+col_nbr)
            key = self._thumb_key(row_nbr,col_nbr)
            c.window[key].update(data=None)
            c.window[key].set_tooltip(None)
            self._set_bg_color(i,key)
            
            col_nbr += 1
            if col_nbr == self._cols:
                row_nbr += 1
                col_nbr = 0
       
    def _set_bg_color(self,row_nbr:int,thumb_key:str):
        ''' set the background color of a thumbnail
            given a row number and a thumbnail key 
        '''
        if row_nbr >= len(self._collection_rows):
            bg = '#000000'
        else:
            row = self._collection_rows[row_nbr]
            if row in self._selected_rows:
                bg = '#FFFFFF'
            else:
                bg = '#000000'

        c.window[thumb_key].Widget.config(bg=bg)

    def _thumb_key(self,row_nbr:int,col_nbr:int):
        ''' return the thumbnail key given a row and column number '''
        return (f'{self.key}Thumbnail', row_nbr*self._cols+col_nbr)