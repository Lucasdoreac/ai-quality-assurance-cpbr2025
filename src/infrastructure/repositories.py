"""
Infrastructure implementations of repository interfaces.
Real file-based and in-memory storage for development and demo.
"""
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import pickle

from ..domain.entities import AnalysisResult, CodeMetrics
from ..domain.repositories import CodeAnalysisRepository, MetricsRepository, ModelRepository


class InMemoryCodeAnalysisRepository(CodeAnalysisRepository):
    """In-memory repository for code analysis results."""
    
    def __init__(self):
        self._analyses: Dict[str, AnalysisResult] = {}
    
    async def save_analysis(self, result: AnalysisResult) -> str:
        """Save an analysis result and return its ID."""
        analysis_id = str(uuid.uuid4())
        self._analyses[analysis_id] = result
        return analysis_id
    
    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Retrieve an analysis result by ID."""
        return self._analyses.get(analysis_id)
    
    async def get_analyses_by_file(self, file_path: str) -> List[AnalysisResult]:
        """Get all analyses for a specific file."""
        return [
            result for result in self._analyses.values()
            if result.file_path == file_path
        ]


class FileCodeAnalysisRepository(CodeAnalysisRepository):
    """File-based repository for persistent storage."""
    
    def __init__(self, storage_path: str = "data/analyses"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    async def save_analysis(self, result: AnalysisResult) -> str:
        """Save an analysis result and return its ID."""
        analysis_id = str(uuid.uuid4())
        
        # Convert result to dict for JSON serialization
        result_dict = self._analysis_to_dict(result)
        
        file_path = os.path.join(self.storage_path, f"{analysis_id}.json")
        with open(file_path, 'w') as f:
            json.dump(result_dict, f, indent=2)
        
        return analysis_id
    
    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Retrieve an analysis result by ID."""
        file_path = os.path.join(self.storage_path, f"{analysis_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            result_dict = json.load(f)
        
        return self._dict_to_analysis(result_dict)
    
    async def get_analyses_by_file(self, file_path: str) -> List[AnalysisResult]:
        """Get all analyses for a specific file."""
        results = []
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                full_path = os.path.join(self.storage_path, filename)
                with open(full_path, 'r') as f:
                    result_dict = json.load(f)
                
                if result_dict.get('file_path') == file_path:
                    results.append(self._dict_to_analysis(result_dict))
        
        return results
    
    def _analysis_to_dict(self, result: AnalysisResult) -> Dict[str, Any]:
        """Convert AnalysisResult to dictionary."""
        return {
            'file_path': result.file_path,
            'metrics': {
                'cyclomatic_complexity': result.metrics.cyclomatic_complexity,
                'lines_of_code': result.metrics.lines_of_code,
                'number_of_methods': result.metrics.number_of_methods,
                'number_of_attributes': result.metrics.number_of_attributes,
                'depth_of_inheritance': result.metrics.depth_of_inheritance,
                'coupling_between_objects': result.metrics.coupling_between_objects,
                'lack_of_cohesion': result.metrics.lack_of_cohesion,
                'halstead_difficulty': result.metrics.halstead_difficulty,
                'halstead_volume': result.metrics.halstead_volume,
                'maintainability_index': result.metrics.maintainability_index
            },
            'code_smells': [
                {
                    'smell_type': smell.smell_type.value,
                    'severity': smell.severity.value,
                    'file_path': smell.file_path,
                    'line_start': smell.line_start,
                    'line_end': smell.line_end,
                    'function_name': smell.function_name,
                    'class_name': smell.class_name,
                    'description': smell.description,
                    'confidence': smell.confidence,
                    'metrics': smell.metrics
                } for smell in result.code_smells
            ],
            'defect_predictions': [
                {
                    'file_path': pred.file_path,
                    'class_name': pred.class_name,
                    'function_name': pred.function_name,
                    'defect_probability': pred.defect_probability,
                    'confidence': pred.confidence,
                    'risk_level': pred.risk_level.value,
                    'contributing_factors': pred.contributing_factors,
                    'metrics_used': pred.metrics_used
                } for pred in result.defect_predictions
            ],
            'generated_tests': [
                {
                    'function_name': test.function_name,
                    'test_name': test.test_name,
                    'test_code': test.test_code,
                    'test_type': test.test_type,
                    'coverage_target': test.coverage_target,
                    'expected_assertions': test.expected_assertions,
                    'complexity_score': test.complexity_score
                } for test in result.generated_tests
            ],
            'suggested_repairs': [
                {
                    'file_path': repair.file_path,
                    'line_start': repair.line_start,
                    'line_end': repair.line_end,
                    'issue_description': repair.issue_description,
                    'suggested_fix': repair.suggested_fix,
                    'fix_type': repair.fix_type,
                    'confidence': repair.confidence,
                    'validation_status': repair.validation_status
                } for repair in result.suggested_repairs
            ],
            'overall_quality_score': result.overall_quality_score,
            'analysis_timestamp': result.analysis_timestamp,
            'processing_time_seconds': result.processing_time_seconds
        }
    
    def _dict_to_analysis(self, data: Dict[str, Any]) -> AnalysisResult:
        """Convert dictionary to AnalysisResult."""
        from ..domain.entities import (
            CodeMetrics, CodeSmell, DefectPrediction, TestCase, CodeRepair,
            SmellType, Severity
        )
        
        # Reconstruct metrics
        metrics = CodeMetrics(**data['metrics'])
        
        # Reconstruct code smells
        code_smells = [
            CodeSmell(
                smell_type=SmellType(smell['smell_type']),
                severity=Severity(smell['severity']),
                file_path=smell['file_path'],
                line_start=smell['line_start'],
                line_end=smell['line_end'],
                function_name=smell['function_name'],
                class_name=smell['class_name'],
                description=smell['description'],
                confidence=smell['confidence'],
                metrics=smell['metrics']
            ) for smell in data['code_smells']
        ]
        
        # Reconstruct defect predictions
        defect_predictions = [
            DefectPrediction(
                file_path=pred['file_path'],
                class_name=pred['class_name'],
                function_name=pred['function_name'],
                defect_probability=pred['defect_probability'],
                confidence=pred['confidence'],
                risk_level=Severity(pred['risk_level']),
                contributing_factors=pred['contributing_factors'],
                metrics_used=pred['metrics_used']
            ) for pred in data['defect_predictions']
        ]
        
        # Reconstruct tests
        generated_tests = [
            TestCase(
                function_name=test['function_name'],
                test_name=test['test_name'],
                test_code=test['test_code'],
                test_type=test['test_type'],
                coverage_target=test['coverage_target'],
                expected_assertions=test['expected_assertions'],
                complexity_score=test['complexity_score']
            ) for test in data['generated_tests']
        ]
        
        # Reconstruct repairs
        suggested_repairs = [
            CodeRepair(
                file_path=repair['file_path'],
                line_start=repair['line_start'],
                line_end=repair['line_end'],
                issue_description=repair['issue_description'],
                suggested_fix=repair['suggested_fix'],
                fix_type=repair['fix_type'],
                confidence=repair['confidence'],
                validation_status=repair['validation_status']
            ) for repair in data['suggested_repairs']
        ]
        
        return AnalysisResult(
            file_path=data['file_path'],
            metrics=metrics,
            code_smells=code_smells,
            defect_predictions=defect_predictions,
            generated_tests=generated_tests,
            suggested_repairs=suggested_repairs,
            overall_quality_score=data['overall_quality_score'],
            analysis_timestamp=data['analysis_timestamp'],
            processing_time_seconds=data['processing_time_seconds']
        )


class InMemoryMetricsRepository(MetricsRepository):
    """In-memory repository for metrics."""
    
    def __init__(self):
        self._metrics: Dict[str, List[CodeMetrics]] = {}
    
    async def save_metrics(self, file_path: str, metrics: CodeMetrics) -> None:
        """Save code metrics for a file."""
        if file_path not in self._metrics:
            self._metrics[file_path] = []
        self._metrics[file_path].append(metrics)
    
    async def get_historical_metrics(self, file_path: str) -> List[CodeMetrics]:
        """Get historical metrics for trend analysis."""
        return self._metrics.get(file_path, [])


class FileModelRepository(ModelRepository):
    """File-based repository for ML models."""
    
    def __init__(self, storage_path: str = "data/models"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    async def save_model(self, model_name: str, model_data: bytes) -> None:
        """Save a trained ML model."""
        model_path = os.path.join(self.storage_path, f"{model_name}.pkl")
        with open(model_path, 'wb') as f:
            f.write(model_data)
        
        # Save metadata
        metadata = {
            'name': model_name,
            'saved_at': datetime.now().isoformat(),
            'size_bytes': len(model_data)
        }
        metadata_path = os.path.join(self.storage_path, f"{model_name}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    async def load_model(self, model_name: str) -> Optional[bytes]:
        """Load a trained ML model."""
        model_path = os.path.join(self.storage_path, f"{model_name}.pkl")
        
        if not os.path.exists(model_path):
            return None
        
        with open(model_path, 'rb') as f:
            return f.read()
    
    async def get_model_metadata(self, model_name: str) -> Optional[dict]:
        """Get metadata about a model."""
        metadata_path = os.path.join(self.storage_path, f"{model_name}_metadata.json")
        
        if not os.path.exists(metadata_path):
            return None
        
        with open(metadata_path, 'r') as f:
            return json.load(f)