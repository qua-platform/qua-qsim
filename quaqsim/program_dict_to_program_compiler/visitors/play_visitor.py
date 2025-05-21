from typing import List

from .expression_visitors.expression_visitor import ExpressionVisitor
from .visitor import Visitor
from .ramp_visitor import RampVisitor
from ...program_ast.play import Play
from ...program_ast.node import Node


class PlayVisitor(Visitor):
    def visit(self, d: dict) -> List[Node]:
        element = d["qe"]["name"]

        operation = None
        if "namedPulse" in d:
            operation = d["namedPulse"]["name"]
        elif "rampPulse" in d:
            operation = RampVisitor().visit(d["rampPulse"])

        amp = None
        if "amp" in d:
            amp = ExpressionVisitor().visit(d["amp"]["v0"])

        duration = None
        if "duration" in d:
            duration = ExpressionVisitor().visit(d["duration"])

        for k in d:
            if k not in ["loc", "qe", "namedPulse", "amp", "duration", "rampPulse"]:
                raise NotImplementedError(f"Unhandled play parameter {k}")

        return [Play(operation, element, amp, duration)]
