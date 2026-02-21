# src/infrastructure/streams/http.py
from ...app import DataStream

class RemoteHttpStream(DataStream):
    def __init__(self, url): self.url = url
    def open(self): 
        import requests
        self.res = requests.get(self.url, stream=True)
    def read(self): yield from self.res.iter_content(chunk_size=4096)
    def close(self): self.res.close()