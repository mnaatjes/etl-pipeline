# src/app/domain/services/context_orchestrator.py

# --- Models ---
from src.app.domain.models.session_context import SessionContext, TraceID
from src.app.domain.models.app_config import AppConfig
# --- Services ---
from src.app.domain.services.settings_resolver import SettingsResolver
from src.app.domain.services.traceability_provider import TraceabilityProvider

class ContextOrchestrator:

    def __init__(
            self,
            resolver: SettingsResolver,
            app_config: AppConfig
    ) -> None:
        # Onboard Properties
        self._resolver   = resolver
        self._app_config = app_config

    def build_context(
            self,
            session_trace: TraceID,
            method_trace: str|None=None,
            **overrides
    ) -> SessionContext:
        """
        Determines identity for operation

        :param session_trace (str) - 
        :param method_trace (str) - Represents the 'Method-Level Override' for the trace_id

        Returns
        """
        tid = TraceabilityProvider.resolve(
            user_override=method_trace, 
            context_id=session_trace
        )
        return SessionContext(trace_id=tid, overrides=overrides)
    
    def resolve_settings(self, context: SessionContext) -> dict:
        """Calculates the final 'Dense Bag' for the infrastructure layer"""
        return self._resolver.resolve(self._app_config, context.overrides)