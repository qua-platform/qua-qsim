import dash_bootstrap_components as dbc
from dash import Dash, html, callback, Input, Output, ctx
import requests


dashboard = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    requests_pathname_prefix="/dashboard/",
)

controls = html.Div(
    [
        dbc.Button("Reload", color="primary", id="reload", class_name="me-3"),
        dbc.Button("Reset", outline=True, color="danger", id="reset"),
    ]
)

dashboard.layout = dbc.Container(
    [
        html.H1("qua-qsim dashboard"),
        html.Hr(),
        dbc.Row(
            dbc.Col(
                controls,
            ),
        ),
        dbc.Row(
            dbc.Col(
                html.Div("Message", id="message"),
            ),
            class_name="mt-3",
            id="message-row",
            style={"display": "none"},
        ),
        html.H2("Pulse schedule", className="mt-3"),
        html.Hr(),
        dbc.Row(
            dbc.Col(
                html.Img(id="pulse-schedule"),
                width=6,
            ),
            class_name="mt-3",
            id="pulse-schedule-row",
            style={"display": "none"},
        ),
        html.H2("Simulated results", className="mt-3"),
        html.Hr(),
        dbc.Row(
            dbc.Col(
                html.Img(id="simulated-results"),
                width=6,
            ),
            class_name="mt-3",
            id="simulated-results-row",
            style={"display": "none"},
        ),
    ],
    fluid=True,
)


@callback(
    [
        Output("message", "children"),
        Output("message-row", "style"),
        Output("pulse-schedule", "src"),
        Output("pulse-schedule-row", "style"),
        Output("simulated-results", "src"),
        Output("simulated-results-row", "style"),
    ],
    Input("reload", "n_clicks"),
    Input("reset", "n_clicks"),
    prevent_initial_call=True,
)
def update_simulated_results(reload, reset):
    triggered_id = ctx.triggered_id

    if triggered_id == "reload":
        return _reload_simulated_results()
    elif triggered_id == "reset":
        return _reset_simulated_results()


def _reload_simulated_results():
    response = requests.get("http://localhost:8000/api/status")

    if response.status_code == 200:
        pulse_schedule_graph = response.json()["pulse_schedule_graph"]
        simulated_results_graph = response.json()["simulated_results_graph"]
        return (
            "",
            {"display": "none"},
            f"data:image/png;base64,{pulse_schedule_graph}",
            {"display": "block"},
            f"data:image/png;base64,{simulated_results_graph}",
            {"display": "block"},
        )
    else:
        error_message = response.json()["detail"]
        return (
            f"Error: “{error_message}”.",
            {"display": "block"},
            "",
            {"display": "none"},
            "",
            {"display": "none"},
        )


def _reset_simulated_results():
    response = requests.post("http://localhost:8000/api/reset")

    if response.status_code == 200:
        return (
            "Simulation was reset successfully.",
            {"display": "block"},
            "",
            {"display": "none"},
            "",
            {"display": "none"},
        )

    return (
        f"Error: {response.text}.",
        {"display": "block"},
        "",
        {"display": "none"},
        "",
        {"display": "none"},
    )
