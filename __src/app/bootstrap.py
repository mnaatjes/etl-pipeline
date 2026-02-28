# src/app/bootstrap.py
from typing import Dict, Any
from dataclasses import dataclass, asdict
from src.app.ports.config import AppConfig
from src.app.ports.settings import StreamContract
from src.app.ports.resolver import SettingsResolver
from src.app.manager import StreamManager
from src.infrastructure.registry import StreamRegistry

class Bootstrap:
    """
    Assembler for Rules
    - NOT a Singleton; Use Dependency Injection
    - Wires the Logic (Resolver) to the Mechanics (Registry)
    """

    def __init__(self, app_config: AppConfig|None = None) -> None:
        # --- Tier 1: Baseline Settings
        self.app_settings = app_config or AppConfig()
        self.protocol_overrides: Dict[str, StreamContract]

    def add_protocol_settings(self, protocol:str, settings: StreamContract) -> None:
        """Allows the user to 'tune' a specific protocol before building."""
        if not isinstance(settings, StreamContract):
             raise TypeError(f"Settings for {protocol} must implement StreamContract")
        self.protocol_overrides[protocol] = settings

    def build_manager(self):
        """
        The Welding Point.
        Assembles the tools and returns the operational Manager.
        """
        # 1. Initialize the Mechanics (The Librarian)
        registry = StreamRegistry()
        
        # 2. Initialize the Brain (The Calculator)
        # We pass the collected Tier 1 and Tier 2 data into the Resolver
        resolver = SettingsResolver(
            app_config=self.app_settings, 
            protocol_overrides=self.protocol_overrides
        )
        
        # 3. Create the long-lived Operator
        return StreamManager(registry=registry, resolver=resolver)


