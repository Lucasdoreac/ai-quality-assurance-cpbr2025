"""
Domain entities for AI Quality Assurance system.
These represent the core business concepts in software quality analysis.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SmellType(Enum):
    LONG_METHOD = "long_method"
    LARGE_CLASS = "large_class"
    DUPLICATE_CODE = "duplicate_code"
    GOD_OBJECT = "god_object"
    FEATURE_ENVY = "feature_envy"
    DATA_CLASS = "data_class"
    LONG_PARAMETER_LIST = "long_parameter_list"


@dataclass
class CodeMetrics:
    """Code complexity and quality metrics."""
    cyclomatic_complexity: int
    lines_of_code: int
    number_of_methods: int
    number_of_attributes: int
    depth_of_inheritance: int
    coupling_between_objects: int
    lack_of_cohesion: float
    halstead_difficulty: float
    halstead_volume: float
    maintainability_index: float


@dataclass
class CodeSmell:
    """Represents a detected code smell."""
    smell_type: SmellType
    severity: Severity
    file_path: str
    line_start: int
    line_end: int
    function_name: Optional[str]
    class_name: Optional[str]
    description: str
    confidence: float
    metrics: Dict[str, Any]


@dataclass
class DefectPrediction:
    """Prediction of defect probability in code."""
    file_path: str
    class_name: Optional[str]
    function_name: Optional[str]
    defect_probability: float
    confidence: float
    risk_level: Severity
    contributing_factors: List[str]
    metrics_used: Dict[str, float]


@dataclass
class TestCase:
    """Generated test case."""
    function_name: str
    test_name: str
    test_code: str
    test_type: str  # unit, integration, property
    coverage_target: str
    expected_assertions: int
    complexity_score: float


@dataclass
class CodeRepair:
    """Suggested code repair/fix."""
    file_path: str
    line_start: int
    line_end: int
    issue_description: str
    suggested_fix: str
    fix_type: str  # bug_fix, refactor, optimization
    confidence: float
    validation_status: str  # pending, validated, failed


@dataclass
class AnalysisResult:
    """Complete analysis result for a code file or project."""
    file_path: str
    metrics: CodeMetrics
    code_smells: List[CodeSmell]
    defect_predictions: List[DefectPrediction]
    generated_tests: List[TestCase]
    suggested_repairs: List[CodeRepair]
    overall_quality_score: float
    analysis_timestamp: str
    processing_time_seconds: float