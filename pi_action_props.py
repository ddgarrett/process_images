''' Implement action to display and update properties '''

import re

import FreeSimpleGUI as sg

import pi_config as c
from pi_action import PiAction
from pi_image_util import cnv_image
from pi_util import get_fn_for_row

_K_FN = '-PROPS-FILENAME-'
_K_LAT = '-PROPS-LAT-'
_K_LON = '-PROPS-LON-'
_K_CAPTION = '-PROPS-CAPTION-'
_K_ALBUM = '-PROPS-ALBUM-'
_K_INTRO = '-PROPS-INTRO-'
_K_EXT = '-PROPS-EXT-'
_K_THUMB = '-PROPS-THUMB-'
_E_UPDATE = '-PROPS-UPDATE-'
_E_CANCEL = '-PROPS-CANCEL-'


def _effective_values(values):
    if values is not None:
        return values
    return c.last_window_values if c.last_window_values is not None else {}


def _first_row(values):
    rowget = c.status_menu_rowgetter
    if rowget is None:
        return None
    rows = rowget(values)
    rows = [r for r in (rows or []) if r is not None]
    if not rows:
        return None
    return rows[0]


def _normalize_text(value):
    return re.sub(r'\s+', ' ', value).strip()


def _parse_coord(text, label, low, high):
    txt = str(text).strip()
    if txt == '':
        return True, '', None
    try:
        num = float(txt)
    except ValueError:
        return False, None, f'{label} must be a number.'
    if num < low or num > high:
        return False, None, f'{label} must be between {low} and {high}.'
    return True, txt, None


class PiFileProperties(PiAction):
    def handle_event(self, event, values):
        vals = _effective_values(values)
        row = _first_row(vals)
        if row is None:
            sg.popup('No image selected for Properties.')
            return

        fn = get_fn_for_row(row)
        full_fn = f'{c.directory}{fn}'.replace('\\', '/')
        rotate = 1
        try:
            rotate = int(row.get('img_rotate', 1))
        except (TypeError, ValueError):
            rotate = 1

        layout = [
            [sg.Text('File'), sg.Text(fn, key=_K_FN, expand_x=True)],
            [sg.Image(key=_K_THUMB, size=(280, 280))],
            [sg.Text('GPS Lat', size=(12, 1)), sg.Input(str(row.get('img_lat', '') or ''), key=_K_LAT, expand_x=True)],
            [sg.Text('GPS Lon', size=(12, 1)), sg.Input(str(row.get('img_lon', '') or ''), key=_K_LON, expand_x=True)],
            [sg.Text('Caption', size=(12, 1)), sg.Input(str(row.get('img_caption', '') or ''), key=_K_CAPTION, expand_x=True)],
            [sg.Text('Album URI', size=(12, 1)), sg.Input(str(row.get('img_album_uri', '') or ''), key=_K_ALBUM, expand_x=True)],
            [sg.Text('Intro', size=(12, 1)), sg.Multiline(str(row.get('img_intro_paragraph', '') or ''), key=_K_INTRO, size=(70, 5), expand_x=True)],
            [sg.Text('Ext Descr', size=(12, 1)), sg.Multiline(str(row.get('img_ext_descr', '') or ''), key=_K_EXT, size=(70, 5), expand_x=True)],
            [sg.Push(), sg.Button('Update', key=_E_UPDATE), sg.Button('Cancel', key=_E_CANCEL)],
        ]

        window = sg.Window('Image Properties', layout, modal=True, finalize=True, resizable=True)

        thumb, _ = cnv_image(full_fn, resize=(280, 280), rotate=rotate)
        if thumb != '':
            window[_K_THUMB].update(data=thumb, size=(280, 280))
            window._thumb_ref = thumb
        else:
            window._thumb_ref = None

        while True:
            dlg_event, dlg_values = window.read()
            if dlg_event in (sg.WIN_CLOSED, _E_CANCEL):
                break
            if dlg_event != _E_UPDATE:
                continue

            ok, lat_value, err = _parse_coord(dlg_values.get(_K_LAT, ''), 'GPS latitude', -90, 90)
            if not ok:
                sg.popup(err)
                continue
            ok, lon_value, err = _parse_coord(dlg_values.get(_K_LON, ''), 'GPS longitude', -180, 180)
            if not ok:
                sg.popup(err)
                continue

            row['img_lat'] = lat_value
            row['img_lon'] = lon_value
            row['img_caption'] = str(dlg_values.get(_K_CAPTION, '')).strip()
            row['img_album_uri'] = str(dlg_values.get(_K_ALBUM, '')).strip()
            row['img_intro_paragraph'] = _normalize_text(str(dlg_values.get(_K_INTRO, '')))
            row['img_ext_descr'] = _normalize_text(str(dlg_values.get(_K_EXT, '')))

            out_vals = dict(vals)
            out_vals[c.EVT_TABLE_ROW_CHG] = [row]
            c.listeners.notify(c.EVT_TABLE_ROW_CHG, out_vals)
            break

        window.close()