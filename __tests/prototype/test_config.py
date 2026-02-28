# tests/prototype/test_config.py

"""
Waterfall Strategy: Heirarchy of Power
1. Baseline [Package Defaults]
    --> Registry looks at ProtocolSettings Dataclass (e.g. HttpSettings)
    --> Identifies hard-coded defaults (e.g. property: int = <default_value>)
2. Overlay [Global Bootstrap]
    --> Registry checks PipelineConfig (user provided at startup)
    --> Overwrites the defaults from ProtocolSettings Dataclass
3. Execution [Call-Time Overrides]
    --> Registry checks args of get_stream(...)
    --> Values from get_stream(...) used in place of Overlay and Baseline values
"""