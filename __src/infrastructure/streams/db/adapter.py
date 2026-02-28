# src/infrastructure/streams/db_table.py
from ...app import DataStream

class DbTableStream(DataStream):
    def __init__(self, table): self.table = table
    def open(self): # Connect to DB...
        pass
    def read(self): # Yield rows converted to bytes/JSON...
        pass
    def close(self): pass