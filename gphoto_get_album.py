from gphotospy import authorize
from gphotospy.album import *

CLIENT_SECRET_FILE = "gphoto_oauth.json"

service = authorize.init(CLIENT_SECRET_FILE)
album_manager = Album(service)
album_iterator = album_manager.list()
# print(album_iterator)

for a in album_iterator:
    print(a)

'''
print(f"album iterator is none: {album_iterator is None}")

first_album = next(album_iterator)
print(first_album)

'''