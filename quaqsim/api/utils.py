import base64
import dill

from io import BytesIO
from typing import Any

from qm import Program
from qm.qua import *  # Useful to `script_to_program`.

from ..program_ast.program import Program as ProgramAST
from ..program_dict_to_program_compiler.program_tree_builder import ProgramTreeBuilder


def load_from_base64(s: str) -> Any:
    """Deserialize an object serialized as a base 64 string."""
    return dill.loads(base64.b64decode(s))


def dump_to_base64(obj: Any) -> str:
    """Serialize an object into a base 64 string."""
    return base64.b64encode(dill.dumps(obj)).decode(encoding="utf-8")


def dump_fig_to_base64(fig) -> str:
    """Serialize a matplotlib figure into a base 64 string."""
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode(encoding="utf-8")


def script_to_program(script: str) -> Program:
    """Convert a QUA script into a QM Program.

    This is a security concern if `script` is not trusted.
    """
    with program() as prog:
        exec(script)
    return prog


def program_to_ast(prog: Program) -> ProgramAST:
    """Transform a QM Program into an AST, which is safer to serialize."""
    return ProgramTreeBuilder().build(prog)
