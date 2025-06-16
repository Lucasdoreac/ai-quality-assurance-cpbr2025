"""
Application use cases - Business logic for AI Quality Assurance.
These implement the core functionality using domain entities.
"""
import ast
import time
from typing import List, Dict, Any
from datetime import datetime

from ..domain.entities import (
    AnalysisResult, CodeMetrics, CodeSmell, DefectPrediction, 
    TestCase, CodeRepair, SmellType, Severity
)
from ..domain.repositories import CodeAnalysisRepository


class AnalyzeCodeUseCase:
    """Use case for comprehensive code analysis."""
    
    def __init__(self, repository: CodeAnalysisRepository):
        self.repository = repository
    
    async def execute(self, file_path: str, source_code: str) -> AnalysisResult:
        """Execute comprehensive code analysis."""
        start_time = time.time()
        
        # Parse the code into AST
        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")
        
        # Calculate metrics
        metrics = self._calculate_metrics(tree, source_code)
        
        # Detect code smells
        smells = self._detect_code_smells(tree, source_code, metrics)
        
        # Predict defects
        predictions = self._predict_defects(tree, metrics)
        
        # Generate tests
        tests = self._generate_tests(tree)
        
        # Suggest repairs
        repairs = self._suggest_repairs(tree, smells)
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(metrics, smells, predictions)
        
        processing_time = time.time() - start_time
        
        result = AnalysisResult(
            file_path=file_path,
            metrics=metrics,
            code_smells=smells,
            defect_predictions=predictions,
            generated_tests=tests,
            suggested_repairs=repairs,
            overall_quality_score=quality_score,
            analysis_timestamp=datetime.now().isoformat(),
            processing_time_seconds=processing_time
        )
        
        # Save analysis result
        await self.repository.save_analysis(result)
        
        return result
    
    def _calculate_metrics(self, tree: ast.AST, source_code: str) -> CodeMetrics:
        """Calculate comprehensive code metrics."""
        visitor = MetricsVisitor()
        visitor.visit(tree)
        
        lines = source_code.split('\n')
        lines_of_code = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Calculate Halstead metrics
        halstead = self._calculate_halstead_metrics(tree)
        
        # Calculate maintainability index
        maintainability = self._calculate_maintainability_index(
            visitor.cyclomatic_complexity, lines_of_code, halstead['volume']
        )
        
        return CodeMetrics(
            cyclomatic_complexity=visitor.cyclomatic_complexity,
            lines_of_code=lines_of_code,
            number_of_methods=visitor.number_of_methods,
            number_of_attributes=visitor.number_of_attributes,
            depth_of_inheritance=visitor.depth_of_inheritance,
            coupling_between_objects=visitor.coupling_between_objects,
            lack_of_cohesion=visitor.lack_of_cohesion,
            halstead_difficulty=halstead['difficulty'],
            halstead_volume=halstead['volume'],
            maintainability_index=maintainability
        )
    
    def _detect_code_smells(self, tree: ast.AST, source_code: str, metrics: CodeMetrics) -> List[CodeSmell]:
        """Detect code smells using AST analysis."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Long Method detection
                if self._count_function_lines(node, source_code) > 20:
                    smells.append(CodeSmell(
                        smell_type=SmellType.LONG_METHOD,
                        severity=Severity.MEDIUM,
                        file_path="",
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        function_name=node.name,
                        class_name=None,
                        description=f"Method '{node.name}' is too long ({self._count_function_lines(node, source_code)} lines)",
                        confidence=0.85,
                        metrics={"lines": self._count_function_lines(node, source_code)}
                    ))
                
                # Long Parameter List detection
                if len(node.args.args) > 5:
                    smells.append(CodeSmell(
                        smell_type=SmellType.LONG_PARAMETER_LIST,
                        severity=Severity.LOW,
                        file_path="",
                        line_start=node.lineno,
                        line_end=node.lineno,
                        function_name=node.name,
                        class_name=None,
                        description=f"Method '{node.name}' has too many parameters ({len(node.args.args)})",
                        confidence=0.90,
                        metrics={"parameter_count": len(node.args.args)}
                    ))
            
            elif isinstance(node, ast.ClassDef):
                # Large Class detection
                class_methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(class_methods) > 15:
                    smells.append(CodeSmell(
                        smell_type=SmellType.LARGE_CLASS,
                        severity=Severity.HIGH,
                        file_path="",
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        function_name=None,
                        class_name=node.name,
                        description=f"Class '{node.name}' is too large ({len(class_methods)} methods)",
                        confidence=0.80,
                        metrics={"method_count": len(class_methods)}
                    ))
        
        return smells
    
    def _predict_defects(self, tree: ast.AST, metrics: CodeMetrics) -> List[DefectPrediction]:
        """Predict defects using ML-based analysis."""
        predictions = []
        
        # Simple rule-based prediction (in real system, use trained ML model)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate defect probability based on complexity
                complexity_score = self._calculate_function_complexity(node)
                
                if complexity_score > 10:
                    probability = min(0.95, complexity_score / 20.0)
                    risk_level = Severity.HIGH if probability > 0.7 else Severity.MEDIUM
                    
                    predictions.append(DefectPrediction(
                        file_path="",
                        class_name=None,
                        function_name=node.name,
                        defect_probability=probability,
                        confidence=0.75,
                        risk_level=risk_level,
                        contributing_factors=["High cyclomatic complexity", "Many nested loops"],
                        metrics_used={"complexity": complexity_score}
                    ))
        
        return predictions
    
    def _generate_tests(self, tree: ast.AST) -> List[TestCase]:
        """Generate test cases for functions."""
        tests = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                # Generate basic unit test
                test_code = self._generate_test_code(node)
                
                tests.append(TestCase(
                    function_name=node.name,
                    test_name=f"test_{node.name}",
                    test_code=test_code,
                    test_type="unit",
                    coverage_target=f"{node.name}()",
                    expected_assertions=len(node.args.args) + 1,
                    complexity_score=self._calculate_function_complexity(node)
                ))
        
        return tests
    
    def _suggest_repairs(self, tree: ast.AST, smells: List[CodeSmell]) -> List[CodeRepair]:
        """Suggest code repairs based on detected smells."""
        repairs = []
        
        for smell in smells:
            if smell.smell_type == SmellType.LONG_METHOD:
                repairs.append(CodeRepair(
                    file_path="",
                    line_start=smell.line_start,
                    line_end=smell.line_end,
                    issue_description=smell.description,
                    suggested_fix="Consider breaking this method into smaller, more focused methods",
                    fix_type="refactor",
                    confidence=0.70,
                    validation_status="pending"
                ))
            elif smell.smell_type == SmellType.LONG_PARAMETER_LIST:
                repairs.append(CodeRepair(
                    file_path="",
                    line_start=smell.line_start,
                    line_end=smell.line_end,
                    issue_description=smell.description,
                    suggested_fix="Consider using a parameter object or configuration class",
                    fix_type="refactor",
                    confidence=0.65,
                    validation_status="pending"
                ))
        
        return repairs
    
    def _calculate_quality_score(self, metrics: CodeMetrics, smells: List[CodeSmell], predictions: List[DefectPrediction]) -> float:
        """Calculate overall quality score (0-100)."""
        base_score = 100.0
        
        # Deduct points for high complexity
        if metrics.cyclomatic_complexity > 10:
            base_score -= (metrics.cyclomatic_complexity - 10) * 2
        
        # Deduct points for code smells
        for smell in smells:
            if smell.severity == Severity.CRITICAL:
                base_score -= 15
            elif smell.severity == Severity.HIGH:
                base_score -= 10
            elif smell.severity == Severity.MEDIUM:
                base_score -= 5
            else:
                base_score -= 2
        
        # Deduct points for high defect probability
        high_risk_predictions = [p for p in predictions if p.risk_level in [Severity.HIGH, Severity.CRITICAL]]
        base_score -= len(high_risk_predictions) * 8
        
        return max(0.0, min(100.0, base_score))
    
    def _count_function_lines(self, node: ast.FunctionDef, source_code: str) -> int:
        """Count lines in a function."""
        if node.end_lineno:
            return node.end_lineno - node.lineno + 1
        return 1
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_halstead_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate Halstead complexity metrics."""
        operators = set()
        operands = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                operators.add(type(node.op).__name__)
            elif isinstance(node, ast.Name):
                operands.add(node.id)
        
        n1 = len(operators)  # Number of distinct operators
        n2 = len(operands)   # Number of distinct operands
        N1 = n1 * 2          # Total operators (approximation)
        N2 = n2 * 2          # Total operands (approximation)
        
        if n2 == 0:
            return {"difficulty": 0, "volume": 0}
        
        difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
        volume = (N1 + N2) * (n1 + n2).bit_length() if (n1 + n2) > 0 else 0
        
        return {"difficulty": difficulty, "volume": volume}
    
    def _calculate_maintainability_index(self, complexity: int, loc: int, volume: float) -> float:
        """Calculate maintainability index."""
        import math
        
        if loc == 0 or volume == 0:
            return 100.0
        
        # Simplified maintainability index calculation
        mi = 171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(loc)
        return max(0.0, min(100.0, mi))
    
    def _generate_test_code(self, node: ast.FunctionDef) -> str:
        """Generate test code for a function."""
        params = [arg.arg for arg in node.args.args if arg.arg != 'self']
        
        # Create test parameters
        test_params = []
        for param in params:
            test_params.append(f"{param}=None")  # Simplified
        
        params_str = ", ".join(test_params)
        
        return f"""def test_{node.name}():
    # Arrange
    {params_str if params_str else "pass"}
    
    # Act
    result = {node.name}({', '.join(params)})
    
    # Assert
    assert result is not None
    # Add more specific assertions based on function behavior"""


class MetricsVisitor(ast.NodeVisitor):
    """AST visitor to calculate code metrics."""
    
    def __init__(self):
        self.cyclomatic_complexity = 1
        self.number_of_methods = 0
        self.number_of_attributes = 0
        self.depth_of_inheritance = 0
        self.coupling_between_objects = 0
        self.lack_of_cohesion = 0.0
    
    def visit_FunctionDef(self, node):
        self.number_of_methods += 1
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.number_of_methods += 1
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
    
    def visit_AsyncFor(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
    
    def visit_Try(self, node):
        self.cyclomatic_complexity += len(node.handlers)
        self.generic_visit(node)