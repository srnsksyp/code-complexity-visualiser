export interface CodeExample {
  id: string;
  name: string;
  category: string;
  expectedTime: string;
  expectedSpace: string;
  code: string;
  description: string;
}

export const CODE_EXAMPLES: CodeExample[] = [
  {
    id: "nested-pairs",
    name: "Quadratic Pair Search",
    category: "Nested Loops",
    expectedTime: "O(n²)",
    expectedSpace: "O(1)",
    description: "Two nested loops comparing all index pairs (i, j).",
    code: `def find_pairs(arr):
    n = len(arr)

    for i in range(n):
        for j in range(i + 1, n):
            print(arr[i], arr[j])

    return True`,
  },
  {
    id: "binary-search",
    name: "Binary Search",
    category: "Logarithmic While",
    expectedTime: "O(log n)",
    expectedSpace: "O(1)",
    description: "Halves search interval at each iteration via pointer updates.",
    code: `def binary_search(arr, target):
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

    return -1`,
  },
  {
    id: "linear-sum",
    name: "Linear Array Sum",
    category: "Single Loop",
    expectedTime: "O(n)",
    expectedSpace: "O(1)",
    description: "Iterates through each element in an array once.",
    code: `def sum_array(arr):
    total = 0

    for x in arr:
        total += x

    return total`,
  },
  {
    id: "sequential-loops",
    name: "Sequential Independent Loops",
    category: "Additive Loops",
    expectedTime: "O(n)",
    expectedSpace: "O(1)",
    description: "Two consecutive loops: O(n) + O(n) = O(n), NOT O(n²).",
    code: `def process_stages(items):
    # Stage 1: find maximum
    max_val = items[0]
    for item in items:
        if item > max_val:
            max_val = item

    # Stage 2: compute total
    total = 0
    for item in items:
        total += item

    return max_val, total`,
  },
  {
    id: "halving-while",
    name: "Logarithmic Counter",
    category: "Logarithmic While",
    expectedTime: "O(log n)",
    expectedSpace: "O(1)",
    description: "Repeatedly integer-divides variable by 2.",
    code: `def count_divisions(n):
    divisions = 0

    while n > 1:
        n = n // 2
        divisions += 1

    return divisions`,
  },
  {
    id: "recursion-factorial",
    name: "Factorial (Linear Recursion)",
    category: "Recursion",
    expectedTime: "O(n)",
    expectedSpace: "O(n)",
    description: "Single recursive decrement with depth proportional to n.",
    code: `def factorial(n):
    if n <= 1:
        return 1

    return n * factorial(n - 1)`,
  },
  {
    id: "recursion-fibonacci",
    name: "Fibonacci (Exponential Tree)",
    category: "Recursion",
    expectedTime: "O(2^n)",
    expectedSpace: "O(n)",
    description: "Branching recursive calls without memoization.",
    code: `def fibonacci(n):
    if n <= 1:
        return n

    return fibonacci(n - 1) + fibonacci(n - 2)`,
  },
  {
    id: "matrix-allocation",
    name: "2D Matrix Grid Allocation",
    category: "Space Complexity",
    expectedTime: "O(n²)",
    expectedSpace: "O(n²)",
    description: "Allocates an n x n nested list grid.",
    code: `def initialize_grid(n):
    # Creates n x n matrix of zeros
    matrix = [[0] * n for _ in range(n)]
    return matrix`,
  },
  {
    id: "cubic-loop",
    name: "Matrix Multiplication (Cubic)",
    category: "Nested Loops",
    expectedTime: "O(n³)",
    expectedSpace: "O(1)",
    description: "Three deeply nested loops iterating up to n.",
    code: `def compute_tensor(n):
    ops = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                ops += i * j * k
    return ops`,
  },
];
