"""
Dash web application for ctrl-viz Bode and Nyquist plots.
"""

from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update

from ctrl_viz.parse import parse_transfer_function
from ctrl_viz.web.plots import build_bode_fig, build_nyquist_fig

ASSETS_PATH = Path(__file__).resolve().parents[3] / "assets"

EMPTY_FIG = {"data": [], "layout": {"template": "plotly_white"}}


def handle_calculate(tf_expr, show_nyquist, show_bode):
    """
    Process a calculate request and return plot figures plus validation state.

    Returns
    -------
    tuple
        (nyquist_fig, bode_fig, input_invalid, feedback_children, feedback_style)
    """
    hidden_feedback = {"display": "none"}

    if not show_nyquist and not show_bode:
        return (
            EMPTY_FIG,
            EMPTY_FIG,
            True,
            "Select at least one plot type (Nyquist or Bode).",
            {"display": "block"},
        )

    try:
        system = parse_transfer_function(tf_expr)
    except ValueError as exc:
        return (
            EMPTY_FIG,
            EMPTY_FIG,
            True,
            str(exc),
            {"display": "block"},
        )

    nyquist_fig = (
        build_nyquist_fig(system) if show_nyquist else EMPTY_FIG
    )
    bode_fig = build_bode_fig(system) if show_bode else EMPTY_FIG

    return nyquist_fig, bode_fig, False, "", hidden_feedback


def create_app():
    """Create and configure the Dash application."""
    app = dash.Dash(
        "ControlViz",
        external_stylesheets=[dbc.themes.FLATLY],
        assets_folder=str(ASSETS_PATH),
        suppress_callback_exceptions=True,
    )

    app.layout = dbc.Container(
        [
            html.H1("ControlViz", className="app-title mt-4 mb-2"),
            html.P(
                "Enter a transfer function in s and plot Bode and/or Nyquist diagrams.",
                className="text-muted mb-4",
            ),
            html.P(
                "Syntax example: 1/(s^2+0.5*s+1) or (s+1)/(s^2+2*s+1)",
                className="syntax-hint mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="tf-input",
                            type="text",
                            placeholder="e.g. 1/(s^2+0.5*s+1)",
                            size="lg",
                            className="tf-input",
                            value="1/(s+1)",
                        ),
                        width=9,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Calculate",
                            id="calc-btn",
                            color="primary",
                            size="lg",
                            className="w-100",
                        ),
                        width=3,
                    ),
                ],
                className="g-2 mb-1",
            ),
            dbc.FormFeedback(
                id="tf-feedback",
                type="invalid",
                style={"display": "none"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Checkbox(
                            id="chk-nyquist",
                            label="Nyquist plot",
                            value=True,
                            className="me-4",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Checkbox(
                            id="chk-bode",
                            label="Bode plot",
                            value=False,
                        ),
                        width="auto",
                    ),
                ],
                className="mb-4 mt-3",
            ),
            html.Div(
                dcc.Graph(id="nyquist-graph", figure=EMPTY_FIG),
                id="nyquist-container",
                style={"display": "block"},
            ),
            html.Div(
                dcc.Graph(id="bode-graph", figure=EMPTY_FIG),
                id="bode-container",
                style={"display": "none"},
            ),
        ],
        fluid=True,
        className="app-container pb-5",
    )

    app.clientside_callback(
        """
        function(value) {
            if (value === null || value === undefined) {
                return [true, "Enter a transfer function.", {"display": "block"}];
            }

            const expr = value.trim();
            if (!expr) {
                return [true, "Enter a transfer function.", {"display": "block"}];
            }

            if (!/[s]/.test(expr)) {
                return [true, "Expression must contain the variable s.", {"display": "block"}];
            }

            if (!/^[0-9s+\\-*/().^ ]+$/.test(expr)) {
                return [true, "Invalid characters. Use s, numbers, +, -, *, /, (, ), ^.", {"display": "block"}];
            }

            let depth = 0;
            for (const ch of expr) {
                if (ch === "(") depth += 1;
                if (ch === ")") depth -= 1;
                if (depth < 0) {
                    return [true, "Unbalanced parentheses.", {"display": "block"}];
                }
            }
            if (depth !== 0) {
                return [true, "Unbalanced parentheses.", {"display": "block"}];
            }

            if (/[+\\-*/^]{2,}/.test(expr.replace(/\\s+/g, ""))) {
                return [true, "Invalid operator sequence.", {"display": "block"}];
            }

            return [false, "", {"display": "none"}];
        }
        """,
        Output("tf-input", "invalid"),
        Output("tf-feedback", "children"),
        Output("tf-feedback", "style"),
        Input("tf-input", "value"),
    )

    @app.callback(
        Output("nyquist-graph", "figure"),
        Output("bode-graph", "figure"),
        Output("tf-input", "invalid", allow_duplicate=True),
        Output("tf-feedback", "children", allow_duplicate=True),
        Output("tf-feedback", "style", allow_duplicate=True),
        Output("nyquist-container", "style"),
        Output("bode-container", "style"),
        Input("calc-btn", "n_clicks"),
        State("tf-input", "value"),
        State("chk-nyquist", "value"),
        State("chk-bode", "value"),
        prevent_initial_call=True,
    )
    def on_calculate(n_clicks, tf_expr, show_nyquist, show_bode):
        if not n_clicks:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        nyquist_fig, bode_fig, invalid, feedback, feedback_style = handle_calculate(
            tf_expr or "", bool(show_nyquist), bool(show_bode)
        )

        nyquist_style = {"display": "block"} if show_nyquist else {"display": "none"}
        bode_style = {"display": "block"} if show_bode else {"display": "none"}

        return (
            nyquist_fig,
            bode_fig,
            invalid,
            feedback,
            feedback_style,
            nyquist_style,
            bode_style,
        )

    return app


def main():
    """Run the Dash development server."""
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
