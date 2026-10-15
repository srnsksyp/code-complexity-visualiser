import pytest
from app.analyzers.ast_parser import SafeASTParser
from app.analyzers.complexity_analyzer import ComplexityAnalyzer


@pytest.fixture
def analyzer():
    return ComplexityAnalyzer()


@pytest.fixture
def parser():
    return SafeASTParser()


def test_constant_time(analyzer, parser):
    code = """
def add(a, b):
    result = a + b
    return result
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(1)"
    assert res.space_complexity == "O(1)"
    assert res.confidence == "HIGH"


def test_single_loop_linear(analyzer, parser):
    code = """
def sum_array(arr):
    total = 0
    for x in arr:
        total += x
    return total
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n)"
    assert res.space_complexity == "O(1)"
    assert res.confidence == "HIGH"


def test_nested_loops_quadratic(analyzer, parser):
    code = """
def find_pairs(arr):
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            print(arr[i], arr[j])
    return True
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n²)"
    assert res.confidence == "HIGH"


def test_triple_nested_loops_cubic(analyzer, parser):
    code = """
def matrix_mult(n):
    for i in range(n):
        for j in range(n):
            for k in range(n):
                c = i + j + k
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n³)"


def test_sequential_independent_loops(analyzer, parser):
    code = """
def process_data(n):
    for i in range(n):
        print(i)
    for j in range(n):
        print(j)
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    # Sequential loops sum to max: O(n) + O(n) = O(n), NOT O(n²)
    assert res.time_complexity == "O(n)"


def test_halving_while_loop_logarithmic(analyzer, parser):
    code = """
def halve(n):
    count = 0
    while n > 1:
        n = n // 2
        count += 1
    return count
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(log n)"


def test_binary_search(analyzer, parser):
    code = """
def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(log n)"
    assert res.space_complexity == "O(1)"


def test_linear_recursion(analyzer, parser):
    code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.time_complexity == "O(n)"
    assert res.space_complexity == "O(n)"
    assert res.statistics.recursion_detected is True


def test_exponential_recursion(analyzer, parser):
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
    assert res.space_complexity == "O(n)"


def test_linear_space_allocation(analyzer, parser):
    code = """
def create_buffer(n):
    arr = [0] * n
    return arr
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.space_complexity == "O(n)"


def test_matrix_space_allocation(analyzer, parser):
    code = """
def create_grid(n):
    matrix = [[0] * n for _ in range(n)]
    return matrix
"""
    tree, err = parser.parse_code(code)
    assert err is None
    res = analyzer.analyze(tree)
    assert res.space_complexity == "O(n²)"


def test_syntax_error_handling(parser):
    invalid_code = "def broken_func(:\n    return 42"
    tree, err = parser.parse_code(invalid_code)
    assert tree is None
    assert err is not None
    assert err.line == 1
    assert "syntax" in err.message.lower() or "expected" in err.message.lower()
