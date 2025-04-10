from quaqsim.program_ast.expressions.definition import ArrayDefinition

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


class ArrayDefinitionVisitor:
    def visit(self, definition: ArrayDefinition) -> dict:
        value = definition.value
        if value == []:
            if definition.type not in default_values:
                raise KeyError(f"Unrecognised variable type in definition {definition.type}")
            value = [default_values[definition.type] for _ in range(definition.size)]
        else:
            value = [cast_funcs[definition.type](value[i].value) for i in range(len(value))]

        return {definition.name: value}
