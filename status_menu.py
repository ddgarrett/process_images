'''
    Return a common set of menu items to set the status of one or more photos
    or filter for particular statuses.

    "Set status" uses canonical events on pi_config (EVT_STATUS_*) handled once
    in pi_status_apply; row targets come from status_menu_rowgetter (set on
    right-click).

    Use something like this to embed the items in your menu:

    status_menu = StatusMenu()
    menu = ['',
             [ 'your item 1',
               status_menu.get_set_menu(),
               status_menu.get_show_submenu(),
               'your item 2']
            ]

'''

import pi_config as c


class StatusMenu():
    @staticmethod
    def get_set_menu():
        """Shared menu definition; same event strings on tree, gallery, image, dup."""
        return [
            'S&et Status...', [
                f'&Reject::{c.EVT_STATUS_SET_REJECT}',
                f'&Poor Quality::{c.EVT_STATUS_SET_POOR_QUALITY}',
                f'&Duplicate::{c.EVT_STATUS_SET_DUPLICATE}',
                f'&Just Okay::{c.EVT_STATUS_SET_JUST_OKAY}',
                f'&Good::{c.EVT_STATUS_SET_GOOD}',
                f'&Best!::{c.EVT_STATUS_SET_BEST}',
            ],
            '&TBD - Possible...', [
                f'&Reject::{c.EVT_STATUS_TBD_REJECT}',
                f'&Poor Quality::{c.EVT_STATUS_TBD_POOR_QUALITY}',
                f'&Duplicate::{c.EVT_STATUS_TBD_DUPLICATE}',
                f'&Ok Good Best::{c.EVT_STATUS_TBD_OK_GOOD_BEST}',
                f'&Good or Best::{c.EVT_STATUS_TBD_GOOD_OR_BEST}',
            ],
        ]

    @staticmethod
    def get_show_submenu():
        return [
            f'&All::{c.EVT_SHOW_ALL}',
            f'To Be Determined (&TBD)::{c.EVT_SHOW_TBD}',
            f'Possible &Duplicate::{c.EVT_SHOW_POSSIBLE_DUP}',
            f'Possible &Good or Best::{c.EVT_SHOW_POSSIBLE_GOOD_PLUS}',
            f'Possible &Best::{c.EVT_SHOW_POSSIBLE_BEST}',
            f'TBD Best + Best::{c.EVT_SHOW_TBD_BEST_PLUS_BEST}',
            f'&Custom::{c.EVT_NOT_IMPL}', #{c.EVT_SHOW_CUSTOM'}
        ]
