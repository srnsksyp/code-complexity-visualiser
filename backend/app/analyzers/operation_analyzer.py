import ast
from typing import List, Dict, Any, Tuple, Set


class OperationReport:
    def __init__(self):
        self.operations: List[Dict[str, Any]] = []
        self.max_operation_cost: str = "O(1)"
        self.has_sorting: bool = False
        self.has_linear_search_in_loop: bool = False
        self.has_quadratic_insert: bool = False
        self.has_repeated_sort_in_loop: bool = False
        self.has_string_concat_in_loop: bool = False
        self.has_list_copy: bool = False
        self.detected_allocations: List[Dict[str, Any]] = []
        self.space_complexity_from_allocations: str = "O(1)"
        self.space_reasoning: List[str] = []
        self.optimization_hints: List[str] = []


class OperationAnalyzer:
    """Analyzes built-in operations, container allocations, performance pitfalls, and Python cost model."""

    def analyze(self, tree: ast.AST) -> OperationReport:
        report = OperationReport()
        self._inspect_allocations(tree, report)
        self._inspect_calls_and_operations(tree, report)
        return report

    def _inspect_allocations(self, tree: ast.AST, report: OperationReport):
        """Detects data structure creations like [0]*n or [[0]*n for _ in range(n)]."""
        for node in ast.walk(tree):
            # Check 2D matrix comprehension: [[0 for _ in range(n)] for _ in range(n)]
            # or [[0] * n for _ in range(n)]
            if isinstance(node, ast.ListComp):
                is_matrix = False
                if isinstance(node.elt, ast.BinOp) and isinstance(node.elt.op, ast.Mult):
                    is_matrix = True
                elif isinstance(node.elt, ast.ListComp):
                    is_matrix = True

                if is_matrix:
                    report.detected_allocations.append({
                        "type": "2D Matrix / Grid",
                        "complexity": "O(n²)",
                        "line": getattr(node, "lineno", 0),
                        "snippet": "Nested list comprehension / matrix allocation"
                    })
                    report.space_complexity_from_allocations = "O(n²)"
                    report.space_reasoning.append(
                        "Allocates a 2D matrix / nested list proportional to n × n, requiring O(n²) auxiliary space."
                    )
                else:
                    if report.space_complexity_from_allocations != "O(n²)":
                        report.detected_allocations.append({
                            "type": "1D List Comprehension",
                            "complexity": "O(n)",
                            "line": getattr(node, "lineno", 0),
                            "snippet": "List comprehension allocation"
                        })
                        report.space_complexity_from_allocations = "O(n)"
                        report.space_reasoning.append(
                            "List comprehension creates a new collection sized proportionally to input, requiring O(n) auxiliary space."
                        )

            # Check list multiplication: [0] * n or n * [0]
            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
                is_list_mult = False
                var_operand = "n"

                if isinstance(node.left, ast.List) and isinstance(node.right, (ast.Name, ast.Call)):
                    is_list_mult = True
                    var_operand = ast.unparse(node.right) if hasattr(ast, "unparse") else "n"
                elif isinstance(node.right, ast.List) and isinstance(node.left, (ast.Name, ast.Call)):
                    is_list_mult = True
                    var_operand = ast.unparse(node.left) if hasattr(ast, "unparse") else "n"

                if is_list_mult and report.space_complexity_from_allocations != "O(n²)":
                    report.detected_allocations.append({
                        "type": "Linear Array Allocation",
                        "complexity": "O(n)",
                        "line": getattr(node, "lineno", 0),
                        "snippet": f"[...] * {var_operand}"
                    })
                    report.space_complexity_from_allocations = "O(n)"
                    report.space_reasoning.append(
                        f"List multiplication '[...] * {var_operand}' allocates an array proportional to {var_operand}, requiring O(n) auxiliary space."
                    )

    def _inspect_calls_and_operations(self, tree: ast.AST, report: OperationReport):
        loop_nodes: Set[int] = set()

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for descendant in ast.walk(node):
                    if descendant is not node:
                        loop_nodes.add(id(descendant))

        for node in ast.walk(tree):
            in_loop = id(node) in loop_nodes
            lineno = getattr(node, "lineno", 0)

            # Repeated string concatenation inside loop: s += c
            if in_loop and isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Add):
                # Check if target is likely string
                report.has_string_concat_in_loop = True
                report.optimization_hints.append(
                    f"Repeated accumulation ('+=') inside a loop on line {lineno}. "
                    "If concatenating strings, this creates a new string copy each iteration (O(n²)); "
                    "consider accumulating into a list and using ''.join(...) for linear O(n) time."
                )

            # Slicing detection: lst[1:], s[:k]
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
                report.operations.append({
                    "name": "slice",
                    "cost": "O(k)",
                    "line": lineno,
                    "in_loop": in_loop
                })

            # List copying: list(current), current.copy()
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in ("list", "copy"):
                    report.has_list_copy = True
                    report.operations.append({
                        "name": "list_copy",
                        "cost": "O(n)",
                        "line": lineno,
                        "in_loop": in_loop
                    })

                elif func_name in ("sorted", "sort"):
                    report.has_sorting = True
                    report.operations.append({
                        "name": func_name,
                        "cost": "O(n log n)",
                        "line": lineno,
                        "in_loop": in_loop
                    })
                    if in_loop:
                        report.has_repeated_sort_in_loop = True
                        report.optimization_hints.append(
                            f"Repeated sorting '{func_name}' detected inside a loop on line {lineno}. "
                            "Sorting repeatedly inside an iteration can degrade performance to O(n² log n); "
                            "consider sorting once before the loop."
                        )

                elif func_name == "insert" and isinstance(node.func, ast.Attribute):
                    if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 0:
                        report.has_quadratic_insert = True
                        if in_loop:
                            report.optimization_hints.append(
                                f"List insert at index 0 ('insert(0, ...)') detected inside a loop on line {lineno}. "
                                "Inserting at the beginning shifts all elements (O(n) per call); "
                                "consider using 'collections.deque' for O(1) appends to the left."
                            )

                elif func_name in ("min", "max", "sum"):
                    report.operations.append({
                        "name": func_name,
                        "cost": "O(n)",
                        "line": lineno,
                        "in_loop": in_loop
                    })

            # Membership test: 'x in lst'
            elif isinstance(node, ast.Compare):
                for op in node.ops:
                    if isinstance(op, (ast.In, ast.NotIn)):
                        report.operations.append({
                            "name": "membership",
                            "cost": "O(n) for list, O(1) for set/dict",
                            "line": lineno,
                            "in_loop": in_loop
                        })
                        if in_loop:
                            report.has_linear_search_in_loop = True
                            report.optimization_hints.append(
                                f"Membership check ('in' operator) detected inside a loop on line {lineno}. "
                                "If the container is a list, each check takes O(n), creating an O(n²) bottleneck. "
                                "Consider converting the container to a 'set' or 'dict' for average O(1) lookups."
                            )
