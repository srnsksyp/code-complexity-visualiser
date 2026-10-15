import ast
from typing import Dict, Any, List, Optional, Tuple, Set
from app.analyzers.complexity_classes import ComplexityClass
from app.analyzers.recurrence_solver import RecurrenceRelation, RecurrenceSolver


class RecursionCallSite:
    """Detailed record of a single recursive call site in the AST."""

    def __init__(
        self,
        call_id: str,
        lineno: int,
        arg_snippets: List[str],
        is_in_loop: bool = False,
        loop_bound: Optional[str] = None,
        branch_context: str = "main",
    ):
        self.call_id = call_id
        self.lineno = lineno
        self.arg_snippets = arg_snippets
        self.is_in_loop = is_in_loop
        self.loop_bound = loop_bound
        self.branch_context = branch_context


class RecursionAnalyzer:
    """Extracts call sites, control-flow execution paths, argument transformations, and symbolic recurrences."""

    def analyze(self, tree: ast.AST) -> List[RecurrenceRelation]:
        results: List[RecurrenceRelation] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                rel = self._analyze_function(node, func_name)
                if rel is not None:
                    # Solve the extracted recurrence relation
                    solved_rel = RecurrenceSolver.solve(rel)
                    results.append(solved_rel)

        return results

    def _analyze_function(self, func_node: ast.FunctionDef, func_name: str) -> Optional[RecurrenceRelation]:
        # 1. Collect all recursive calls
        recursive_calls: List[ast.Call] = []
        for child in ast.walk(func_node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id == func_name:
                    recursive_calls.append(child)

        if not recursive_calls:
            return None

        param_names = [arg.arg for arg in func_node.args.args]
        total_call_sites = len(recursive_calls)

        # 2. Check for memoization (e.g. @cache, @lru_cache, or memo[key] dictionary usage)
        has_memoization, state_space = self._detect_memoization(func_node, param_names)

        # 3. Check if any recursive call is enclosed inside a loop (e.g. for i in range(n): f(n-1))
        in_loop, loop_bound = self._check_recursion_in_loop(func_node, func_name)

        # 4. Calculate worst-case branching factor along any single execution path
        worst_case_branches = self._calculate_worst_case_branches(func_node.body, func_name)
        if worst_case_branches == 0:
            worst_case_branches = total_call_sites

        # 5. Analyze argument transformations across recursive calls
        reduction_type, step_size = self._analyze_argument_transformations(
            func_node, recursive_calls, param_names
        )

        if in_loop:
            reduction_type = "in_loop"

        # 6. Check for leaf output materialization and full output retention
        # e.g. result.append(list(current)) -> leaf output work O(n), retains all outputs
        leaf_output_work, retains_all = self._inspect_leaf_and_output(func_node, param_names)

        # 7. Check local non-recursive work per frame (e.g. slicing, loop, etc.)
        local_work = self._inspect_local_work(func_node)

        # Canonical input size variable
        canonical_var = "n"
        if param_names:
            first_p = param_names[0]
            if first_p in ("m", "k", "W"):
                canonical_var = first_p

        rel = RecurrenceRelation(
            func_name=func_name,
            branching_factor=worst_case_branches,
            total_call_sites=total_call_sites,
            reduction_type=reduction_type,
            step_size=step_size,
            local_work=local_work,
            has_memoization=has_memoization,
            state_space=state_space,
            parameter_names=[canonical_var],
            leaf_output_work=leaf_output_work,
            retains_all_outputs=retains_all,
            recursion_inside_loop_size=loop_bound,
        )

        return rel

    def _calculate_worst_case_branches(self, stmts: List[ast.stmt], func_name: str) -> int:
        """Computes the maximum number of recursive calls that execute along any single control-flow path."""
        calls_on_path = 0

        for stmt in stmts:
            if isinstance(stmt, ast.If):
                # Count calls in the test condition (always evaluated)
                test_calls = self._count_calls_in_expr(stmt.test, func_name)
                # Either body executes OR orelse executes
                body_calls = self._calculate_worst_case_branches(stmt.body, func_name)
                orelse_calls = self._calculate_worst_case_branches(stmt.orelse, func_name) if stmt.orelse else 0
                calls_on_path += test_calls + max(body_calls, orelse_calls)

            elif isinstance(stmt, (ast.For, ast.While)):
                # If a loop has a recursive call, it will execute repeatedly per frame
                loop_calls = self._calculate_worst_case_branches(stmt.body, func_name)
                if loop_calls > 0:
                    # Enclosed in loop, will be handled by in_loop flag
                    calls_on_path += loop_calls
                else:
                    calls_on_path += 0

            elif isinstance(stmt, (ast.Assign, ast.AugAssign)):
                calls_on_path += self._count_calls_in_expr(stmt.value, func_name)

            elif isinstance(stmt, ast.Expr):
                calls_on_path += self._count_calls_in_expr(stmt.value, func_name)

            elif isinstance(stmt, ast.Return):
                if stmt.value:
                    calls_on_path += self._count_calls_in_expr(stmt.value, func_name)

        return calls_on_path

    def _count_calls_in_expr(self, node: ast.AST, func_name: str) -> int:
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == func_name:
                count += 1
        return count

    def _check_recursion_in_loop(self, func_node: ast.AST, func_name: str) -> Tuple[bool, Optional[str]]:
        for node in ast.walk(func_node):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == func_name:
                        # Extract loop bound
                        bound = "n"
                        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
                            if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range" and node.iter.args:
                                bound = ast.unparse(node.iter.args[-1]) if hasattr(ast, "unparse") else "n"
                        return True, bound
        return False, None

    def _detect_memoization(self, func_node: ast.FunctionDef, param_names: List[str]) -> Tuple[bool, Optional[str]]:
        # Check decorators: @cache, @lru_cache
        for dec in func_node.decorator_list:
            dec_id = ""
            if isinstance(dec, ast.Name):
                dec_id = dec.id
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                dec_id = dec.func.id
            elif isinstance(dec, ast.Attribute):
                dec_id = dec.attr

            if "cache" in dec_id.lower():
                return True, f"Θ({'*'.join(param_names[:2])})" if len(param_names) >= 2 else "Θ(n)"

        # Check in-body cache access: memo[key], cache[key]
        has_dict_lookup = False
        has_dict_store = False
        has_key_tuple = False

        for node in ast.walk(func_node):
            if isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name) and any(kw in node.value.id.lower() for kw in ("memo", "cache", "dp")):
                    has_dict_lookup = True
                    if isinstance(node.slice, ast.Tuple):
                        has_key_tuple = True
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                        if any(kw in target.value.id.lower() for kw in ("memo", "cache", "dp")):
                            has_dict_store = True

        if has_dict_lookup and has_dict_store:
            if has_key_tuple and any("cap" in p.lower() or "weight" in p.lower() for p in param_names):
                return True, "Θ(n*W)"
            return True, "Θ(n)"

        return False, None

    def _analyze_argument_transformations(
        self, func_node: ast.FunctionDef, recursive_calls: List[ast.Call], param_names: List[str]
    ) -> Tuple[str, float]:
        is_halving = False
        is_subtraction = False
        is_addition_to_bound = False
        step = 1.0

        for call in recursive_calls:
            for idx, arg in enumerate(call.args):
                # Halving: n // 2, n / 2, mid - 1
                if isinstance(arg, ast.BinOp):
                    if isinstance(arg.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                        is_halving = True
                        step = 2.0
                    elif isinstance(arg.op, ast.Sub):
                        is_subtraction = True
                        if isinstance(arg.right, ast.Constant) and isinstance(arg.right.value, (int, float)):
                            step = max(step, float(arg.right.value))
                    elif isinstance(arg.op, ast.Add):
                        is_addition_to_bound = True
                        if isinstance(arg.right, ast.Constant) and isinstance(arg.right.value, (int, float)):
                            step = max(step, float(arg.right.value))

                # Slicing: arr[:mid], arr[mid:] -> halving; arr[1:] -> linear decrement
                elif isinstance(arg, ast.Subscript) and isinstance(arg.slice, ast.Slice):
                    sl = arg.slice
                    is_slice_half = False
                    for slice_bound in (sl.lower, sl.upper):
                        if slice_bound is not None:
                            if isinstance(slice_bound, ast.Name) and "mid" in slice_bound.id.lower():
                                is_slice_half = True
                            elif isinstance(slice_bound, ast.BinOp) and isinstance(slice_bound.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                                is_slice_half = True

                    if is_slice_half:
                        is_halving = True
                        step = 2.0
                    elif sl.lower is not None:
                        is_subtraction = True
                        step = 1.0

        # Check for multi-term decrement like fib(n-1) + fib(n-2)
        distinct_steps: Set[float] = set()
        for call in recursive_calls:
            for arg in call.args:
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Sub):
                    if isinstance(arg.right, ast.Constant) and isinstance(arg.right.value, (int, float)):
                        distinct_steps.add(float(arg.right.value))

        if len(distinct_steps) >= 2 and 1.0 in distinct_steps and 2.0 in distinct_steps:
            return "multi_term", 1.0

        if is_halving:
            return "divide_and_conquer", 2.0

        if is_subtraction or is_addition_to_bound:
            return "linear_decrement", step

        # Default linear decrement
        return "linear_decrement", 1.0

    def _inspect_leaf_and_output(
        self, func_node: ast.FunctionDef, param_names: List[str]
    ) -> Tuple[Optional[ComplexityClass], bool]:
        """Detects if base case or body copies/materializes output items (e.g. list(current))."""
        has_list_copy = False
        retains_all = False

        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                # Check list(current) or copy.copy(current)
                if isinstance(node.func, ast.Name) and node.func.id == "list":
                    has_list_copy = True
                elif isinstance(node.func, ast.Attribute) and node.func.attr == "copy":
                    has_list_copy = True
                elif isinstance(node.func, ast.Attribute) and node.func.attr == "append":
                    # result.append(...)
                    if isinstance(node.func.value, ast.Name) and "result" in node.func.value.id.lower():
                        retains_all = True
            elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
                # current[:] full slice copy
                if node.slice.lower is None and node.slice.upper is None:
                    has_list_copy = True

        leaf_work = ComplexityClass.linear("n") if has_list_copy else None
        return leaf_work, retains_all

    def _inspect_local_work(self, func_node: ast.FunctionDef) -> ComplexityClass:
        """Inspects non-recursive work per execution frame (e.g. loops or slicing)."""
        has_loop = False
        for child in ast.iter_child_nodes(func_node):
            if isinstance(child, (ast.For, ast.While)):
                has_loop = True

        if has_loop:
            return ComplexityClass.linear("n")
        return ComplexityClass.constant()
