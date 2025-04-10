import random
from typing import Literal

from quaqsim.program_ast.expressions import Operation, Function
from .expression_visitor import ExpressionVisitor
from ...context import Context


class FunctionVisitor:
    def visit(self, function: Function, context: Context):
        expression_visitor = ExpressionVisitor()
        if function.function_name == 'mul_fixed_by_int':
            left = expression_visitor.visit(function.arguments[0], context)
            right = expression_visitor.visit(function.arguments[1], context)
            return _mul_fixed_by_int(left, right)
        elif function.function_name == 'rand_int':
            max_int = expression_visitor.visit(function.arguments[1], context)
            if max_int < 1:
                raise ValueError("Random number maximum must be greater than or equal to 1.")
            return random.randint(0, max_int-1)  # non-inclusive
        else:
            raise NotImplementedError(f"Unimplemented function {function.function_name}.")
        pass


def _mul_fixed_by_int(left: float, right: int) -> float:
    return left * right
