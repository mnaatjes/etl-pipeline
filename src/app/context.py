# src/app/context.py
from dataclasses import dataclass
from src.app.domain.services.settings_resolver import SettingsResolver
from src.app.domain.services.resource_catalog import ResourceCatalog
from src.app.domain.services.resource_factory import ResourceFactory
from src.app.domain.services.traceability_provider import TraceabilityProvider
from src.app.use_cases.manager import StreamManager
from src.app.use_cases.pipeline_runner import PipelineRunner
from src.app.registry.engines import EngineRegistry
from src.app.registry.streams import StreamRegistry
from src.app.domain.models.app_config import AppConfig

@dataclass(frozen=True)
class AppContext:
    """Runtime Container"""
    # --- Orchestrators and Use Cases ---
    stream_manager: StreamManager
    pipeline_runner: PipelineRunner

    # --- Registries ---
    stream_registry: StreamRegistry
    engine_registry: EngineRegistry

    # --- Services and Resolvers ---
    settings_resolver: SettingsResolver
    resource_catalog: ResourceCatalog
    resource_factory: ResourceFactory
    trace_provider: TraceabilityProvider

    # --- Settings ---
    config: AppConfig
