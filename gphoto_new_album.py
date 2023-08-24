from gphotospy import authorize
from gphotospy.album import Album

# Select secrets file (got through Google's API console)
CLIENT_SECRET_FILE = "gphoto_oauth.json" # Here your secret's file. See below.

# Get authorization and return a service object
service = authorize.init(CLIENT_SECRET_FILE)

# Init the album manager
album_manager = Album(service)

# Create a new album
new_album = album_manager.create('test album')

# Get the album id and share it
id_album = new_album.get("id")
album_manager.share(id_album)