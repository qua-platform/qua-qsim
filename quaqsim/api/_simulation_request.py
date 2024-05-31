from dataclasses import dataclass

from ..program_ast.program import Program


@dataclass
class SimulationResult:
    """Result of a simulation. The `pulse_schedule_graph` and `simulated_results_graph`
    are base64-encoded PNGs."""
    pulse_schedule_graph: str | None
    simulated_results: list[list[float]] | None
    simulated_results_graph: str | None
    error: Exception | None


@dataclass
class SimulationRequest:
    qua_configuration: dict | None = None
    qua_program: Program | None = None
    quantum_system: bytes | None = None
    channel_map: bytes | None = None
    result: SimulationResult | None = None

    @property
    def can_simulate(self) -> bool:
        """Whether this request can be simulated."""
        return (
            self.qua_configuration is not None
            and self.qua_program is not None
            and self.quantum_system is not None
            and self.channel_map is not None
        )
