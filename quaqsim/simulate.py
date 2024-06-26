from typing import List

from qiskit_dynamics import DynamicsBackend
from qm import Program

from quaqsim import Compiler
from quaqsim.architectures.transmon_pair_backend_from_qua import ConfigToTransmonPairBackendMap
from quaqsim.program_ast.program import Program as ProgramAST


def simulate_program(qua_program: Program | ProgramAST,
                     qua_config: dict,
                     qua_config_to_backend_map: ConfigToTransmonPairBackendMap,
                     backend: DynamicsBackend,
                     num_shots: int,
                     schedules_to_plot: List[int] = None):

    compiler = Compiler(config=qua_config)
    sim = compiler.compile(qua_program, qua_config_to_backend_map, backend)

    if schedules_to_plot is not None:
        for i in schedules_to_plot:
            sim.plot_schedule(i)
    results = sim.run(num_shots=num_shots)

    return results
