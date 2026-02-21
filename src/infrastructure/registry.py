# src/infrastructure/registry.py
from ..app import DataStream
from .streams.local import LocalFileStream
from .streams.http import RemoteHttpStream
from .streams.db_table import DbTableStream

class StreamRegistry:
    def __init__(self):
        self._protocols = {
            "file://": LocalFileStream,
            "http://": RemoteHttpStream,
            "https://": RemoteHttpStream,
            "db://": DbTableStream
        }

    def get_stream(self, uri: str) -> DataStream:
        """
        Method acts as a Factory. 
        It looks at the URI "scheme," identifies which technical adapter is required, 
        and returns an initialized instance of that adapter—all while the rest of your code thinks it’s just 
        dealing with a generic DataStream.
        """
        for proto, stream_class in self._protocols.items():
            if uri.startswith(proto):
                # Strip protocol to get the actual path/url
                # 'file:///var/log/syslog' becomes '/var/log/syslog'
                resource = uri.replace(proto, "")
                return stream_class(resource)
        
        # Cannot find registered stream
        raise ValueError(f"No adapter registered for: {uri}")