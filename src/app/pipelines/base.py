# src/app/pipelines/base.py

from abc import ABC, abstractmethod
from ..ports.datastream import DataStream

class BasePipeline(ABC):
    def run(self, source: DataStream, sink: DataStream):
        """The Template Method defining the skeleton of the ETL process."""
        try:
            with source, sink:
                self.before_transfer(source, sink)
                
                for chunk in source.read():
                    processed_chunk = self.transform(chunk)
                    sink.write(processed_chunk)
                
                self.after_transfer(source, sink)
        except Exception as e:
            self.on_error(e)
            raise

    def before_transfer(self, source, sink):
        """Optional hook: e.g., Log start time or check disk space."""
        pass

    def transform(self, chunk):
        """Optional hook: Default is a 'Pass-through' (no change)."""
        return chunk

    def after_transfer(self, source, sink):
        """Optional hook: e.g., Update DB status to 'Complete'."""
        pass

    @abstractmethod
    def on_error(self, error: Exception):
        """Mandatory: Every pipeline must define how to handle failure."""
        pass