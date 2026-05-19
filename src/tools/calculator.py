import ast
import math
import operator

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

_SAFE_FUNCTIONS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pi": math.pi,
    "e": math.e,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _SAFE_FUNCTIONS:
        return _SAFE_FUNCTIONS[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
        return _SAFE_OPERATORS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPERATORS:
        return _SAFE_OPERATORS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.Call):
        func = _eval_node(node.func)
        if not callable(func):
            raise ValueError(f"Not a callable: {ast.dump(node.func)}")
        args = [_eval_node(a) for a in node.args]
        return func(*args)
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def calculate(expression: str) -> dict:
    """
    Safely evaluate a mathematical expression string.

    Returns a dict with 'result' on success or 'error' on failure.
    Only numeric literals and whitelisted math functions are allowed —
    arbitrary Python code cannot be executed.
    """
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _eval_node(tree.body)
        return {"result": result, "expression": expression}
    except ZeroDivisionError:
        return {"error": "Division by zero", "expression": expression}
    except (ValueError, TypeError) as exc:
        return {"error": str(exc), "expression": expression}
    except SyntaxError:
        return {"error": "Invalid expression syntax", "expression": expression}
