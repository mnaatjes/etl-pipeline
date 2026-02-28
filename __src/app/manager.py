# src/app/manager.py
from src.app.ports.resolver import SettingsResolver
from src.infrastructure.registry import StreamRegistry

class StreamManager:
    """
    Operational Face of Manager:
    - Coordinates Resolver and Registry
    """
    def __init__(self, registry:StreamRegistry, resolver:SettingsResolver) -> None:
        self.registry = registry
        self.resolver = resolver

    def get_stream(self, uri:str, as_sink:bool=False, **overrides):
        """User API"""
        # 1. Parse the protocol (e.g., 'http')
        protocol = uri.split("://")[0]
        
        # 2. Get the Final Regime for this specific call
        final_settings = self.resolver.resolve(protocol, overrides)
        
        # 3. Ask the Infrastructure Registry to build the physical stream
        return self.registry.get_stream(uri, as_sink=as_sink, **final_settings)