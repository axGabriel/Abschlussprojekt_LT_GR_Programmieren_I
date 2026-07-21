"""
This is a module containing utility functions for the OOP exercise.
It is mainly intended to repeat import and using modules in Python.
"""


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between a minimum and maximum value."""
    return max(min_value, min(value, max_value))


def is_equal_in_tolerance(a: float, b: float, tol: float = 1e-9) -> bool:
    """Check if two floating-point numbers are equal within a given tolerance."""
    return abs(a - b) <= tol


def is_less_equal_in_tol(a: float, b: float, tol: float = 1e-9) -> bool:
    """Check if a is less than or equal to b within a given tolerance."""
    return a <= b + tol


def is_greater_equal_in_tol(a: float, b: float, tol: float = 1e-9) -> bool:
    """Check if a is greater than or equal to b within a given tolerance."""
    return a >= b - tol

def moving_average(data_list: list[float], window_size: int = 5) -> list[float]:
    """calculating moving average"""
    data_smoothed = []
    for i in range(len(data_list)):
        lower_bound = max(0, i - window_size + 1)
        window = data_list[lower_bound : i + 1]
        avg = sum(window) / len(window)
        data_smoothed.append(avg)
    return data_smoothed