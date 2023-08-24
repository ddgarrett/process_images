from googleapiclient import discovery

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

class Photos:
    def __init__(self):
        self.SCOPE = "https://www.googleapis.com/auth/photoslibrary"
        self.CLIENT_SECRET = "client_id.json"
        self.store = file.Storage("storage.json")
        self.credentials = self.store.get()
        if not self.credentials or self.credentials.invalid:
            self.flow = client.flow_from_clientsecrets("client_id.json", self.SCOPE)
            self.credentials = tools.run_flow(self.flow, self.store)
        self.PHOTOS = discovery.build("photoslibrary", "v1", http=self.credentials.authorize(Http()))

photos = Photos()