from dash import html

header = html.Div(
    [
        html.H1("qua-qsim"),
        html.A("Dashboard", href="/dashboard/"),
        " | ",
        html.A("Editor", href="/editor/"),
    ]
)
