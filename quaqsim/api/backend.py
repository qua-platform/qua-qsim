from typing import Annotated, Optional

from fastapi import Body, FastAPI, HTTPException
from fastapi import status as http_status
from fastapi.middleware.wsgi import WSGIMiddleware
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from qiskit.pulse import Schedule
from qiskit.visualization.pulse_v2 import draw, IQXDebugging
from qm.qua import *

from ..architectures.transmon_pair_backend_from_qua import TransmonPairBackendFromQUA
from ..program_to_quantum_pulse_sim_compiler.quantum_pulse_sim_compiler import Compiler
from ._simulation_request import SimulationRequest, SimulationResult
from .frontend import dashboard, editor
from .utils import (
    load_from_base64,
    dump_fig_to_base64,
    program_to_ast,
    script_to_program,
)

matplotlib.use("agg")

start, stop, step = -2, 2, 0.1
xs = np.arange(start, stop, step)


def _get_pulse_schedule_graphs(schedules: list[Schedule]) -> tuple[str, list[str]]:
    """Return a tuple `(pulse_schedule_graph, pulse_schedule_graphs)`. All graphs are
    base64-encoded PNGs.

    `pulse_schedule_graph` is a big graph with all pulse schedules.

    `pulse_schedule_graphs` is a list of each individual single pulse schedule.
    """

    def _draw(ax):
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
            axis=ax,
        )

    n = len(schedules)
    all_graphs_fig, all_graphs_axes = plt.subplots(
        ncols=5,
        nrows=n // 5 if n % 5 == 0 else n // 5 + 1,
        figsize=(25, 4 * (n // 5)),
        dpi=75,
    )
    for i, schedule in enumerate(schedules):
        _draw(ax=all_graphs_axes[i // 5][i % 5])
    all_graphs_fig.tight_layout()

    graphs = []
    for schedule in schedules:
        individual_fig, individual_ax = plt.subplots(ncols=1, nrows=1)
        _draw(ax=individual_ax)
        individual_fig.tight_layout()
        graphs.append(dump_fig_to_base64(individual_fig))
        plt.close(individual_fig)

    return dump_fig_to_base64(all_graphs_fig), graphs


def _get_simulated_results_graph_figure(results) -> tuple[str, Figure]:
    fig, ax = plt.subplots()
    for i, result in enumerate(results):
        ax.plot(xs, result, ".-", label=f"Simulated Q{i}")
        ax.set_ylim(-0.05, 1.05)
    fig.legend()

    return dump_fig_to_base64(fig), fig


def _add_vertical_line_to_simulated_results_figure(tick: int, fig: Figure) -> str:
    ax = fig.gca()
    line = ax.axvline(x=xs[tick], color="r", linestyle="--")

    graph = dump_fig_to_base64(fig)

    line.remove()  # Delete the line, otherwise it stays on the figure.

    return graph


def create_app():
    app = FastAPI()

    app.mount("/dashboard", WSGIMiddleware(dashboard.server))
    app.mount("/editor", WSGIMiddleware(editor.server))

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
                pulse_schedule_graphs=None,
                simulated_results=None,
                simulated_results_graph=None,
                simulated_results_figure=None,
                error=e,
            )
        else:
            pulse_schedule_graph, pulse_schedule_graphs = _get_pulse_schedule_graphs(
                simulation.schedules
            )
            simulated_results_graph, simulated_results_figure = (
                _get_simulated_results_graph_figure(results)
            )
            request.result = SimulationResult(
                pulse_schedule_graph=pulse_schedule_graph,
                pulse_schedule_graphs=pulse_schedule_graphs,
                simulated_results=results,
                simulated_results_graph=simulated_results_graph,
                simulated_results_figure=simulated_results_figure,
                error=None,
            )

    @app.get("/api/status")
    async def status(tick: Optional[int] = None) -> dict:
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

        if tick is None:
            return {
                "num_pulse_schedules": len(result.pulse_schedule_graphs),
                "pulse_schedule_graph": result.pulse_schedule_graph,
                "simulated_results": result.simulated_results,
                "simulated_results_graph": result.simulated_results_graph,
                "error": result.error,
            }

        # Ensure `tick` is within bounds.
        tick = max(0, min(int(tick), len(result.pulse_schedule_graphs) - 1))

        return {
            "num_pulse_schedules": len(result.pulse_schedule_graphs),
            "pulse_schedule_graph": result.pulse_schedule_graphs[tick],
            "simulated_results": result.simulated_results,
            "simulated_results_graph": _add_vertical_line_to_simulated_results_figure(
                tick, result.simulated_results_figure
            ),
            "error": result.error,
        }

    @app.post("/api/reset")
    async def reset():
        """Erase any request and simulation."""
        app.state.simulation_request = SimulationRequest()

    return app


app = create_app()
