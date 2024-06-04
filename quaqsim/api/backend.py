from dataclasses import asdict
from typing import Annotated, Optional

from fastapi import Body, FastAPI, HTTPException
from fastapi import status as http_status
from fastapi.middleware.wsgi import WSGIMiddleware
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from qiskit.pulse import Schedule
from qiskit.visualization.pulse_v2 import draw, IQXDebugging
from qm.qua import *

from ..architectures.transmon_pair_backend_from_qua import TransmonPairBackendFromQUA
from ..program_to_quantum_pulse_sim_compiler.quantum_pulse_sim_compiler import Compiler
from ._simulation_request import SimulationRequest, SimulationResult
from .frontend import dashboard
from .utils import (
    load_from_base64,
    dump_fig_to_base64,
    program_to_ast,
    script_to_program,
)

matplotlib.use("agg")


def _get_pulse_schedule_graph(schedules: list[Schedule]):
    n = len(schedules)
    fig, ax = plt.subplots(
        ncols=5,
        nrows=n // 5 if n % 5 == 0 else n // 5 + 1,
        figsize=(25, 4 * (n // 5)),
        dpi=75,
    )

    for i, schedule in enumerate(schedules):
        draw(
            program=schedule,
            style=IQXDebugging(),
            backend=None,
            time_range=None,
            time_unit="ns",
            disable_channels=None,
            show_snapshot=True,
            show_framechange=True,
            show_waveform_info=True,
            show_barrier=True,
            plotter="mpl2d",
            axis=ax[i // 5][i % 5],
        )

    fig.tight_layout()

    return dump_fig_to_base64(fig)


def _get_simulated_results_graph(results):
    start, stop, step = -2, 2, 0.1

    fig, ax = plt.subplots()
    for i, result in enumerate(results):
        ax.plot(
            np.arange(start, stop, step),
            result,
            ".-",
            label=f"Simulated Q{i}",
        )
        ax.set_ylim(-0.05, 1.05)
    fig.legend()

    return dump_fig_to_base64(fig)


def create_app():
    app = FastAPI()

    app.mount("/dashboard", WSGIMiddleware(dashboard.server))

    app.state.simulation_request = SimulationRequest()

    @app.post("/api/submit_qua_configuration")
    async def submit_qua_configuration(
        qua_configuration: Annotated[str, Body(embed=True)],
    ):
        """Submit QUA configuration. The dict must be serialized with dill and encoded
        as a base64 string."""
        app.state.simulation_request.qua_configuration = load_from_base64(
            qua_configuration
        )

    @app.post("/api/submit_qua_program")
    async def submit_qua_program(
        qua_script: Annotated[Optional[str], Body(embed=True)] = None,
        qua_program: Annotated[Optional[str], Body(embed=True)] = None,
    ):
        """Submit QUA script or program. The string or program_ast.Program must be
        serialized with dill and encoded as a base64 string.

        Warning:
            If provided, `qua_script` is executed through `exec()`, which is a security
            risk if the input is not trusted.
        """
        if qua_script is not None and qua_program is not None:
            raise ValueError(
                "Only one of `qua_script` and `qua_program` can be provided"
            )

        if qua_script is not None:
            app.state.simulation_request.qua_program = program_to_ast(
                script_to_program(load_from_base64(qua_script))
            )
        elif qua_program is not None:
            app.state.simulation_request.qua_program = load_from_base64(qua_program)
        else:
            raise ValueError("One of `qua_script` and `qua_program` must be provided")

    @app.post("/api/submit_quantum_system")
    async def submit_quantum_system(quantum_system: Annotated[bytes, Body(embed=True)]):
        """Submit quantum system. The object must be serialized with dill and encoded as
        a base64 string."""
        app.state.simulation_request.quantum_system = load_from_base64(quantum_system)

    @app.post("/api/submit_channel_map")
    async def submit_channel_map(channel_map: Annotated[bytes, Body(embed=True)]):
        """Submit quantum system. The dict must be serialized with dill and encoded as a
        base64 string."""
        app.state.simulation_request.channel_map = load_from_base64(channel_map)

    @app.get("/api/simulate")
    async def simulate(num_shots: int = 1000):
        """Simulate the system."""
        # When this method returns, `self.result` is set.
        request: SimulationRequest = app.state.simulation_request

        try:
            if not request.can_simulate:
                raise ValueError("Missing data for simulation.")

            # This is a breakdown of `simulate_program`, which gives an easier access to
            # the schedules in `simulation`.
            compiler = Compiler(config=request.qua_configuration)
            simulation = compiler.compile(
                request.qua_program,
                request.channel_map,
                TransmonPairBackendFromQUA(request.quantum_system, request.channel_map),
            )
            results = simulation.run(num_shots)
        except Exception as e:
            request.result = SimulationResult(
                pulse_schedule_graph=None,
                simulated_results=None,
                simulated_results_graph=None,
                error=e,
            )
        else:
            request.result = SimulationResult(
                pulse_schedule_graph=_get_pulse_schedule_graph(simulation.schedules),
                simulated_results=results,
                simulated_results_graph=_get_simulated_results_graph(results),
                error=None,
            )

    @app.get("/api/status")
    async def status() -> dict:
        """Return a dict with the result of the simulation, or an HTTP error if
        something went wrong."""
        result: SimulationResult = app.state.simulation_request.result

        if result is None:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="/simulate was not called",
            )

        if result.error is not None:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=str(app.state.simulation_request.result.error),
            )

        return asdict(result)

    @app.post("/api/reset")
    async def reset():
        """Erase any request and simulation."""
        app.state.simulation_request = SimulationRequest()

    return app


app = create_app()
