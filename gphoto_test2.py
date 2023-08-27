'''
    from https://dev.to/davidedelpapa/manage-your-google-photo-account-with-python-p-2-3kaa
'''

from gphotospy import authorize
from gphotospy.media import *

CLIENT_SECRET_FILE = "gphoto_oauth.json"

service = authorize.init(CLIENT_SECRET_FILE)
media_manager = Media(service)
media_iterator = media_manager.list()
first_media = next(media_iterator)
media_obj = MediaItem(first_media)
print(media_obj)