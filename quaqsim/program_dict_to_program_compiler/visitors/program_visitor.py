import qm

from .statements_visitor import StatementsVisitor
from ...program_ast.expressions.definition import Definition, ArrayDefinition
from ...program_ast.program import Program


class ProgramVisitor:
    def visit(self, program: qm.Program) -> Program:
        body_dict = program.body._body.to_dict()
        body = StatementsVisitor().visit(body_dict)
        vars = []
        for var in program.qua_program.script.variables:
            if var.size == 1:
                vars.append(Definition(name=var.name, type=var.type.name, value=var.value))
            else:
                vars.append(ArrayDefinition(name=var.name, type=var.type.name, value=var.value, size=var.size))

        return Program(body=body, vars=vars)
