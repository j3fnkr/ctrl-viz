"""
Transfer function string parsing for ctrl-viz.
"""

import control


def parse_transfer_function(expr: str) -> control.TransferFunction:
    """
    Parse a rational expression in s into a transfer function.

    Supported syntax examples:
        1/(s^2+0.5*s+1)
        (s+1)/(s^2+2*s+1)

    Parameters
    ----------
    expr : str
        Transfer function expression using variable ``s``.

    Returns
    -------
    control.TransferFunction
        Parsed transfer function.

    Raises
    ------
    ValueError
        If the expression is empty or cannot be parsed.
    """
    if not expr or not expr.strip():
        raise ValueError("Transfer function expression cannot be empty")

    normalized = expr.strip().replace("^", "**")
    s = control.tf("s")

    try:
        system = eval(normalized, {"__builtins__": {}}, {"s": s})
    except Exception as exc:
        raise ValueError(f"Could not parse transfer function: {exc}") from exc

    if not isinstance(system, control.TransferFunction):
        raise ValueError("Expression must evaluate to a transfer function in s")

    return system
