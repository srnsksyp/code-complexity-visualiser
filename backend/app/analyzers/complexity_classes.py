import math
from typing import Dict, Any, Optional, Tuple


class ComplexityClass:
    """Mathematical representation of asymptotic growth classes.

    Supports polynomial, logarithmic, exponential, factorial, and multi-variable forms.
    Provides canonical normalization and asymptotic dominance comparisons.
    """

    def __init__(
        self,
        category: str,  # "constant", "logarithmic", "linear", "linearithmic", "polynomial", "exponential", "factorial", "unsupported", "custom"
        poly_degree: float = 0.0,
        log_degree: float = 0.0,
        exp_base: float = 1.0,
        variables: Optional[Tuple[str, ...]] = None,
        is_tight: bool = True,
        custom_str: Optional[str] = None,
    ):
        self.category = category
        self.poly_degree = poly_degree
        self.log_degree = log_degree
        self.exp_base = exp_base
        self.variables = variables or ("n",)
        self.is_tight = is_tight
        self.custom_str = custom_str

    @classmethod
    def constant(cls) -> "ComplexityClass":
        return cls("constant", poly_degree=0.0, log_degree=0.0)

    @classmethod
    def logarithmic(cls, log_degree: float = 1.0) -> "ComplexityClass":
        return cls("logarithmic", poly_degree=0.0, log_degree=log_degree)

    @classmethod
    def linear(cls, var: str = "n") -> "ComplexityClass":
        return cls("linear", poly_degree=1.0, log_degree=0.0, variables=(var,))

    @classmethod
    def linearithmic(cls, var: str = "n") -> "ComplexityClass":
        return cls("linearithmic", poly_degree=1.0, log_degree=1.0, variables=(var,))

    @classmethod
    def polynomial(cls, degree: float, var: str = "n") -> "ComplexityClass":
        if degree == 0:
            return cls.constant()
        if degree == 1:
            return cls.linear(var)
        return cls("polynomial", poly_degree=degree, log_degree=0.0, variables=(var,))

    @classmethod
    def exponential(cls, base: float = 2.0, poly_factor: float = 0.0) -> "ComplexityClass":
        # Normalizes bases: e.g. base=2, poly_factor=0 -> O(2^n)
        return cls("exponential", poly_degree=poly_factor, exp_base=base)

    @classmethod
    def factorial(cls, var: str = "n") -> "ComplexityClass":
        return cls("factorial", variables=(var,))

    @classmethod
    def multi_variable(cls, desc: str) -> "ComplexityClass":
        return cls("custom", custom_str=desc)

    @classmethod
    def unsupported(cls, reason: str = "Unsupported recurrence") -> "ComplexityClass":
        return cls("unsupported", custom_str=f"Unsupported ({reason})", is_tight=False)

    @property
    def big_o(self) -> str:
        """Returns standard Big-O notation, e.g. O(2^n)."""
        expr = self._raw_expression()
        if expr.startswith("Unsupported"):
            return "Unsupported / Cannot Determine"
        return f"O({expr})"

    @property
    def tight_bound(self) -> str:
        """Returns tight bound notation Θ(...) or O(...) if loose."""
        expr = self._raw_expression()
        if expr.startswith("Unsupported"):
            return "Unsupported / Cannot Determine"
        prefix = "Θ" if self.is_tight else "O"
        return f"{prefix}({expr})"

    def _raw_expression(self) -> str:
        if self.custom_str:
            return self.custom_str

        var = self.variables[0] if self.variables else "n"

        if self.category == "constant":
            return "1"

        if self.category == "logarithmic":
            if self.log_degree == 1.0:
                return f"log {var}"
            return f"log^{int(self.log_degree) if self.log_degree.is_integer() else self.log_degree} {var}"

        if self.category == "linear":
            return var

        if self.category == "linearithmic":
            return f"{var} log {var}"

        if self.category == "polynomial":
            deg = int(self.poly_degree) if self.poly_degree.is_integer() else self.poly_degree
            if deg == 2:
                return f"{var}²"
            if deg == 3:
                return f"{var}³"
            return f"{var}^{deg}"

        if self.category == "exponential":
            b = int(self.exp_base) if self.exp_base.is_integer() else round(self.exp_base, 2)
            base_str = f"{b}^{var}"
            if self.poly_degree > 0:
                p_deg = int(self.poly_degree) if self.poly_degree.is_integer() else self.poly_degree
                p_str = var if p_deg == 1 else f"{var}^{p_deg}"
                return f"{p_str} * {base_str}"
            return base_str

        if self.category == "factorial":
            return f"{var}!"

        return "n"

    def rank_score(self) -> float:
        """Numerical ranking to evaluate dominance in sums max(f(n), g(n))."""
        if self.category == "constant":
            return 0.0
        if self.category == "logarithmic":
            return 1.0 * self.log_degree
        if self.category == "linear":
            return 10.0
        if self.category == "linearithmic":
            return 15.0
        if self.category == "polynomial":
            return 10.0 * self.poly_degree
        if self.category == "custom":
            return 25.0
        if self.category == "exponential":
            # 2^n -> 100, 3^n -> 150, etc.
            return 100.0 * math.log2(max(1.5, self.exp_base)) + 5.0 * self.poly_degree
        if self.category == "factorial":
            return 1000.0
        return 10.0

    def __lt__(self, other: "ComplexityClass") -> bool:
        return self.rank_score() < other.rank_score()

    def __le__(self, other: "ComplexityClass") -> bool:
        return self.rank_score() <= other.rank_score()

    def __gt__(self, other: "ComplexityClass") -> bool:
        return self.rank_score() > other.rank_score()

    def __ge__(self, other: "ComplexityClass") -> bool:
        return self.rank_score() >= other.rank_score()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ComplexityClass):
            return False
        return self.big_o == other.big_o

    @classmethod
    def dominant_of(cls, *classes: "ComplexityClass") -> "ComplexityClass":
        valid = [c for c in classes if c.category != "unsupported"]
        if not valid:
            return classes[0] if classes else cls.unsupported()
        return max(valid, key=lambda c: c.rank_score())

    @classmethod
    def multiply(cls, c1: "ComplexityClass", c2: "ComplexityClass") -> "ComplexityClass":
        """Symbolically multiplies two complexities: e.g. O(n) * O(n) = O(n²), O(n) * O(2^n) = O(n * 2^n)."""
        if c1.category == "constant":
            return c2
        if c2.category == "constant":
            return c1

        # Exponential * Polynomial -> Exponential with poly factor
        if c1.category == "exponential" and c2.category in ("linear", "polynomial"):
            new_poly = c1.poly_degree + c2.poly_degree
            return cls.exponential(base=c1.exp_base, poly_factor=new_poly)
        if c2.category == "exponential" and c1.category in ("linear", "polynomial"):
            new_poly = c2.poly_degree + c1.poly_degree
            return cls.exponential(base=c2.exp_base, poly_factor=new_poly)

        # Polynomial * Polynomial
        if c1.category in ("linear", "polynomial") and c2.category in ("linear", "polynomial"):
            deg = c1.poly_degree + c2.poly_degree
            return cls.polynomial(deg)

        # Linear * Logarithmic -> Linearithmic
        if (c1.category == "linear" and c2.category == "logarithmic") or (c2.category == "linear" and c1.category == "logarithmic"):
            return cls.linearithmic()

        # Multi-variable: O(n) * O(m) -> O(n*m)
        if c1.variables != c2.variables and c1.variables and c2.variables:
            return cls.multi_variable(f"{c1.variables[0]}*{c2.variables[0]}")

        # Fallback to dominant or custom
        return cls.dominant_of(c1, c2)
