"""
Repository interfaces for the domain layer.
Define contracts for data access without implementation details.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import AnalysisResult, CodeMetrics, CodeSmell, DefectPrediction


class CodeAnalysisRepository(ABC):
    """Repository for storing and retrieving code analysis results."""
    
    @abstractmethod
    async def save_analysis(self, result: AnalysisResult) -> str:
        """Save an analysis result and return its ID."""
        pass
    
    @abstractmethod
    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Retrieve an analysis result by ID."""
        pass
    
    @abstractmethod
    async def get_analyses_by_file(self, file_path: str) -> List[AnalysisResult]:
        """Get all analyses for a specific file."""
        pass


class MetricsRepository(ABC):
    """Repository for code metrics data."""
    
    @abstractmethod
    async def save_metrics(self, file_path: str, metrics: CodeMetrics) -> None:
        """Save code metrics for a file."""
        pass
    
    @abstractmethod
    async def get_historical_metrics(self, file_path: str) -> List[CodeMetrics]:
        """Get historical metrics for trend analysis."""
        pass


class ModelRepository(ABC):
    """Repository for ML models used in analysis."""
    
    @abstractmethod
    async def save_model(self, model_name: str, model_data: bytes) -> None:
        """Save a trained ML model."""
        pass
    
    @abstractmethod
    async def load_model(self, model_name: str) -> Optional[bytes]:
        """Load a trained ML model."""
        pass
    
    @abstractmethod
    async def get_model_metadata(self, model_name: str) -> Optional[dict]:
        """Get metadata about a model (accuracy, training date, etc.)."""
        pass