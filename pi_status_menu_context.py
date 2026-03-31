"""
Set pi_config.status_menu_rowgetter on secondary-click for widgets that use the
shared status menu. Needed on Linux/Windows where there is no macOS Tk popup
path; Darwin sets rowgetter inside pi_macos_popup._show_popup instead.
"""

import platform

import pi_config as c


def _bind_rowgetter(widget, rowgetter):
    if widget is None or rowgetter is None:
        return

    def _set_ctx(_event=None):
        c.status_menu_rowgetter = rowgetter

    for seq in ('<Button-3>', '<Button-2>', '<Control-Button-1>'):
        widget.bind(seq, _set_ctx, add='+')


def install_status_menu_context_bindings(window, ui_refs):
    if platform.system() == 'Darwin':
        return

    tree = ui_refs.get('tree')
    image = ui_refs.get('image')
    gallery = ui_refs.get('gallery')
    dup = ui_refs.get('dup')

    if tree is not None and getattr(tree, '_menu', None):
        try:
            _bind_rowgetter(window[tree.key].Widget, tree.get_selected_rows)
        except Exception:
            pass

    if image is not None and getattr(image, '_menu', None):
        try:
            _bind_rowgetter(window[image.key].Widget, image.get_row)
        except Exception:
            pass

    if gallery is not None and getattr(gallery, '_menu', None):
        for i in range(gallery._rows * gallery._cols):
            key = (f'{gallery.key}Thumbnail', i)
            if key in window.AllKeysDict:
                try:
                    _bind_rowgetter(window[key].Widget, gallery.get_rows)
                except Exception:
                    pass

    if dup is not None and getattr(dup, '_menu', None):
        for i in range(dup._rows * dup._cols):
            key = (f'{dup.key}Thumbnail', i)
            if key in window.AllKeysDict:
                try:
                    _bind_rowgetter(window[key].Widget, dup.get_rows)
                except Exception:
                    pass
