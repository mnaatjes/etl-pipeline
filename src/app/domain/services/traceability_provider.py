# src/app/domain/services/traceability_provider.py

class TraceabilityProvider:

    @staticmethod
    def generate() -> str: 
        """Returns generated UUID string"""
        from uuid import uuid4
        return str(uuid4())[:12]
    
    @staticmethod
    def resolve(user_override:str|None=None, context_id:str|None=None) -> str:
        """
        Coalescing Strategy:
        1. User Override - Priority A
        2. Context / Orchestration ID - Priority B
        3. Fresh Generation - Priority C
        """
        return user_override or context_id or TraceabilityProvider.generate()
