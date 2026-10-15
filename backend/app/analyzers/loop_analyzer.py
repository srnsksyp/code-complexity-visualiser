import ast
from typing import List, Dict, Any, Optional, Set, Tuple


class LoopInfo:
    def __init__(
        self,
        loop_id: str,
        loop_type: str,
        lineno: int,
        depth: int = 1,
        parent_id: Optional[str] = None,
        variable: Optional[str] = None,
        iterable_str: Optional[str] = None,
        bound_symbol: str = "n",
        complexity_class: str = "O(n)",
        reasoning: str = "",
        is_halving: bool = False,
        is_doubling: bool = False,
        is_binary_search: bool = False,
        is_dependent_on_outer: bool = False,
        dependent_degree: float = 1.0,
        has_break: bool = False,
    ):
        self.loop_id = loop_id
        self.loop_type = loop_type
        self.lineno = lineno
        self.depth = depth
        self.parent_id = parent_id
        self.variable = variable
        self.iterable_str = iterable_str
        self.bound_symbol = bound_symbol
        self.complexity_class = complexity_class
        self.reasoning = reasoning
        self.is_halving = is_halving
        self.is_doubling = is_doubling
        self.is_binary_search = is_binary_search
        self.is_dependent_on_outer = is_dependent_on_outer
        self.dependent_degree = dependent_degree
        self.has_break = has_break
        self.children: List["LoopInfo"] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loop_id": self.loop_id,
            "type": self.loop_type,
            "lineno": self.lineno,
            "depth": self.depth,
            "parent_id": self.parent_id,
            "variable": self.variable,
            "iterable_str": self.iterable_str,
            "bound_symbol": self.bound_symbol,
            "complexity_class": self.complexity_class,
            "reasoning": self.reasoning,
            "is_halving": self.is_halving,
            "is_binary_search": self.is_binary_search,
            "is_dependent_on_outer": self.is_dependent_on_outer,
            "dependent_degree": self.dependent_degree,
            "has_break": self.has_break,
            "children": [child.to_dict() for child in self.children],
        }


class LoopAnalyzer:
    """Analyzes loops in Python AST to determine individual, dependent, and nested asymptotic complexity."""

    def __init__(self):
        self.loops: List[LoopInfo] = []
        self._loop_counter = 0

    def analyze(self, tree: ast.AST) -> List[LoopInfo]:
        self.loops = []
        self._loop_counter = 0
        self._traverse(tree, current_parent=None, current_depth=1, outer_vars=[])
        return self.loops

    def _get_next_id(self) -> str:
        self._loop_counter += 1
        return f"loop_{self._loop_counter}"

    def _traverse(
        self,
        node: ast.AST,
        current_parent: Optional[LoopInfo],
        current_depth: int,
        outer_vars: List[str]
    ):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.For):
                loop_info = self._analyze_for_loop(child, current_parent, current_depth, outer_vars)
                if current_parent is not None:
                    current_parent.children.append(loop_info)
                else:
                    self.loops.append(loop_info)

                new_outer = list(outer_vars)
                if loop_info.variable:
                    new_outer.append(loop_info.variable)

                self._traverse(child, current_parent=loop_info, current_depth=current_depth + 1, outer_vars=new_outer)

            elif isinstance(child, ast.While):
                loop_info = self._analyze_while_loop(child, current_parent, current_depth)
                if current_parent is not None:
                    current_parent.children.append(loop_info)
                else:
                    self.loops.append(loop_info)
                self._traverse(child, current_parent=loop_info, current_depth=current_depth + 1, outer_vars=outer_vars)
            else:
                self._traverse(child, current_parent, current_depth, outer_vars)

    def _analyze_for_loop(
        self,
        node: ast.For,
        parent: Optional[LoopInfo],
        depth: int,
        outer_vars: List[str]
    ) -> LoopInfo:
        loop_id = self._get_next_id()
        lineno = getattr(node, "lineno", 0)
        var_name = self._get_target_name(node.target)

        # Check for break statement in body
        has_break = any(isinstance(c, ast.Break) for c in ast.walk(node))

        # Inspect iterable
        bound_symbol, complexity_class, reasoning, iterable_str, is_dep, dep_deg = self._inspect_for_iterable(
            node.iter, outer_vars
        )

        return LoopInfo(
            loop_id=loop_id,
            loop_type="for",
            lineno=lineno,
            depth=depth,
            parent_id=parent.loop_id if parent else None,
            variable=var_name,
            iterable_str=iterable_str,
            bound_symbol=bound_symbol,
            complexity_class=complexity_class,
            reasoning=reasoning,
            is_dependent_on_outer=is_dep,
            dependent_degree=dep_deg,
            has_break=has_break,
        )

    def _inspect_for_iterable(
        self, iter_node: ast.AST, outer_vars: List[str]
    ) -> Tuple[str, str, str, str, bool, float]:
        iterable_str = ast.unparse(iter_node) if hasattr(ast, "unparse") else "iterable"

        # Check if iter_node is range(...)
        if isinstance(iter_node, ast.Call):
            func_name = ""
            if isinstance(iter_node.func, ast.Name):
                func_name = iter_node.func.id

            if func_name == "range":
                args = iter_node.args
                if len(args) == 1:
                    stop_arg = args[0]
                elif len(args) >= 2:
                    stop_arg = args[1]
                else:
                    stop_arg = ast.Constant(value=0)

                # Check constant range
                if isinstance(stop_arg, ast.Constant) and isinstance(stop_arg.value, (int, float)):
                    if len(args) >= 2 and isinstance(args[0], ast.Constant):
                        count = max(0, int(stop_arg.value - args[0].value))
                    else:
                        count = int(stop_arg.value)
                    return "constant", "O(1)", f"Fixed range of {count} iterations.", iterable_str, False, 0.0

                # Check if stop_arg depends on an outer loop variable
                dep_var, dep_deg = self._check_outer_var_dependence(stop_arg, outer_vars)
                if dep_var:
                    if dep_deg == 2.0:
                        return (
                            dep_var,
                            "O(n²)",
                            f"Dependent quadratic loop bound '{iterable_str}' bounded by {dep_var}².",
                            iterable_str,
                            True,
                            2.0,
                        )
                    return (
                        dep_var,
                        "O(n)",
                        f"Dependent triangular loop bound '{iterable_str}' bounded by outer variable '{dep_var}'.",
                        iterable_str,
                        True,
                        1.0,
                    )

                # Check multi-variable sum range(n + m)
                if isinstance(stop_arg, ast.BinOp) and isinstance(stop_arg.op, ast.Add):
                    left_sym = self._extract_symbol(stop_arg.left)
                    right_sym = self._extract_symbol(stop_arg.right)
                    if left_sym != "constant" and right_sym != "constant":
                        return (
                            f"{left_sym}+{right_sym}",
                            f"O({left_sym}+{right_sym})",
                            f"Range bounded by sum ({left_sym} + {right_sym}).",
                            iterable_str,
                            False,
                            1.0,
                        )

                symbol = self._extract_symbol(stop_arg)
                return symbol, "O(n)", f"Range loop running {symbol} times.", iterable_str, False, 1.0

            elif func_name == "enumerate":
                if iter_node.args:
                    inner_symbol = self._extract_symbol(iter_node.args[0])
                    return inner_symbol, "O(n)", f"Enumerating over {inner_symbol}.", iterable_str, False, 1.0

        # Iterating over collection: for x in arr:
        symbol = self._extract_symbol(iter_node)
        if symbol == "constant":
            return "constant", "O(1)", "Iterating over constant collection.", iterable_str, False, 0.0

        return "n", "O(n)", f"Iterating over elements of collection '{symbol}'.", iterable_str, False, 1.0

    def _check_outer_var_dependence(self, node: ast.AST, outer_vars: List[str]) -> Tuple[Optional[str], float]:
        """Detects if a loop bound depends on an outer loop variable, and at what polynomial power."""
        if not outer_vars:
            return None, 1.0

        for var in outer_vars:
            # Direct name: range(i)
            if isinstance(node, ast.Name) and node.id == var:
                return var, 1.0

            # Quadratic: range(i * i) or range(i ** 2)
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, ast.Mult):
                    if isinstance(node.left, ast.Name) and node.left.id == var:
                        if isinstance(node.right, ast.Name) and node.right.id == var:
                            return var, 2.0
                if isinstance(node.op, ast.Pow):
                    if isinstance(node.left, ast.Name) and node.left.id == var:
                        if isinstance(node.right, ast.Constant) and node.right.value == 2:
                            return var, 2.0

            # Linear arithmetic: range(i + 1), range(n - i)
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and child.id == var:
                    return var, 1.0

        return None, 1.0

    def _extract_symbol(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return "constant"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "len" and node.args:
                if isinstance(node.args[0], ast.Name):
                    return node.args[0].id
                return "n"
            return "n"
        elif isinstance(node, ast.BinOp):
            # n // 2, 2 * n, n - 1 -> keep dominant symbol
            left = self._extract_symbol(node.left)
            right = self._extract_symbol(node.right)
            if left not in ("constant", ""):
                return left
            if right not in ("constant", ""):
                return right
            return "n"
        elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            if all(isinstance(elt, ast.Constant) for elt in node.elts):
                return "constant"
            return "n"
        return "n"

    def _analyze_while_loop(
        self, node: ast.While, parent: Optional[LoopInfo], depth: int
    ) -> LoopInfo:
        loop_id = self._get_next_id()
        lineno = getattr(node, "lineno", 0)
        cond_str = ast.unparse(node.test) if hasattr(ast, "unparse") else "condition"
        has_break = any(isinstance(c, ast.Break) for c in ast.walk(node))

        is_halving, is_doubling, is_binary_search, var_modified = self._inspect_while_body(node)
        bound_symbol = var_modified or "n"

        if is_binary_search:
            complexity_class = "O(log n)"
            reasoning = "Binary search pointer adjustment halves search range in each iteration."
        elif is_halving:
            complexity_class = "O(log n)"
            reasoning = f"Loop repeatedly halves variable '{bound_symbol}', yielding logarithmic O(log n) iterations."
        elif is_doubling:
            complexity_class = "O(log n)"
            reasoning = f"Loop repeatedly doubles variable '{bound_symbol}', reaching boundary in O(log n) steps."
        else:
            complexity_class = "O(n)"
            reasoning = f"While loop condition '{cond_str}' appears to iterate proportionally to input size."

        return LoopInfo(
            loop_id=loop_id,
            loop_type="while",
            lineno=lineno,
            depth=depth,
            parent_id=parent.loop_id if parent else None,
            variable=var_modified,
            iterable_str=cond_str,
            bound_symbol=bound_symbol,
            complexity_class=complexity_class,
            reasoning=reasoning,
            is_halving=is_halving,
            is_doubling=is_doubling,
            is_binary_search=is_binary_search,
            has_break=has_break,
        )

    def _inspect_while_body(self, while_node: ast.While) -> Tuple[bool, bool, bool, Optional[str]]:
        is_halving = False
        is_doubling = False
        is_binary_search = False
        target_var = None

        has_mid_calc = False
        updates_low_or_high = False

        for body_node in ast.walk(while_node):
            if isinstance(body_node, ast.Assign):
                for t in body_node.targets:
                    if isinstance(t, ast.Name):
                        name = t.id
                        if name == "mid":
                            has_mid_calc = True
                        if name in ("low", "high", "left", "right"):
                            updates_low_or_high = True

                        if isinstance(body_node.value, ast.BinOp):
                            if isinstance(body_node.value.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                                if isinstance(body_node.value.left, ast.Name) and body_node.value.left.id == name:
                                    is_halving = True
                                    target_var = name
                            elif isinstance(body_node.value.op, (ast.Mult, ast.LShift)):
                                if isinstance(body_node.value.left, ast.Name) and body_node.value.left.id == name:
                                    is_doubling = True
                                    target_var = name

            elif isinstance(body_node, ast.AugAssign):
                if isinstance(body_node.target, ast.Name):
                    name = body_node.target.id
                    if isinstance(body_node.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                        is_halving = True
                        target_var = name
                    elif isinstance(body_node.op, (ast.Mult, ast.LShift)):
                        is_doubling = True
                        target_var = name
                    elif name in ("low", "high", "left", "right"):
                        updates_low_or_high = True

        if has_mid_calc and updates_low_or_high:
            is_binary_search = True
            is_halving = True
            target_var = "search_interval"

        return is_halving, is_doubling, is_binary_search, target_var

    def _get_target_name(self, target: ast.AST) -> str:
        if isinstance(target, ast.Name):
            return target.id
        elif isinstance(target, (ast.Tuple, ast.List)):
            names = [elt.id for elt in target.elts if isinstance(elt, ast.Name)]
            return ", ".join(names) if names else "item"
        return "item"
