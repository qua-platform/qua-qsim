import dash_bootstrap_components as dbc
import dash_editor_components
from dash import Dash, dcc, html, Input, Output, State, no_update
import requests

from ..utils import dump_to_base64
from ._utils import header


editor = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    requests_pathname_prefix="/editor/",
)

editor_container = html.Div(
    [
        dbc.Button(
            "Simulate",
            color="primary",
            id="editor-simulate",
            class_name="my-3",
        ),
        dash_editor_components.PythonEditor(
            id="editor",
            style={"border": "1px solid black"},
        ),
    ]
)

simulation_container = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dcc.Slider(
                    id="simulation-slider",
                    min=0,
                    max=10,
                    step=1,
                    value=0,
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True},
                )
            ),
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.H3("Pulse schedule", className="mt-3"),
                    html.Img(id="pulse-schedule"),
                ]
            ),
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.H3("Simulated results", className="mt-3"),
                    html.Img(id="simulated-results"),
                ]
            ),
        ),
    ],
    id="simulation-container",
    style={"display": "none"},
)

editor.layout = dbc.Container(
    [
        header,
        html.Hr(),
        dbc.Row(
            dbc.Col(
                html.Div(
                    "Message",
                    id="editor-message",
                    style={"display": "none"},
                ),
            ),
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Editor"),
                        editor_container,
                    ]
                ),
                dbc.Col(
                    [
                        html.H2("Simulations"),
                        simulation_container,
                    ]
                ),
            ]
        ),
    ],
    fluid=True,
)


@editor.callback(
    [
        Output("editor-message", "children"),
        Output("editor-message", "style"),
        Output("simulation-container", "style"),
        Output("simulation-slider", "max"),
        Output("simulation-slider", "value"),
    ],
    Input("editor-simulate", "n_clicks"),
    State("editor", "value"),
    prevent_initial_call=True,
)
def simulate(_simulate, editor_value):
    if editor_value is None or editor_value.isspace():
        return (
            "Error: no script provided.",
            {"display": "block"},
            {"display": "none"},
            no_update,
            no_update,
        )

    requests.post(
        "http://localhost:8000/api/submit_qua_program",
        json={"qua_script": dump_to_base64(editor_value)},
    )
    requests.get("http://localhost:8000/api/simulate")
    status_response = requests.get("http://localhost:8000/api/status")

    if status_response.status_code != 200:
        error_message = status_response.json()["detail"]
        return (
            f"Error: “{error_message}”.",
            {"display": "block"},
            {"display": "none"},
            no_update,
            no_update,
        )

    data = status_response.json()
    num_pulse_schedules = data["num_pulse_schedules"]

    return (
        "",
        {"display": "none"},
        {"display": "block"},
        num_pulse_schedules,
        0,
    )


@editor.callback(
    [
        Output("editor-message", "children", allow_duplicate=True),
        Output("editor-message", "style", allow_duplicate=True),
        Output("pulse-schedule", "src"),
        Output("simulated-results", "src"),
    ],
    Input("simulation-slider", "value"),
    prevent_initial_call=True,
)
def update_graphs(slider_value):
    response = requests.get(f"http://localhost:8000/api/status?tick={slider_value}")

    if response.status_code == 200:
        data = response.json()
        pulse_schedule_graph = data["pulse_schedule_graph"]
        simulated_results_graph = data["simulated_results_graph"]
        return (
            "",
            {"display": "none"},
            f"data:image/png;base64,{pulse_schedule_graph}",
            f"data:image/png;base64,{simulated_results_graph}",
        )

    error_message = response.json()["detail"]
    return (
        f"Error: “{error_message}”.",
        {"display": "block"},
        "",
        "",
    )
