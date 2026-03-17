# src/app/domain/services/traceability_provider.py

from src.app.domain.models.session_context import TraceID

class TraceabilityProvider:

    @staticmethod
    def generate() -> TraceID: 
        """Returns generated UUID string"""
        from uuid import uuid4
        return TraceID(str(uuid4())[:12])
    
    @staticmethod
    def resolve(user_override:str|None=None, context_id:str|None=None) -> TraceID:
        """
        Coalescing Strategy:
        1. User Override - Priority A
        2. Context / Orchestration ID - Priority B
        3. Fresh Generation - Priority C
        """
        winner = user_override or context_id or TraceabilityProvider.generate()
        return TraceID(winner)
