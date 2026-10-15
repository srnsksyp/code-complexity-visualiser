import ast
import math
from typing import List, Dict, Any, Tuple
from app.analyzers.loop_analyzer import LoopAnalyzer, LoopInfo
from app.analyzers.recursion_analyzer import RecursionAnalyzer
from app.analyzers.recurrence_solver import RecurrenceRelation
from app.analyzers.operation_analyzer import OperationAnalyzer, OperationReport
from app.analyzers.structure_analyzer import StructureAnalyzer
from app.analyzers.complexity_classes import ComplexityClass
from app.schemas.analysis import (
    AnalyzeResponse,
    CodeStatistics,
    CodeStructureData,
    TheoreticalGraphData,
    SpaceBreakdown,
    RecurrenceInfo,
)


class ComplexityAnalyzer:
    """Coordinates static loop, recurrence, operation, and structural analyses into mathematically sound Big-O derivations."""

    def __init__(self):
        self.loop_analyzer = LoopAnalyzer()
        self.recursion_analyzer = RecursionAnalyzer()
        self.operation_analyzer = OperationAnalyzer()
        self.structure_analyzer = StructureAnalyzer()

    def analyze(self, tree: ast.AST) -> AnalyzeResponse:
        # 1. Run component analyzers
        loops = self.loop_analyzer.analyze(tree)
        recurrence_relations = self.recursion_analyzer.analyze(tree)
        op_report = self.operation_analyzer.analyze(tree)

        has_recursion = len(recurrence_relations) > 0
        stats, structure = self.structure_analyzer.analyze(
            tree,
            recursion_detected=has_recursion,
            recursion_count=len(recurrence_relations)
        )

        # 2. Determine Time Complexity, Tight Bound, Space Breakdown, Confidence, and Derivation
        (
            time_comp,
            tight_bound,
            space_comp,
            space_breakdown,
            confidence,
            confidence_reasons,
            reasoning,
            detected_patterns,
            recurrence_info,
        ) = self._compute_complexities(loops, recurrence_relations, op_report, stats)

        # 3. Generate rule-based optimization suggestions
        optimization_suggestions = list(op_report.optimization_hints)
        self._add_algorithmic_suggestions(time_comp, space_comp, recurrence_relations, loops, optimization_suggestions)

        # 4. Generate theoretical growth graph data
        graph_data = self._generate_graph_data(time_comp)

        return AnalyzeResponse(
            success=(confidence != "UNSUPPORTED"),
            time_complexity=time_comp,
            tight_bound=tight_bound,
            space_complexity=space_comp,
            space_breakdown=space_breakdown,
            confidence=confidence,
            confidence_reasons=confidence_reasons,
            complexity_reasoning=reasoning,
            recurrence=recurrence_info,
            statistics=stats,
            detected_patterns=detected_patterns,
            optimization_suggestions=optimization_suggestions,
            structure=structure,
            graph=graph_data,
            functions=[r.to_dict() for r in recurrence_relations],
            loops=[loop.to_dict() for loop in loops],
            recursion=recurrence_relations[0].to_dict() if recurrence_relations else {},
        )

    def _compute_complexities(
        self,
        loops: List[LoopInfo],
        recursions: List[RecurrenceRelation],
        op_report: OperationReport,
        stats: CodeStatistics
    ) -> Tuple[str, str, str, SpaceBreakdown, str, List[str], str, List[str], RecurrenceInfo]:
        detected_patterns: List[str] = []
        confidence_reasons: List[str] = []

        # ----------------------------------------------------
        # BRANCH A: RECURSIVE FUNCTION DETECTED
        # ----------------------------------------------------
        if recursions:
            rel = recursions[0]
            detected_patterns.append(f"Recursive function '{rel.func_name}'")
            if rel.branching_factor > 1:
                detected_patterns.append(f"Worst-case branching factor: {rel.branching_factor}")
            else:
                detected_patterns.append("Single recursive call per execution path")

            if rel.has_memoization:
                detected_patterns.append("Memoization / State-space cache detected")
            if rel.retains_all_outputs:
                detected_patterns.append(f"Output accumulation: {rel.output_space_class.big_o}")

            time_comp = rel.solved_complexity.big_o
            tight_bound = rel.solved_complexity.tight_bound
            space_comp = rel.total_retained_space_class.big_o

            # If additional heap structures allocated in body
            if op_report.space_complexity_from_allocations in ("O(n²)", "O(n)"):
                if op_report.space_complexity_from_allocations == "O(n²)":
                    space_comp = "O(n²)"
                detected_patterns.append(f"Auxiliary heap memory: {op_report.space_complexity_from_allocations}")

            space_breakdown = SpaceBreakdown(
                auxiliary=rel.auxiliary_space_class.big_o,
                recursion_stack=rel.stack_depth_class.big_o,
                output=rel.output_space_class.big_o,
                total_retained=space_comp,
            )

            rec_info = RecurrenceInfo(
                present=True,
                expression=rel.recurrence_str,
                is_solved=rel.is_solved,
                branching_factor=rel.branching_factor,
                total_call_sites=rel.total_call_sites,
                derivation_steps=rel.derivation_steps,
            )

            reasoning = " ".join(rel.derivation_steps)
            confidence = rel.confidence
            confidence_reasons = rel.confidence_reasons

            return (
                time_comp,
                tight_bound,
                space_comp,
                space_breakdown,
                confidence,
                confidence_reasons,
                reasoning,
                detected_patterns,
                rec_info,
            )

        # ----------------------------------------------------
        # BRANCH B: ITERATIVE LOOPS DETECTED
        # ----------------------------------------------------
        if loops:
            loop_class, loop_reasoning, loop_patterns, loop_confidence, loop_evidence = self._evaluate_loop_trees(loops)
            detected_patterns.extend(loop_patterns)
            confidence_reasons.extend(loop_evidence)

            time_comp = loop_class.big_o
            tight_bound = loop_class.tight_bound

            # Space complexity from auxiliary allocations
            if op_report.space_complexity_from_allocations != "O(1)":
                space_comp = op_report.space_complexity_from_allocations
                detected_patterns.append(f"Auxiliary memory allocation: {space_comp}")
                reasoning = f"{loop_reasoning} " + " ".join(op_report.space_reasoning)
            else:
                space_comp = "O(1)"
                detected_patterns.append("O(1) scalar auxiliary memory")
                reasoning = f"{loop_reasoning} Only scalar auxiliary variables are allocated, maintaining O(1) auxiliary space."

            space_breakdown = SpaceBreakdown(
                auxiliary=space_comp,
                recursion_stack="O(1)",
                output="O(1)",
                total_retained=space_comp,
            )

            rec_info = RecurrenceInfo(present=False)
            return (
                time_comp,
                tight_bound,
                space_comp,
                space_breakdown,
                loop_confidence,
                confidence_reasons,
                reasoning,
                detected_patterns,
                rec_info,
            )

        # ----------------------------------------------------
        # BRANCH C: NO LOOPS & NO RECURSION (SCALAR / COMPREHENSION / SORT)
        # ----------------------------------------------------
        if stats.comprehension_count > 0:
            time_comp = "O(n)"
            tight_bound = "Θ(n)"
            space_comp = op_report.space_complexity_from_allocations if op_report.space_complexity_from_allocations != "O(1)" else "O(n)"
            confidence = "HIGH"
            confidence_reasons = ["Collection comprehension iterating over input items."]
            detected_patterns.append("List/Collection comprehension")
            reasoning = "No explicit loops or recursion detected. Code contains a collection comprehension iterating over input elements in linear O(n) time."
            space_breakdown = SpaceBreakdown(
                auxiliary=space_comp, recursion_stack="O(1)", output="O(1)", total_retained=space_comp
            )
            return time_comp, tight_bound, space_comp, space_breakdown, confidence, confidence_reasons, reasoning, detected_patterns, RecurrenceInfo(present=False)

        if op_report.has_sorting:
            time_comp = "O(n log n)"
            tight_bound = "Θ(n log n)"
            space_comp = "O(n)"
            confidence = "HIGH"
            confidence_reasons = ["Direct invocation of Python Timsort (O(n log n))."]
            detected_patterns.append("Sorting operation (Timsort)")
            reasoning = "Direct invocation of sorting algorithm requires O(n log n) comparison time and O(n) temporary storage."
            space_breakdown = SpaceBreakdown(
                auxiliary="O(n)", recursion_stack="O(1)", output="O(1)", total_retained="O(n)"
            )
            return time_comp, tight_bound, space_comp, space_breakdown, confidence, confidence_reasons, reasoning, detected_patterns, RecurrenceInfo(present=False)

        # Pure constant scalar execution
        time_comp = "O(1)"
        tight_bound = "Θ(1)"
        space_comp = op_report.space_complexity_from_allocations
        confidence = "HIGH"
        confidence_reasons = ["Sequential scalar instructions without loops, recursion, or dynamic growth."]

        if space_comp != "O(1)":
            reasoning = (
                f"The code executes scalar operations in constant O(1) time, but allocates "
                f"auxiliary data structures requiring {space_comp} space. "
                + " ".join(op_report.space_reasoning)
            )
            detected_patterns.append(f"Auxiliary memory allocation: {space_comp}")
        else:
            reasoning = "The code executes a fixed sequence of scalar operations with no loops, recursions, or variable allocations. Both execution time and memory remain constant O(1)."
            detected_patterns.append("Constant-time sequential instructions")

        space_breakdown = SpaceBreakdown(
            auxiliary=space_comp, recursion_stack="O(1)", output="O(1)", total_retained=space_comp
        )
        return time_comp, tight_bound, space_comp, space_breakdown, confidence, confidence_reasons, reasoning, detected_patterns, RecurrenceInfo(present=False)

    def _evaluate_loop_trees(
        self, loops: List[LoopInfo]
    ) -> Tuple[ComplexityClass, str, List[str], str, List[str]]:
        tree_results: List[Tuple[ComplexityClass, int, str, List[str], str, List[str]]] = []

        for root in loops:
            res = self._evaluate_single_loop_node(root)
            tree_results.append(res)

        # Sequential root loops: max(tree1, tree2, ...)
        best_class = ComplexityClass.constant()
        all_patterns: List[str] = []
        all_reasons: List[str] = []
        all_evidence: List[str] = []
        overall_conf = "HIGH"

        for comp_class, depth, reason, patterns, conf, evidence in tree_results:
            all_patterns.extend(patterns)
            all_reasons.append(reason)
            all_evidence.extend(evidence)
            if comp_class > best_class:
                best_class = comp_class
            if conf != "HIGH":
                overall_conf = conf

        if len(loops) > 1:
            all_patterns.append(f"{len(loops)} independent sequential loop blocks")
            final_reason = (
                f"Detected {len(loops)} sequential loop blocks. In asymptotic analysis, sequential blocks add: "
                f"O(f(n)) + O(g(n)) = O(max(f(n), g(n))). The dominant block determines the overall time complexity of {best_class.big_o}. "
                + " ".join(all_reasons)
            )
        else:
            final_reason = " ".join(all_reasons)

        return best_class, final_reason, list(dict.fromkeys(all_patterns)), overall_conf, all_evidence

    def _evaluate_single_loop_node(
        self, node: LoopInfo
    ) -> Tuple[ComplexityClass, int, str, List[str], str, List[str]]:
        patterns: List[str] = []
        evidence: List[str] = []
        conf = "HIGH"

        if node.is_binary_search:
            patterns.append("Binary search logarithmic halving")
            current_class = ComplexityClass.logarithmic()
            evidence.append("Loop pointers halve the search interval each step.")
        elif node.is_halving or node.is_doubling:
            patterns.append("Logarithmic variable update in while loop")
            current_class = ComplexityClass.logarithmic()
            evidence.append("While loop variable halves/doubles each iteration.")
        elif node.complexity_class == "O(1)":
            patterns.append("Fixed-bound constant loop")
            current_class = ComplexityClass.constant()
            evidence.append(f"Constant bound of iterations: {node.bound_symbol}.")
        elif "+" in node.bound_symbol:
            current_class = ComplexityClass.multi_variable(node.bound_symbol)
            patterns.append(f"Multi-variable sum bound: {node.bound_symbol}")
            evidence.append(f"Range bound bounded by multi-variable expression: {node.bound_symbol}.")
        elif node.is_dependent_on_outer:
            if node.dependent_degree == 2.0:
                current_class = ComplexityClass.polynomial(2.0)
                patterns.append(f"Dependent quadratic loop bound {node.bound_symbol}²")
            else:
                current_class = ComplexityClass.linear()
                patterns.append(f"Dependent triangular loop bound {node.bound_symbol}")
        else:
            var_name = node.bound_symbol if node.bound_symbol in ("m", "k", "W") else "n"
            current_class = ComplexityClass.linear(var_name)
            patterns.append(f"Loop bounded by {node.bound_symbol}")
            evidence.append(f"Iteration bounded linearly by '{node.bound_symbol}'.")

        # If no nested children
        if not node.children:
            return current_class, 1, node.reasoning, patterns, conf, evidence

        # Has nested children: evaluate children
        child_results = [self._evaluate_single_loop_node(c) for c in node.children]
        max_child_class = ComplexityClass.constant()
        max_child_depth = 1
        child_reasons = []

        for c_class, depth, reason, c_patterns, c_conf, c_evidence in child_results:
            patterns.extend(c_patterns)
            evidence.extend(c_evidence)
            child_reasons.append(reason)
            if c_class > max_child_class:
                max_child_class = c_class
                max_child_depth = depth
            if c_conf != "HIGH":
                conf = c_conf

        current_depth = 1 + max_child_depth
        patterns.append(f"Nested loop structure (depth {current_depth})")

        # Check dependent bound combination:
        # e.g., outer is O(n), inner is dependent on outer var i:
        # sum_(i=0)^n i = O(n²)
        # sum_(i=0)^n i² = O(n³)
        first_child = node.children[0]
        if first_child.is_dependent_on_outer:
            if first_child.dependent_degree == 2.0:
                combined_class = ComplexityClass.polynomial(3.0)
                reasoning = (
                    f"Outer loop iterates up to n, and inner loop has dependent quadratic bound i². "
                    "Summing sum_(i=0)^n i² = n(n+1)(2n+1)/6 yields cubic O(n³) asymptotic time."
                )
            else:
                combined_class = ComplexityClass.polynomial(2.0)
                reasoning = (
                    f"Outer loop iterates up to n, and inner loop has dependent triangular bound i. "
                    "Summing sum_(i=0)^n i = n(n-1)/2 yields quadratic O(n²) asymptotic time."
                )
            return combined_class, current_depth, reasoning, patterns, conf, evidence

        # Multiplicative nesting:
        combined_class = ComplexityClass.multiply(current_class, max_child_class)

        if current_class.category == "linear" and max_child_class.category == "linear":
            child_symbol = first_child.bound_symbol
            if node.bound_symbol != child_symbol and child_symbol not in ("constant", "n"):
                reasoning = (
                    f"Outer loop iterates over '{node.bound_symbol}' and inner loop iterates over '{child_symbol}'. "
                    f"Total time is {combined_class.big_o}."
                )
            else:
                reasoning = (
                    "Two nested loops iterate over input size n. For every outer iteration, the inner loop "
                    f"runs up to n times, producing n × n = {combined_class.big_o} total iterations."
                )
        elif combined_class.poly_degree >= 3.0:
            deg = int(combined_class.poly_degree)
            reasoning = f"{current_depth} nested loops each scaling proportionally with input size, multiplying to O(n^{deg}) asymptotic time."
        else:
            reasoning = f"Nested loop combination is dominated by {combined_class.big_o}."

        return combined_class, current_depth, reasoning, patterns, conf, evidence

    def _add_algorithmic_suggestions(
        self,
        time_comp: str,
        space_comp: str,
        recursions: List[RecurrenceRelation],
        loops: List[LoopInfo],
        suggestions: List[str]
    ):
        if "²" in time_comp or "³" in time_comp or "*" in time_comp:
            suggestions.append(
                "Polynomial nested loop detected: If searching for pairs or matches, consider whether a Hash Table (dict/set) "
                "or two-pointer approach on a pre-sorted list could reduce the complexity to O(n) or O(n log n)."
            )

        if recursions and any(r.branching_factor >= 2 for r in recursions):
            if not any(r.has_memoization for r in recursions):
                suggestions.append(
                    "Branching recursion detected with exponential growth: "
                    "Consider applying Dynamic Programming (memoization or tabulation) "
                    "to cache intermediate subproblem results and reduce time to polynomial O(n) or pseudo-polynomial O(n*W)."
                )

        if "²" in space_comp or "2^n" in space_comp:
            suggestions.append(
                "High auxiliary/output space allocation detected: Verify if intermediate data can be streamed/yielded "
                "via generators instead of buffering all results simultaneously in memory."
            )

    def _generate_graph_data(self, active_complexity: str) -> TheoreticalGraphData:
        """Generates mathematical asymptotic growth curves for comparison across all major classes."""
        sample_n = [1, 2, 4, 8, 16, 32, 64]
        points: List[Dict[str, Any]] = []

        for n in sample_n:
            log_val = round(math.log2(n), 2) if n > 1 else 0.0
            n_log_n = round(n * math.log2(n), 2) if n > 1 else 0.0
            n2 = n * n
            n3 = min(n * n * n, 5000.0)
            exp2 = min(float(2 ** n), 5000.0)
            exp3 = min(float(3 ** n), 5000.0)
            fact = min(float(math.factorial(min(n, 8))), 5000.0)

            points.append({
                "n": n,
                "O(1)": 1.0,
                "O(log n)": log_val,
                "O(n)": float(n),
                "O(n log n)": n_log_n,
                "O(n²)": float(min(n2, 5000.0)),
                "O(n³)": float(n3),
                "O(2^n)": float(exp2),
                "O(3^n)": float(exp3),
                "O(n!)": float(fact),
            })

        # Match active complexity string to closest curve name for UI highlight
        canonical_active = "O(1)"
        if "!" in active_complexity:
            canonical_active = "O(n!)"
        elif "3^" in active_complexity:
            canonical_active = "O(3^n)"
        elif "2^" in active_complexity:
            canonical_active = "O(2^n)"
        elif "⁴" in active_complexity or "^4" in active_complexity or "³" in active_complexity or "^3" in active_complexity:
            canonical_active = "O(n³)"
        elif "²" in active_complexity or "^2" in active_complexity or "*" in active_complexity:
            canonical_active = "O(n²)"
        elif "log" in active_complexity and "n" in active_complexity:
            canonical_active = "O(n log n)"
        elif "log" in active_complexity:
            canonical_active = "O(log n)"
        elif "n" in active_complexity:
            canonical_active = "O(n)"

        return TheoreticalGraphData(
            active_complexity=canonical_active,
            growth_points=points,
        )
