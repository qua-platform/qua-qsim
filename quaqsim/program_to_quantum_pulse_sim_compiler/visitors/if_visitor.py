from quaqsim.program_ast._if import If
from quaqsim.program_to_quantum_pulse_sim_compiler.context import Context
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.expression_visitors.expression_visitor import \
    ExpressionVisitor
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.visitor import Visitor


class IfVisitor(Visitor):
    def visit(self, node: If, context: Context):
        condition = ExpressionVisitor().visit(node.cond, context)

        from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.node_visitor import \
            NodeVisitor
        node_visitor = NodeVisitor()
        if condition:
            for inner_node in node.body:
                inner_node.accept(node_visitor, context)
        else:
            for else_if in node.else_ifs:
                self.visit(else_if, context)
