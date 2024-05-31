import numpy as np
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from quaqsim.api.backend import create_app
from quaqsim.api.utils import dump_to_base64, program_to_ast


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_submit_qua_configuration(client: TestClient, transmon_pair_qua_config: dict):
    response = client.post(
        "/api/submit_qua_configuration",
        json={"qua_configuration": dump_to_base64(transmon_pair_qua_config)},
    )
    assert response.json() is None
    assert response.status_code == 200


def test_submit_qua_script(client: TestClient, rabi_prog_script):
    response = client.post(
        "/api/submit_qua_program",
        json={"qua_script": dump_to_base64(rabi_prog_script)},
    )
    assert response.json() is None
    assert response.status_code == 200


def test_submit_qua_program(client: TestClient, rabi_prog):
    response = client.post(
        "/api/submit_qua_program",
        json={"qua_program": dump_to_base64(program_to_ast(rabi_prog))},
    )
    assert response.json() is None
    assert response.status_code == 200


def test_submit_quantum_system(client: TestClient, transmon_pair):
    response = client.post(
        "/api/submit_quantum_system",
        json={"quantum_system": dump_to_base64(transmon_pair)},
    )
    assert response.json() is None
    assert response.status_code == 200


def test_submit_channel_map(client: TestClient, config_to_transmon_pair_backend_map):
    response = client.post(
        "/api/submit_channel_map",
        json={"channel_map": dump_to_base64(config_to_transmon_pair_backend_map)},
    )
    assert response.json() is None
    assert response.status_code == 200


@pytest.fixture
def submit_rabi(
    client: TestClient,
    transmon_pair_qua_config,
    rabi_prog,
    transmon_pair,
    config_to_transmon_pair_backend_map,
):
    client.post(
        "/api/submit_qua_configuration",
        json={"qua_configuration": dump_to_base64(transmon_pair_qua_config)},
    )
    client.post(
        "/api/submit_qua_program",
        json={"qua_program": dump_to_base64(program_to_ast(rabi_prog))},
    )
    client.post(
        "/api/submit_quantum_system",
        json={"quantum_system": dump_to_base64(transmon_pair)},
    )
    client.post(
        "/api/submit_channel_map",
        json={"channel_map": dump_to_base64(config_to_transmon_pair_backend_map)},
    )


def test_status_no_simulate(client: TestClient, submit_rabi):
    response = client.get("/api/status")
    assert response.status_code == 400
    assert response.json() == {"detail": "/simulate was not called"}


def test_status_simulate_missing_data(client: TestClient, transmon_pair_qua_config):
    client.post(
        "/api/submit_qua_configuration",
        json={"qua_configuration": transmon_pair_qua_config},
    )
    client.get("/api/simulate")

    response = client.get("/api/status")
    assert response.status_code == 400
    assert response.json() == {"detail": "Missing data for simulation."}


def test_status(client: TestClient, submit_rabi):
    client.get("/api/simulate")

    response = client.get("/api/status")
    assert response.status_code == 200

    data = response.json()
    assert "pulse_schedule_graph" in data
    assert "simulated_results_graph" in data

    results = data["simulated_results"]
    start, stop, step = -2, 2, 0.1
    q1_state_probabilities = np.array(results[0])
    q2_state_probabilities = np.array(results[0])
    amps = np.arange(start, stop, step)
    expected_state_probabilities = np.sin(np.pi * amps / 4) ** 2
    assert np.allclose(q1_state_probabilities, expected_state_probabilities, atol=0.1)
    assert np.allclose(q2_state_probabilities, expected_state_probabilities, atol=0.1)
