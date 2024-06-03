import copy

from quaqsim.program_ast.expressions.definition import Definition


default_values = {
    'INT': 0,
    'REAL': 0.,
    'BOOL': False,
}

cast_funcs = {
    'INT': int,
    'REAL': float,
    'BOOL': bool
}


class DefinitionVisitor:
    def visit(self, definition: Definition) -> dict:
        value = definition.value
        if value == []:
            if definition.type not in default_values:
                raise KeyError(f"Unrecognised variable type in definition {definition.type}")
            value = default_values[definition.type]
        elif len(value) == 1:
            value = cast_funcs[definition.type](value[0].value)
        else:
            value = [cast_funcs[definition.type](value[i].value) for i in range(len(value))]

        return {definition.name: value}
