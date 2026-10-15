from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Python source code to analyze")
    title: Optional[str] = Field(default="Untitled Snippet", max_length=255)
    project_id: Optional[str] = None


class CodeStructureNode(BaseModel):
    id: str
    label: str
    node_type: str  # function, loop, conditional, operation, return, recursion
    line: Optional[int] = None
    complexity: Optional[str] = None
    details: Optional[str] = None


class CodeStructureEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None


class CodeStructureData(BaseModel):
    nodes: List[CodeStructureNode] = Field(default_factory=list)
    edges: List[CodeStructureEdge] = Field(default_factory=list)


class CodeStatistics(BaseModel):
    function_count: int = 0
    loop_count: int = 0
    for_loop_count: int = 0
    while_loop_count: int = 0
    conditional_count: int = 0
    max_nesting_depth: int = 0
    recursion_detected: bool = False
    recursion_count: int = 0
    operation_count: int = 0
    comprehension_count: int = 0
    imported_modules: List[str] = Field(default_factory=list)


class TheoreticalGrowthPoint(BaseModel):
    n: int
    O_1: float = Field(alias="O(1)")
    O_log_n: float = Field(alias="O(log n)")
    O_n: float = Field(alias="O(n)")
    O_n_log_n: float = Field(alias="O(n log n)")
    O_n2: float = Field(alias="O(n²)")
    O_n3: float = Field(alias="O(n³)")
    O_2n: Optional[float] = Field(default=None, alias="O(2^n)")
    O_3n: Optional[float] = Field(default=None, alias="O(3^n)")
    O_nfact: Optional[float] = Field(default=None, alias="O(n!)")

    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }


class TheoreticalGraphData(BaseModel):
    active_complexity: str
    growth_points: List[Dict[str, Any]] = Field(default_factory=list)
    disclaimer: str = "Theoretical asymptotic growth rate. This illustrates mathematical scaling, not hardware-dependent runtime benchmarks."


class SyntaxErrorInfo(BaseModel):
    line: int
    column: int
    message: str
    snippet: Optional[str] = None


class SpaceBreakdown(BaseModel):
    auxiliary: str = "O(1)"
    recursion_stack: str = "O(1)"
    output: str = "O(1)"
    total_retained: str = "O(1)"


class RecurrenceInfo(BaseModel):
    present: bool = False
    expression: Optional[str] = None
    is_solved: bool = False
    branching_factor: int = 0
    total_call_sites: int = 0
    derivation_steps: List[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    success: bool
    time_complexity: str
    tight_bound: Optional[str] = None
    space_complexity: str
    space_breakdown: SpaceBreakdown = Field(default_factory=SpaceBreakdown)
    confidence: str  # HIGH, MEDIUM, LOW, UNSUPPORTED
    confidence_reasons: List[str] = Field(default_factory=list)
    complexity_reasoning: str
    recurrence: RecurrenceInfo = Field(default_factory=RecurrenceInfo)
    statistics: CodeStatistics
    detected_patterns: List[str] = Field(default_factory=list)
    optimization_suggestions: List[str] = Field(default_factory=list)
    structure: CodeStructureData
    graph: TheoreticalGraphData
    functions: List[Dict[str, Any]] = Field(default_factory=list)
    loops: List[Dict[str, Any]] = Field(default_factory=list)
    recursion: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[SyntaxErrorInfo] = None
    submission_id: Optional[str] = None
