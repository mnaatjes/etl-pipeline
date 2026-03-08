# src/app/domain/exceptions/pipeline/pipeline_execution_error.py

class PipelineExecutionError(Exception):
    """Raises when a low-level engine error occurs"""
    pass