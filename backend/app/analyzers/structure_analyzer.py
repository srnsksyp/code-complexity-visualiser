import ast
from typing import List, Dict, Any, Optional
from app.schemas.analysis import (
    CodeStructureData,
    CodeStructureNode,
    CodeStructureEdge,
    CodeStatistics,
)


class StructureAnalyzer:
    """Extracts high-level AST structure, statistics, and graph nodes/edges for React Flow."""

    def __init__(self):
        self.node_id_counter = 0
        self.edge_id_counter = 0
        self.nodes: List[CodeStructureNode] = []
        self.edges: List[CodeStructureEdge] = []

    def analyze(self, tree: ast.AST, recursion_detected: bool = False, recursion_count: int = 0) -> tuple[CodeStatistics, CodeStructureData]:
        self.node_id_counter = 0
        self.edge_id_counter = 0
        self.nodes = []
        self.edges = []

        stats = CodeStatistics()
        stats.recursion_detected = recursion_detected
        stats.recursion_count = recursion_count

        # Compute counts and imported modules
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                stats.function_count += 1
            elif isinstance(node, ast.For):
                stats.loop_count += 1
                stats.for_loop_count += 1
            elif isinstance(node, ast.While):
                stats.loop_count += 1
                stats.while_loop_count += 1
            elif isinstance(node, ast.If):
                stats.conditional_count += 1
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                stats.comprehension_count += 1
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    stats.imported_modules.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    stats.imported_modules.append(node.module)
            elif isinstance(node, (ast.Assign, ast.AugAssign, ast.Expr, ast.Return)):
                stats.operation_count += 1

        # Calculate max nesting depth
        stats.max_nesting_depth = self._calculate_max_nesting(tree)

        # Build Flow Graph nodes and edges
        root_node_id = self._create_node(
            label="Module / Program Entry",
            node_type="root",
            line=1,
            complexity="O(1)",
            details="Program execution entry point"
        )

        self._build_flow_hierarchy(tree, parent_id=root_node_id)

        structure_data = CodeStructureData(nodes=self.nodes, edges=self.edges)
        return stats, structure_data

    def _get_next_node_id(self, prefix: str = "node") -> str:
        self.node_id_counter += 1
        return f"{prefix}_{self.node_id_counter}"

    def _get_next_edge_id(self) -> str:
        self.edge_id_counter += 1
        return f"edge_{self.edge_id_counter}"

    def _create_node(
        self,
        label: str,
        node_type: str,
        line: Optional[int] = None,
        complexity: Optional[str] = None,
        details: Optional[str] = None
    ) -> str:
        nid = self._get_next_node_id(node_type)
        self.nodes.append(
            CodeStructureNode(
                id=nid,
                label=label,
                node_type=node_type,
                line=line,
                complexity=complexity,
                details=details
            )
        )
        return nid

    def _create_edge(self, source: str, target: str, label: Optional[str] = None):
        eid = self._get_next_edge_id()
        self.edges.append(
            CodeStructureEdge(
                id=eid,
                source=source,
                target=target,
                label=label
            )
        )

    def _calculate_max_nesting(self, node: ast.AST, current_depth: int = 0) -> int:
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.If, ast.FunctionDef, ast.With, ast.Try)):
                depth = self._calculate_max_nesting(child, current_depth + 1)
                if depth > max_depth:
                    max_depth = depth
            else:
                depth = self._calculate_max_nesting(child, current_depth)
                if depth > max_depth:
                    max_depth = depth
        return max_depth

    def _build_flow_hierarchy(self, parent_ast: ast.AST, parent_id: str):
        """Recursively builds graph nodes for significant control flow and statements."""
        children = list(ast.iter_child_nodes(parent_ast))
        prev_sibling_id: Optional[str] = None

        for child in children:
            cur_id: Optional[str] = None

            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args_list = [a.arg for a in child.args.args]
                sig = f"{child.name}({', '.join(args_list)})"
                cur_id = self._create_node(
                    label=sig,
                    node_type="function",
                    line=child.lineno,
                    details=f"Function definition with {len(args_list)} parameters"
                )
                self._create_edge(parent_id, cur_id, label="defines")
                self._build_flow_hierarchy(child, parent_id=cur_id)

            elif isinstance(child, ast.For):
                iter_str = ast.unparse(child.iter) if hasattr(ast, "unparse") else "iterable"
                target_str = ast.unparse(child.target) if hasattr(ast, "unparse") else "i"
                cur_id = self._create_node(
                    label=f"for {target_str} in {iter_str}",
                    node_type="loop",
                    line=child.lineno,
                    complexity="O(n)",
                    details=f"For loop iterating over {iter_str}"
                )
                self._create_edge(parent_id, cur_id, label="loop")
                self._build_flow_hierarchy(child, parent_id=cur_id)

            elif isinstance(child, ast.While):
                test_str = ast.unparse(child.test) if hasattr(ast, "unparse") else "condition"
                cur_id = self._create_node(
                    label=f"while {test_str}",
                    node_type="loop",
                    line=child.lineno,
                    complexity="O(n) / O(log n)",
                    details=f"While loop evaluated on '{test_str}'"
                )
                self._create_edge(parent_id, cur_id, label="while")
                self._build_flow_hierarchy(child, parent_id=cur_id)

            elif isinstance(child, ast.If):
                test_str = ast.unparse(child.test) if hasattr(ast, "unparse") else "condition"
                cur_id = self._create_node(
                    label=f"if {test_str}",
                    node_type="conditional",
                    line=child.lineno,
                    complexity="O(1)",
                    details="Branching conditional"
                )
                self._create_edge(parent_id, cur_id, label="branch")
                # Handle then branch
                for body_stmt in child.body:
                    self._build_flow_hierarchy(ast.Module(body=[body_stmt], type_ignores=[]), parent_id=cur_id)
                # Handle else/elif
                if child.orelse:
                    else_id = self._create_node(
                        label="else",
                        node_type="conditional",
                        line=child.orelse[0].lineno if hasattr(child.orelse[0], "lineno") else child.lineno,
                        complexity="O(1)",
                        details="Alternative branch"
                    )
                    self._create_edge(cur_id, else_id, label="else")
                    for else_stmt in child.orelse:
                        self._build_flow_hierarchy(ast.Module(body=[else_stmt], type_ignores=[]), parent_id=else_id)

            elif isinstance(child, ast.Return):
                ret_val = ast.unparse(child.value) if (child.value and hasattr(ast, "unparse")) else "None"
                cur_id = self._create_node(
                    label=f"return {ret_val}",
                    node_type="return",
                    line=child.lineno,
                    complexity="O(1)",
                    details="Function return point"
                )
                self._create_edge(parent_id, cur_id, label="returns")

            elif isinstance(child, (ast.Assign, ast.AugAssign)):
                code_snippet = ast.unparse(child) if hasattr(ast, "unparse") else "assignment"
                # Keep snippet concise
                if len(code_snippet) > 35:
                    code_snippet = code_snippet[:32] + "..."
                cur_id = self._create_node(
                    label=code_snippet,
                    node_type="operation",
                    line=child.lineno,
                    complexity="O(1)",
                    details="Variable assignment/mutation"
                )
                self._create_edge(parent_id, cur_id, label="step")

            elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
                call_snippet = ast.unparse(child.value) if hasattr(ast, "unparse") else "call()"
                if len(call_snippet) > 35:
                    call_snippet = call_snippet[:32] + "..."
                cur_id = self._create_node(
                    label=call_snippet,
                    node_type="operation",
                    line=child.lineno,
                    complexity="O(1)",
                    details="Function call / statement"
                )
                self._create_edge(parent_id, cur_id, label="call")
