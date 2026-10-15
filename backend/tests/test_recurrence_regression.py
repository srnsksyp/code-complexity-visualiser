import pytest
from app.analyzers.ast_parser import SafeASTParser
from app.analyzers.complexity_analyzer import ComplexityAnalyzer


@pytest.fixture
def analyzer():
    return ComplexityAnalyzer()


@pytest.fixture
def parser():
    return SafeASTParser()


# ========================================================
# KNOWN REGRESSION FAILURE CASES
# ========================================================

def test_power_set_regression(analyzer, parser):
    """Case 1: Power Set must be recognized as exponential, with n*2^n materialization/output."""
    code = """
def generate_power_set(arr, index=0, current=None, result=None):
    if result is None:
        result = []
    if current is None:
        current = []

    if index == len(arr):
        result.append(list(current))
        return result

    current.append(arr[index])
    generate_power_set(arr, index + 1, current, result)

    current.pop()
    generate_power_set(arr, index + 1, current, result)

    return result
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    # Both 2^n and n * 2^n reflect the exponential recurrence
    assert "2^n" in res.time_complexity
    assert res.recurrence.present is True
    assert res.recurrence.branching_factor == 2
    assert res.confidence == "HIGH"
    # Space breakdown separates auxiliary stack from stored output
    assert res.space_breakdown.recursion_stack in ("O(n)", "O(arr)")
    assert "2^n" in res.space_breakdown.output


def test_knapsack_regression(analyzer, parser):
    """Case 2: Naive Knapsack worst-case recursive computation is exponential in item dimension."""
    code = """
def knapsack(capacity, weights, values, n):
    if n == 0 or capacity == 0:
        return 0

    if weights[n - 1] <= capacity:
        include_item = values[n - 1] + knapsack(
            capacity - weights[n - 1],
            weights,
            values,
            n - 1
        )

        exclude_item = knapsack(
            capacity,
            weights,
            values,
            n - 1
        )

        return max(include_item, exclude_item)

    else:
        return knapsack(
            capacity,
            weights,
            values,
            n - 1
        )
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(2^n)"
    assert res.recurrence.present is True
    assert res.recurrence.branching_factor == 2
    assert res.confidence == "HIGH"


def test_3way_combinations_regression(analyzer, parser):
    """Case 3: 3-Way combinations generator branches into 3 subproblems per invocation -> O(3^n)."""
    code = """
def generate_combinations(n, current_string=""):
    if len(current_string) == n:
        print(current_string)
        return

    generate_combinations(n, current_string + "A")
    generate_combinations(n, current_string + "B")
    generate_combinations(n, current_string + "C")
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(3^n)"
    assert res.recurrence.present is True
    assert res.recurrence.branching_factor == 3
    assert res.confidence == "HIGH"


# ========================================================
# RECURSIVE PATTERNS & MASTER THEOREM
# ========================================================

def test_single_recursion_step_3(analyzer, parser):
    """T(n) = T(n-3) + O(1) -> O(n)"""
    code = """
def countdown_by_3(n):
    if n <= 0:
        return 0
    return 1 + countdown_by_3(n - 3)
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n)"
    assert res.recurrence.branching_factor == 1


def test_half_size_logarithmic(analyzer, parser):
    """T(n) = T(n/2) + O(1) -> O(log n)"""
    code = """
def recursive_halve(n):
    if n <= 1:
        return 1
    return 1 + recursive_halve(n // 2)
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(log n)"
    assert res.space_breakdown.recursion_stack == "O(log n)"


def test_binary_divide_conquer_linear(analyzer, parser):
    """T(n) = 2T(n/2) + O(1) -> O(n)"""
    code = """
def divide_and_conquer_count(arr):
    if len(arr) <= 1:
        return 1
    mid = len(arr) // 2
    return divide_and_conquer_count(arr[:mid]) + divide_and_conquer_count(arr[mid:])
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n)"


def test_merge_sort_recurrence(analyzer, parser):
    """T(n) = 2T(n/2) + O(n) -> O(n log n)"""
    code = """
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # Linear merge work
    merged = []
    i = 0
    while i < len(left):
        merged.append(left[i])
        i += 1
    return merged
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n log n)"


def test_divide_conquer_4_parts_quadratic(analyzer, parser):
    """T(n) = 4T(n/2) + O(1) -> O(n^2)"""
    code = """
def quad_tree(n):
    if n <= 1:
        return 1
    return quad_tree(n // 2) + quad_tree(n // 2) + quad_tree(n // 2) + quad_tree(n // 2)
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n²)"


def test_multi_term_fibonacci(analyzer, parser):
    """T(n) = T(n-1) + T(n-2) + O(1) -> O(2^n)"""
    code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(2^n)"


def test_recursion_inside_loop_factorial(analyzer, parser):
    """for i in range(n): f(n-1) -> O(n!)"""
    code = """
def generate_permutations(n):
    if n <= 1:
        return 1
    total = 0
    for i in range(n):
        total += generate_permutations(n - 1)
    return total
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n!)"


# ========================================================
# LOOP & DEPENDENT BOUND PATTERNS
# ========================================================

def test_dependent_triangular_loop(analyzer, parser):
    """for i in range(n): for j in range(i): -> O(n^2)"""
    code = """
def triangular(n):
    count = 0
    for i in range(n):
        for j in range(i):
            count += 1
    return count
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n²)"


def test_dependent_quadratic_loop(analyzer, parser):
    """for i in range(n): for j in range(i * i): -> O(n^3)"""
    code = """
def quadratic_inner(n):
    count = 0
    for i in range(n):
        for j in range(i * i):
            count += 1
    return count
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n³)"


def test_quartic_loop_nesting(analyzer, parser):
    """4 nested loops -> O(n^4)"""
    code = """
def four_loops(n):
    count = 0
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(n):
                    count += 1
    return count
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n^4)"


def test_multi_variable_sum_range(analyzer, parser):
    """range(n + m) -> O(n+m)"""
    code = """
def sum_bounds(n, m):
    count = 0
    for i in range(n + m):
        count += 1
    return count
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert "n+m" in res.time_complexity


# ========================================================
# MEMOIZATION & DYNAMIC PROGRAMMING
# ========================================================

def test_memoized_fibonacci(analyzer, parser):
    """Fibonacci with explicit memo dictionary -> O(n)"""
    code = """
memo = {}
def fib_memo(n):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib_memo(n - 1) + fib_memo(n - 2)
    return memo[n]
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n)"
    assert res.recurrence.is_solved is True


# ========================================================
# PROPERTY & METAMORPHIC TESTS
# ========================================================

def test_metamorphic_variable_renaming(analyzer, parser):
    """Renaming variables must not change derived complexity."""
    code1 = """
def f(n):
    for i in range(n):
        for j in range(n):
            x = i + j
"""
    code2 = """
def f(total_size):
    for outer_idx in range(total_size):
        for inner_idx in range(total_size):
            accumulator = outer_idx + inner_idx
"""
    res1 = analyzer.analyze(parser.parse_code(code1)[0])
    res2 = analyzer.analyze(parser.parse_code(code2)[0])
    assert res1.time_complexity == res2.time_complexity == "O(n²)"


def test_metamorphic_whitespace_and_comments(analyzer, parser):
    """Adding comments and whitespace must not change derived complexity."""
    code1 = """def f(n):\n    return n * 2"""
    code2 = """
# This is a comment
def f(n):

    # Another comment inside
    return n * 2

"""
    res1 = analyzer.analyze(parser.parse_code(code1)[0])
    res2 = analyzer.analyze(parser.parse_code(code2)[0])
    assert res1.time_complexity == res2.time_complexity == "O(1)"


def test_metamorphic_second_recursive_call_exponential(analyzer, parser):
    """Adding a second recursive call must transform O(n) linear recursion into O(2^n)."""
    single_call = """
def f(n):
    if n <= 1:
        return 1
    return f(n - 1)
"""
    two_calls = """
def f(n):
    if n <= 1:
        return 1
    return f(n - 1) + f(n - 1)
"""
    res1 = analyzer.analyze(parser.parse_code(single_call)[0])
    res2 = analyzer.analyze(parser.parse_code(two_calls)[0])
    assert res1.time_complexity == "O(n)"
    assert res2.time_complexity == "O(2^n)"


def test_metamorphic_n_minus_1_to_n_div_2(analyzer, parser):
    """Changing parameter transformation from n-1 to n//2 transforms O(n) into O(log n)."""
    linear_call = """
def f(n):
    if n <= 1:
        return 1
    return 1 + f(n - 1)
"""
    halving_call = """
def f(n):
    if n <= 1:
        return 1
    return 1 + f(n // 2)
"""
    res1 = analyzer.analyze(parser.parse_code(linear_call)[0])
    res2 = analyzer.analyze(parser.parse_code(halving_call)[0])
    assert res1.time_complexity == "O(n)"
    assert res2.time_complexity == "O(log n)"
