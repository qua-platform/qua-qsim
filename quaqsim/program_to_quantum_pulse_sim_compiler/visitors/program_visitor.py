from .array_definition_visitor import ArrayDefinitionVisitor
from .definition_visitor import DefinitionVisitor
from .node_visitor import NodeVisitor
from ..context import Context
from ...program_ast.expressions import Definition
from ...program_ast.expressions.definition import ArrayDefinition
from ...program_ast.program import Program


class ProgramVisitor:
    def visit(self, program: Program, context: Context):
        for definition in program.vars:
            if isinstance(definition, ArrayDefinition):
                var = ArrayDefinitionVisitor().visit(definition)
            elif isinstance(definition, Definition):
                var = DefinitionVisitor().visit(definition)
            else:
                raise NotImplementedError()
            context.vars.update(var)

        node_visitor = NodeVisitor()
        for node in program.body:
            node.accept(node_visitor, context)

        return None
