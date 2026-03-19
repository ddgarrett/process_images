"""
macOS-specific popup menu fallback for FreeSimpleGUI/Tk widgets.

Why this exists:
- On some macOS setups, secondary click (right click / control-click) does not
  reliably trigger FreeSimpleGUI element `right_click_menu` handlers.
- The same app behavior works on Linux (including Raspberry Pi), so this
  workaround is intentionally macOS-only.

What this does:
- Converts existing FreeSimpleGUI menu definitions into native Tk `Menu` objects.
- Binds popup display directly on target widgets for common macOS secondary
  click gestures (`Button-3`, `Button-2`, `Control-Button-1`).
- Emits the original event IDs (the `::EVENT` suffixes) back into the app loop
  using `window.write_event_value(...)`, so existing action handling is reused.
"""

import platform


def _strip_menu_accelerators(label):
    return label.replace('&', '')


def _split_menu_item(text):
    if '::' in text:
        label, event = text.rsplit('::', 1)
        return _strip_menu_accelerators(label), event
    return _strip_menu_accelerators(text), None


def _build_tk_popup_menu(window, menu_def):
    """Build a Tk popup menu from a FreeSimpleGUI-style menu definition."""
    import tkinter as tk

    if not menu_def or not isinstance(menu_def, list) or len(menu_def) < 2:
        return None

    items = menu_def[1]
    popup = tk.Menu(window.TKroot, tearoff=0)

    def _add_items(parent_menu, entries):
        i = 0
        while i < len(entries):
            entry = entries[i]
            if isinstance(entry, str):
                if entry == '---':
                    parent_menu.add_separator()
                    i += 1
                    continue

                # Handle "Label", [submenu...] pattern.
                if i + 1 < len(entries) and isinstance(entries[i + 1], list):
                    submenu = tk.Menu(parent_menu, tearoff=0)
                    _add_items(submenu, entries[i + 1])
                    parent_menu.add_cascade(label=_strip_menu_accelerators(entry), menu=submenu)
                    i += 2
                    continue

                label, event = _split_menu_item(entry)
                if event:
                    parent_menu.add_command(label=label, command=lambda e=event: window.write_event_value(e, None))
                else:
                    parent_menu.add_command(label=label, state='disabled')
                i += 1
                continue

            # Handle ["Label", [submenu...]] pattern.
            if isinstance(entry, (list, tuple)) and len(entry) == 2 and isinstance(entry[1], list):
                submenu = tk.Menu(parent_menu, tearoff=0)
                _add_items(submenu, entry[1])
                parent_menu.add_cascade(label=_strip_menu_accelerators(entry[0]), menu=submenu)
                i += 1
                continue

            # Handle flattened submenu blocks like:
            # ['Set...', [...], 'TBD...', [...]]
            if isinstance(entry, (list, tuple)) and len(entry) > 0:
                _add_items(parent_menu, list(entry))
                i += 1
                continue

            i += 1

    _add_items(popup, items)
    return popup


def _bind_popup_to_widget(widget, popup):
    """Attach popup handlers directly to a widget for secondary-click gestures."""
    if widget is None or popup is None:
        return

    def _show_popup(event):
        try:
            popup.tk_popup(event.x_root, event.y_root)
        finally:
            popup.grab_release()
        return 'break'

    # Keep only the 3 common secondary-click variants.
    widget.bind('<Button-3>', _show_popup, add='+')
    widget.bind('<Button-2>', _show_popup, add='+')
    widget.bind('<Control-Button-1>', _show_popup, add='+')


def install_macos_popup_fallbacks(window, ui_refs):
    """Install macOS-only popup fallbacks on tree/image/gallery widgets.

    The fallback is deliberately limited to Darwin so Linux/Windows behavior is
    unchanged, including Raspberry Pi where default right-click handling works.
    """
    if platform.system() != 'Darwin':
        return

    tree = ui_refs.get('tree')
    image = ui_refs.get('image')
    gallery = ui_refs.get('gallery')

    if tree is not None and getattr(tree, '_menu', None):
        popup = _build_tk_popup_menu(window, tree._menu)
        _bind_popup_to_widget(window[tree.key].Widget, popup)

    if image is not None and getattr(image, '_menu', None):
        popup = _build_tk_popup_menu(window, image._menu)
        _bind_popup_to_widget(window[image.key].Widget, popup)

    if gallery is not None and getattr(gallery, '_menu', None):
        popup = _build_tk_popup_menu(window, gallery._menu)
        for i in range(gallery._rows * gallery._cols):
            key = (f'{gallery.key}Thumbnail', i)
            if key in window.AllKeysDict:
                _bind_popup_to_widget(window[key].Widget, popup)
