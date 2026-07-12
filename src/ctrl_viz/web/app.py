"""
Dash web application for ctrl-viz Bode and Nyquist plots.
"""

from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import numpy as np
from dash import Input, Output, State, dcc, html, no_update

from ctrl_viz.parse import parse_transfer_function
from ctrl_viz.web.plots import SOFT_DARK_TEMPLATE, build_bode_fig, build_nyquist_fig

ASSETS_PATH = Path(__file__).resolve().parents[3] / "assets"

PLOT_CONFIG = {"scrollZoom": True}

NYQUIST_OMEGA_MIN_DEFAULT = 0.01
NYQUIST_OMEGA_MAX_DEFAULT = 100
NYQUIST_X_MIN_DEFAULT = -1.5
NYQUIST_X_MAX_DEFAULT = 1.5
NYQUIST_Y_MIN_DEFAULT = -1.5
NYQUIST_Y_MAX_DEFAULT = 1.5

BODE_OMEGA_MIN_DEFAULT = 0.001
BODE_OMEGA_MAX_DEFAULT = 1000
BODE_FREQ_MIN_DEFAULT = 0.1
BODE_FREQ_MAX_DEFAULT = 10

DEFAULT_TF = "1/(s+1)"

EMPTY_FIG = {"data": [], "layout": {"template": "plotly_white"}}


def empty_fig(dark_mode=False):
    if dark_mode:
        return {
            "data": [],
            "layout": {
                "paper_bgcolor": "#2a2a3e",
                "plot_bgcolor": "#333348",
            },
        }
    return {"data": [], "layout": {"template": "plotly_white"}}


def plot_template(dark_mode=False):
    return SOFT_DARK_TEMPLATE if dark_mode else "plotly_white"


def _parse_float(value, default):
    if value is None or value == "":
        return default
    return float(value)


def _validate_range(min_val, max_val, label, positive=False):
    if min_val >= max_val:
        return f"{label}: minimum must be less than maximum."
    if positive and (min_val <= 0 or max_val <= 0):
        return f"{label}: values must be positive."
    return None


def _is_empty(value):
    return value is None or value == ""


def _parse_optional_range(min_val, max_val, label):
    """Return (min, max) tuple if both set, None if both blank, else error message."""
    min_empty = _is_empty(min_val)
    max_empty = _is_empty(max_val)
    if min_empty and max_empty:
        return None, None
    if min_empty or max_empty:
        return None, f"{label}: enter both min and max, or leave both blank."
    parsed_min = float(min_val)
    parsed_max = float(max_val)
    error = _validate_range(parsed_min, parsed_max, label)
    if error:
        return None, error
    return (parsed_min, parsed_max), None


def _build_omega(omega_min, omega_max, n_points=1000):
    return np.logspace(np.log10(omega_min), np.log10(omega_max), n_points)


def _build_calc_state(
    tf_expr,
    show_nyquist,
    show_bode,
    nyquist_omega_min,
    nyquist_omega_max,
    nyquist_x_min,
    nyquist_x_max,
    nyquist_y_min,
    nyquist_y_max,
    nyquist_unit_circle,
    nyquist_critical_point,
    bode_omega_min,
    bode_omega_max,
    bode_freq_min,
    bode_freq_max,
    bode_mag_min,
    bode_mag_max,
    bode_phase_min,
    bode_phase_max,
    dark_mode,
):
    return {
        "valid": True,
        "tf_expr": tf_expr,
        "show_nyquist": show_nyquist,
        "show_bode": show_bode,
        "nyquist_omega_min": nyquist_omega_min,
        "nyquist_omega_max": nyquist_omega_max,
        "nyquist_x_min": nyquist_x_min,
        "nyquist_x_max": nyquist_x_max,
        "nyquist_y_min": nyquist_y_min,
        "nyquist_y_max": nyquist_y_max,
        "nyquist_unit_circle": nyquist_unit_circle,
        "nyquist_critical_point": nyquist_critical_point,
        "bode_omega_min": bode_omega_min,
        "bode_omega_max": bode_omega_max,
        "bode_freq_min": bode_freq_min,
        "bode_freq_max": bode_freq_max,
        "bode_mag_min": bode_mag_min,
        "bode_mag_max": bode_mag_max,
        "bode_phase_min": bode_phase_min,
        "bode_phase_max": bode_phase_max,
        "dark_mode": dark_mode,
    }


def _run_calc_from_state(calc_state, theme_data=None, unit_circle=None, critical_point=None):
    dark_mode = (
        (theme_data or {}).get("dark", False)
        if theme_data is not None
        else calc_state.get("dark_mode", False)
    )
    return handle_calculate(
        calc_state["tf_expr"],
        calc_state["show_nyquist"],
        calc_state["show_bode"],
        calc_state["nyquist_omega_min"],
        calc_state["nyquist_omega_max"],
        calc_state["nyquist_x_min"],
        calc_state["nyquist_x_max"],
        calc_state["nyquist_y_min"],
        calc_state["nyquist_y_max"],
        unit_circle if unit_circle is not None else calc_state["nyquist_unit_circle"],
        critical_point if critical_point is not None else calc_state["nyquist_critical_point"],
        calc_state["bode_omega_min"],
        calc_state["bode_omega_max"],
        calc_state["bode_freq_min"],
        calc_state["bode_freq_max"],
        calc_state["bode_mag_min"],
        calc_state["bode_mag_max"],
        calc_state["bode_phase_min"],
        calc_state["bode_phase_max"],
        dark_mode=dark_mode,
    )


def _run_default_example(dark_mode=False):
    """Calculate plots for the default example transfer function."""
    return handle_calculate(
        DEFAULT_TF,
        show_nyquist=True,
        show_bode=False,
        nyquist_omega_min=None,
        nyquist_omega_max=None,
        nyquist_x_min=None,
        nyquist_x_max=None,
        nyquist_y_min=None,
        nyquist_y_max=None,
        nyquist_unit_circle=True,
        nyquist_critical_point=True,
        bode_omega_min=None,
        bode_omega_max=None,
        bode_freq_min=None,
        bode_freq_max=None,
        bode_mag_min=None,
        bode_mag_max=None,
        bode_phase_min=None,
        bode_phase_max=None,
        dark_mode=dark_mode,
    )


def handle_calculate(
    tf_expr,
    show_nyquist,
    show_bode,
    nyquist_omega_min,
    nyquist_omega_max,
    nyquist_x_min,
    nyquist_x_max,
    nyquist_y_min,
    nyquist_y_max,
    nyquist_unit_circle,
    nyquist_critical_point,
    bode_omega_min,
    bode_omega_max,
    bode_freq_min,
    bode_freq_max,
    bode_mag_min,
    bode_mag_max,
    bode_phase_min,
    bode_phase_max,
    dark_mode=False,
):
    """
    Process a calculate request and return plot figures plus validation state.

    Returns
    -------
    tuple
        (nyquist_fig, bode_fig, input_invalid, feedback_children, feedback_style)
    """
    hidden_feedback = {"display": "none"}
    empty = empty_fig(dark_mode)
    template = plot_template(dark_mode)

    if not show_nyquist and not show_bode:
        return (
            empty,
            empty,
            True,
            "Select at least one plot type (Nyquist or Bode).",
            {"display": "block"},
        )

    try:
        system = parse_transfer_function(tf_expr)
    except ValueError as exc:
        return (
            empty,
            empty,
            True,
            str(exc),
            {"display": "block"},
        )

    if show_nyquist:
        n_omega_min = _parse_float(nyquist_omega_min, NYQUIST_OMEGA_MIN_DEFAULT)
        n_omega_max = _parse_float(nyquist_omega_max, NYQUIST_OMEGA_MAX_DEFAULT)
        n_x_min = _parse_float(nyquist_x_min, NYQUIST_X_MIN_DEFAULT)
        n_x_max = _parse_float(nyquist_x_max, NYQUIST_X_MAX_DEFAULT)
        n_y_min = _parse_float(nyquist_y_min, NYQUIST_Y_MIN_DEFAULT)
        n_y_max = _parse_float(nyquist_y_max, NYQUIST_Y_MAX_DEFAULT)

        for error in (
            _validate_range(n_omega_min, n_omega_max, "Nyquist frequency sweep", positive=True),
            _validate_range(n_x_min, n_x_max, "Nyquist real axis"),
            _validate_range(n_y_min, n_y_max, "Nyquist imaginary axis"),
        ):
            if error:
                return empty, empty, True, error, {"display": "block"}

        nyquist_omega = _build_omega(n_omega_min, n_omega_max)
        nyquist_fig = build_nyquist_fig(
            system,
            omega=nyquist_omega,
            x_limits=(n_x_min, n_x_max),
            y_limits=(n_y_min, n_y_max),
            unit_circle=bool(nyquist_unit_circle),
            critical_point=bool(nyquist_critical_point),
            template=template,
        )
    else:
        nyquist_fig = empty

    if show_bode:
        b_omega_min = _parse_float(bode_omega_min, BODE_OMEGA_MIN_DEFAULT)
        b_omega_max = _parse_float(bode_omega_max, BODE_OMEGA_MAX_DEFAULT)
        b_freq_min = _parse_float(bode_freq_min, BODE_FREQ_MIN_DEFAULT)
        b_freq_max = _parse_float(bode_freq_max, BODE_FREQ_MAX_DEFAULT)

        for error in (
            _validate_range(b_omega_min, b_omega_max, "Bode frequency sweep", positive=True),
            _validate_range(b_freq_min, b_freq_max, "Bode frequency view", positive=True),
        ):
            if error:
                return empty, empty, True, error, {"display": "block"}

        mag_limits, mag_error = _parse_optional_range(
            bode_mag_min, bode_mag_max, "Bode magnitude view"
        )
        if mag_error:
            return empty, empty, True, mag_error, {"display": "block"}

        phase_limits, phase_error = _parse_optional_range(
            bode_phase_min, bode_phase_max, "Bode phase view"
        )
        if phase_error:
            return empty, empty, True, phase_error, {"display": "block"}

        bode_omega = _build_omega(b_omega_min, b_omega_max, n_points=500)
        bode_fig = build_bode_fig(
            system,
            omega=bode_omega,
            freq_limits=(b_freq_min, b_freq_max),
            mag_limits=mag_limits,
            phase_limits=phase_limits,
            template=template,
        )
    else:
        bode_fig = empty

    return nyquist_fig, bode_fig, False, "", hidden_feedback


def _optional_range_input(input_id, label, step="any"):
    return dbc.Col(
        [
            dbc.Label(label, className="small text-muted mb-0"),
            dbc.Input(
                id=input_id,
                type="number",
                step=step,
                size="sm",
                placeholder="auto",
            ),
        ],
        xs=6,
        sm=4,
        md=3,
        className="mb-2",
    )


def _range_input(input_id, label, default, step="any"):
    return dbc.Col(
        [
            dbc.Label(label, className="small text-muted mb-0"),
            dbc.Input(
                id=input_id,
                type="number",
                value=default,
                step=step,
                size="sm",
            ),
        ],
        xs=6,
        sm=4,
        md=3,
        className="mb-2",
    )


def create_navbar():
    """Build the orange navigation bar."""
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand(
                    "ControlViz",
                    href="/",
                    className="navbar-brand-controlviz",
                ),
                dbc.Nav(
                    [
                        dbc.NavLink("Plot", href="/", active="exact"),
                        dbc.NavLink("About", href="/about", active="exact"),
                        dbc.NavLink("Data Privacy", href="/data-privacy", active="exact"),
                    ],
                    navbar=True,
                    className="ms-3",
                ),
                dbc.Button(
                    "Dark",
                    id="theme-toggle",
                    color="light",
                    outline=True,
                    size="sm",
                    className="ms-auto theme-toggle-btn",
                ),
            ],
            fluid=True,
        ),
        dark=True,
        className="navbar-controlviz mb-4",
    )


def _default_calc_state(dark_mode=False):
    return _build_calc_state(
        DEFAULT_TF,
        True,
        False,
        None,
        None,
        None,
        None,
        None,
        None,
        True,
        True,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        dark_mode,
    )


def plot_page_layout():
    """Build the main plot page layout."""
    nyquist_fig, bode_fig, invalid, _, _ = _run_default_example(False)
    if invalid:
        nyquist_fig, bode_fig = EMPTY_FIG, EMPTY_FIG

    return dbc.Container(
        [
            html.P(
                "Enter a transfer function in s and plot Bode and/or Nyquist diagrams.",
                className="text-muted mb-4",
            ),
            html.P(
                "Syntax examples: 1/(s(s+1)), 4s, 1/(s^2+0.5*s+1)",
                className="syntax-hint mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="tf-input",
                            type="text",
                            placeholder="e.g. 1/(s(s+1))",
                            size="lg",
                            className="tf-input",
                            value=DEFAULT_TF,
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
                className="mb-3 mt-3",
            ),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.Row(
                                [
                                    _range_input(
                                        "nyquist-omega-min",
                                        "ω min (rad/s)",
                                        NYQUIST_OMEGA_MIN_DEFAULT,
                                    ),
                                    _range_input(
                                        "nyquist-omega-max",
                                        "ω max (rad/s)",
                                        NYQUIST_OMEGA_MAX_DEFAULT,
                                    ),
                                    _range_input(
                                        "nyquist-x-min",
                                        "Real min",
                                        NYQUIST_X_MIN_DEFAULT,
                                    ),
                                    _range_input(
                                        "nyquist-x-max",
                                        "Real max",
                                        NYQUIST_X_MAX_DEFAULT,
                                    ),
                                    _range_input(
                                        "nyquist-y-min",
                                        "Imag min",
                                        NYQUIST_Y_MIN_DEFAULT,
                                    ),
                                    _range_input(
                                        "nyquist-y-max",
                                        "Imag max",
                                        NYQUIST_Y_MAX_DEFAULT,
                                    ),
                                ],
                                className="g-2",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Checkbox(
                                            id="chk-nyquist-unit-circle",
                                            label="Show unit circle",
                                            value=True,
                                            className="me-4",
                                        ),
                                        width="auto",
                                    ),
                                    dbc.Col(
                                        dbc.Checkbox(
                                            id="chk-nyquist-critical-point",
                                            label="Show critical point (-1, 0)",
                                            value=True,
                                        ),
                                        width="auto",
                                    ),
                                ],
                                className="mt-2",
                            ),
                        ],
                        title="Nyquist plot settings",
                        item_id="nyquist-settings",
                    ),
                    dbc.AccordionItem(
                        dbc.Row(
                            [
                                _range_input(
                                    "bode-omega-min",
                                    "ω min (rad/s)",
                                    BODE_OMEGA_MIN_DEFAULT,
                                ),
                                _range_input(
                                    "bode-omega-max",
                                    "ω max (rad/s)",
                                    BODE_OMEGA_MAX_DEFAULT,
                                ),
                                _range_input(
                                    "bode-freq-min",
                                    "Freq view min (rad/s)",
                                    BODE_FREQ_MIN_DEFAULT,
                                ),
                                _range_input(
                                    "bode-freq-max",
                                    "Freq view max (rad/s)",
                                    BODE_FREQ_MAX_DEFAULT,
                                ),
                                _optional_range_input(
                                    "bode-mag-min",
                                    "Mag view min (dB)",
                                ),
                                _optional_range_input(
                                    "bode-mag-max",
                                    "Mag view max (dB)",
                                ),
                                _optional_range_input(
                                    "bode-phase-min",
                                    "Phase view min (deg)",
                                ),
                                _optional_range_input(
                                    "bode-phase-max",
                                    "Phase view max (deg)",
                                ),
                            ],
                            className="g-2",
                        ),
                        title="Bode plot settings",
                        item_id="bode-settings",
                    ),
                ],
                id="plot-settings-accordion",
                start_collapsed=True,
                always_open=False,
                className="mb-4",
            ),
            html.Div(
                dcc.Graph(id="nyquist-graph", figure=nyquist_fig, config=PLOT_CONFIG),
                id="nyquist-container",
                style={"display": "block"},
            ),
            html.Div(
                dcc.Graph(id="bode-graph", figure=bode_fig, config=PLOT_CONFIG),
                id="bode-container",
                style={"display": "none"},
            ),
        ],
        fluid=True,
        className="app-container pb-5",
    )


def about_layout():
    """Build the About page layout."""
    return dbc.Container(
        [
            html.H2("About ControlViz", className="mb-4"),
            html.P(
                "ControlViz is a tool for visualizing control systems using "
                "Bode and Nyquist plots. Enter a transfer function in the "
                "complex variable s and generate interactive frequency-domain "
                "plots in your browser.",
                className="mb-3",
            ),
            html.H4("Syntax", className="mt-4 mb-2"),
            html.P("Supported expression syntax includes:"),
            html.Ul(
                [
                    html.Li("Explicit multiplication: 0.5*s, 2*s+1"),
                    html.Li("Implicit multiplication: 4s, 1/(s(s+1)), (s+1)(s+2)"),
                    html.Li("Powers with caret: s^2"),
                    html.Li("Rational expressions: (s+1)/(s^2+2*s+1)"),
                ],
                className="mb-3",
            ),
            html.H4("Plot settings", className="mt-4 mb-2"),
            html.P(
                "Use the Plot settings accordion on the main page to configure "
                "frequency sweep ranges and initial axis view limits for both "
                "Nyquist and Bode plots."
            ),
            html.H4("Feedback", className="mt-4 mb-2"),
            html.P(
                "This was a small free time project because I did not find a good tool "
                "for visualization when studying control systems. I hope this "
                "visualization is useful for others as well."
            ),
            html.P(
                "Please reach out with any feedback on usability, features, and so on."
            ),
            html.P(
                [
                    "Contact me at ",
                    html.A("control@fenker.eu", href="mailto:control@fenker.eu"),
                    ".",
                ]
            ),
            html.P("I am looking forward to your suggestions :)"),
            html.H4("Source", className="mt-4 mb-2"),
            html.P(
                [
                    "Source code and documentation: ",
                    html.A(
                        "github.com/j3f-me/ctrl-viz",
                        href="https://github.com/j3f-me/ctrl-viz",
                        target="_blank",
                    ),
                ]
            ),
            html.P("Licensed under the MIT License.", className="text-muted mt-4"),
        ],
        fluid=True,
        className="app-container pb-5",
    )


def _privacy_section(title, children):
    return html.Div(
        [
            html.H4(title, className="mt-4 mb-2"),
            *children,
        ]
    )


def data_privacy_layout():
    """Build the Data Privacy information page."""
    return dbc.Container(
        [
            html.H2("Data Privacy Information", className="mb-4"),
            html.P(
                "This page explains how personal data is processed when you use "
                "the ControlViz web application. It is structured according to "
                "the transparency requirements of Articles 12–14 of the EU "
                "General Data Protection Regulation (GDPR).",
                className="mb-3",
            ),
            html.P(
                [
                    "Guidance on the content of website privacy notices: ",
                    html.A(
                        "dr-dsgvo.de (English overview)",
                        href="https://dr-dsgvo.de/datenschutzerklaerung-auf-webseiten-inhalt-en/",
                        target="_blank",
                        rel="noopener noreferrer",
                    ),
                    ".",
                ],
                className="text-muted small mb-3",
            ),
            _privacy_section(
                "Controller",
                [
                    html.P("The controller responsible for this website is:"),
                    html.Ul(
                        [
                            html.Li("Jan Fenker"),
                            html.Li(
                                [
                                    "Contact: ",
                                    html.A(
                                        "control@fenker.eu",
                                        href="mailto:control@fenker.eu",
                                    ),
                                ]
                            ),
                        ],
                        className="mb-3",
                    ),
                ],
            ),
            _privacy_section(
                "Overview",
                [
                    html.P(
                        "ControlViz is a technical visualization tool. You enter "
                        "a transfer function; the app computes Bode and/or "
                        "Nyquist plots in your browser session. We do not operate "
                        "user accounts, newsletters, contact forms, or analytics "
                        "on this site."
                    ),
                    html.P(
                        "Visiting a website always involves some processing of "
                        "personal data (for example your IP address when "
                        "connecting to a server). The sections below list the "
                        "processing operations that apply to this application."
                    ),
                ],
            ),
            _privacy_section(
                "Cookies",
                [
                    html.P(
                        [
                            html.Strong("This application does not set HTTP cookies."),
                            " Neither Dash (the web framework) nor Flask (the "
                            "underlying server library) sets cookies in the "
                            "default configuration used here. Plotly.js, which "
                            "renders the interactive charts, is delivered from "
                            "the same server as the app and does not set "
                            "tracking cookies in this setup.",
                        ]
                    ),
                    html.P(
                        "Some browsers or privacy extensions may still show "
                        "storage entries for this site. That is not the same as "
                        "a cookie, but similar transparency obligations apply "
                        "under the GDPR (see “Browser storage” below)."
                    ),
                ],
            ),
            _privacy_section(
                "Browser storage (localStorage)",
                [
                    html.P(
                        "Besides cookies, websites can store small amounts of "
                        "data in your browser. ControlViz uses one persistent "
                        "entry:"
                    ),
                    html.Table(
                        [
                            html.Thead(
                                html.Tr(
                                    [
                                        html.Th("Storage key"),
                                        html.Th("Type"),
                                        html.Th("Purpose"),
                                        html.Th("Retention"),
                                    ]
                                )
                            ),
                            html.Tbody(
                                html.Tr(
                                    [
                                        html.Td(html.Code("theme-store")),
                                        html.Td("localStorage"),
                                        html.Td("Remembers light/dark mode"),
                                        html.Td(
                                            "Until you clear site data in your browser"
                                        ),
                                    ]
                                )
                            ),
                        ],
                        className="table table-sm table-bordered mb-3",
                    ),
                    html.P(
                        "Plot settings and calculation state are kept in browser "
                        "memory only (not in localStorage) and are lost when you "
                        "reload the page."
                    ),
                    html.P(
                        "You can delete the theme preference at any time via "
                        "your browser settings (clear site data / local storage "
                        "for this origin). The app then defaults to light mode."
                    ),
                ],
            ),
            _privacy_section(
                "Plotly and Dash",
                [
                    html.P(
                        [
                            "The user interface is built with ",
                            html.A(
                                "Dash",
                                href="https://dash.plotly.com/",
                                target="_blank",
                                rel="noopener noreferrer",
                            ),
                            " and ",
                            html.A(
                                "Plotly.js",
                                href="https://plotly.com/javascript/",
                                target="_blank",
                                rel="noopener noreferrer",
                            ),
                            " (open-source libraries by Plotly Technologies, Inc., "
                            "based in the United States).",
                        ]
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "Plotly.js is bundled with the app and served "
                                "from the same origin. It is not loaded from "
                                "Plotly’s cloud services."
                            ),
                            html.Li(
                                "No usage data or transfer functions are sent "
                                "to Plotly Inc. when you use this application."
                            ),
                            html.Li(
                                "Plotly does not receive cookies from this app "
                                "and does not operate analytics here."
                            ),
                            html.Li(
                                "Chart zooming and panning are processed locally "
                                "in your browser."
                            ),
                        ],
                        className="mb-3",
                    ),
                ],
            ),
            _privacy_section(
                "Transfer functions and plot calculations",
                [
                    html.P(
                        "When you click Calculate, your transfer function "
                        "expression and plot settings are sent to the server "
                        "running ControlViz so that the frequency response can "
                        "be computed. The result is returned to your browser "
                        "for display."
                    ),
                    html.P(
                        "The application does not persistently store your "
                        "expressions or plot settings on the server. Data exists "
                        "only for the duration of the request and your open "
                        "browser session."
                    ),
                ],
            ),
            _privacy_section(
                "External resources (CDN)",
                [
                    html.P(
                        "The visual theme (Bootstrap “Flatly”) is loaded from "
                        "the jsDelivr content delivery network:"
                    ),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    "Provider: jsDelivr (Prospect One, s.r.o., ",
                                    html.A(
                                        "jsdelivr.com",
                                        href="https://www.jsdelivr.com/",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    ),
                                    ")",
                                ]
                            ),
                            html.Li(
                                [
                                    "URL: ",
                                    html.Code(
                                        "https://cdn.jsdelivr.net/npm/bootswatch@5.3.6/dist/flatly/bootstrap.min.css"
                                    ),
                                ]
                            ),
                            html.Li(
                                "Purpose: styling of buttons, layout, and navigation"
                            ),
                            html.Li(
                                "When your browser requests this file, jsDelivr "
                                "may process your IP address and technical "
                                "connection data to deliver the stylesheet."
                            ),
                        ],
                        className="mb-3",
                    ),
                ],
            ),
            _privacy_section(
                "Server log files",
                [
                    html.P(
                        "If this application is operated on a publicly reachable "
                        "web server, the server or hosting provider typically "
                        "records access data in log files (for example IP "
                        "address, date and time of access, requested URL, browser "
                        "type). This processing is necessary to ensure "
                        "operation and security of the service."
                    ),
                    html.P(
                        "The exact retention period and recipient depend on your "
                        "hosting setup and must be stated by the operator of "
                        "the live deployment."
                    ),
                ],
            ),
            _privacy_section(
                "Contact by e-mail",
                [
                    html.P(
                        [
                            "If you contact us at ",
                            html.A("control@fenker.eu", href="mailto:control@fenker.eu"),
                            ", we process the personal data you provide (at "
                            "minimum your e-mail address and message content) "
                            "solely to handle your enquiry.",
                        ]
                    ),
                ],
            ),
            _privacy_section(
                "Legal bases",
                [
                    html.P(
                        "Depending on the situation, processing is based on:"
                    ),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Art. 6(1)(b) GDPR"),
                                    " — performance of steps at your request "
                                    "(computing and displaying plots).",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Art. 6(1)(f) GDPR"),
                                    " — legitimate interests in operating, "
                                    "securing, and improving the website "
                                    "(server logs, CDN delivery, theme "
                                    "preference), where your interests do not "
                                    "override ours.",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Art. 6(1)(a) GDPR"),
                                    " — consent, where applicable (for example "
                                    "if optional non-essential storage were "
                                    "added in the future).",
                                ]
                            ),
                        ],
                        className="mb-3",
                    ),
                ],
            ),
            _privacy_section(
                "Your rights",
                [
                    html.P("Under the GDPR, you have the right to:"),
                    html.Ul(
                        [
                            html.Li(
                                "request access to your personal data (Art. 15)"
                            ),
                            html.Li(
                                "request rectification of inaccurate data (Art. 16)"
                            ),
                            html.Li(
                                "request erasure, where applicable (Art. 17)"
                            ),
                            html.Li(
                                "request restriction of processing (Art. 18)"
                            ),
                            html.Li(
                                "data portability, where applicable (Art. 20)"
                            ),
                            html.Li(
                                "object to processing based on legitimate "
                                "interests (Art. 21)"
                            ),
                            html.Li(
                                "withdraw consent at any time, without affecting "
                                "lawfulness of prior processing (Art. 7(3))"
                            ),
                            html.Li(
                                "lodge a complaint with a supervisory authority "
                                "(Art. 77), typically in your country of "
                                "residence or work."
                            ),
                        ],
                        className="mb-3",
                    ),
                    html.P(
                        [
                            "To exercise these rights, contact ",
                            html.A("control@fenker.eu", href="mailto:control@fenker.eu"),
                            ".",
                        ]
                    ),
                ],
            ),
            html.P(
                "Last updated: July 2026.",
                className="text-muted mt-4",
            ),
            html.P(
                "This notice is provided for transparency and does not replace "
                "individual legal advice. Operators of public deployments should "
                "review it against their hosting environment and national "
                "requirements (for example an imprint page).",
                className="text-muted small",
            ),
        ],
        fluid=True,
        className="app-container pb-5",
    )


def create_app():
    """Create and configure the Dash application."""
    app = dash.Dash(
        "ControlViz",
        external_stylesheets=[dbc.themes.FLATLY],
        assets_folder=str(ASSETS_PATH),
        suppress_callback_exceptions=True,
    )

    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="theme-store", storage_type="local", data={"dark": False}),
            dcc.Store(id="calc-store", data=_default_calc_state(False)),
            create_navbar(),
            html.Div(id="page-content"),
        ],
        id="app-root",
        className="theme-light",
    )

    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
    )
    def display_page(pathname):
        if pathname == "/about":
            return about_layout()
        if pathname == "/data-privacy":
            return data_privacy_layout()
        return plot_page_layout()

    @app.callback(
        Output("theme-store", "data"),
        Input("theme-toggle", "n_clicks"),
        State("theme-store", "data"),
        prevent_initial_call=True,
    )
    def toggle_theme(n_clicks, theme_data):
        dark = not (theme_data or {}).get("dark", False)
        return {"dark": dark}

    @app.callback(
        Output("app-root", "className"),
        Output("theme-toggle", "children"),
        Input("theme-store", "data"),
    )
    def apply_theme(theme_data):
        dark = (theme_data or {}).get("dark", False)
        return (
            "theme-dark" if dark else "theme-light",
            "Light" if dark else "Dark",
        )

    @app.callback(
        Output("nyquist-graph", "figure", allow_duplicate=True),
        Output("bode-graph", "figure", allow_duplicate=True),
        Input("theme-store", "data"),
        Input("chk-nyquist-unit-circle", "value"),
        Input("chk-nyquist-critical-point", "value"),
        State("calc-store", "data"),
        prevent_initial_call="initial_duplicate",
    )
    def refresh_plots(theme_data, unit_circle, critical_point, calc_state):
        if not calc_state or not calc_state.get("valid"):
            return no_update, no_update

        nyquist_fig, bode_fig, invalid, _, _ = _run_calc_from_state(
            calc_state,
            theme_data=theme_data,
            unit_circle=unit_circle,
            critical_point=critical_point,
        )
        if invalid:
            return no_update, no_update
        return nyquist_fig, bode_fig

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
        Output("calc-store", "data"),
        Input("calc-btn", "n_clicks"),
        State("tf-input", "value"),
        State("chk-nyquist", "value"),
        State("chk-bode", "value"),
        State("nyquist-omega-min", "value"),
        State("nyquist-omega-max", "value"),
        State("nyquist-x-min", "value"),
        State("nyquist-x-max", "value"),
        State("nyquist-y-min", "value"),
        State("nyquist-y-max", "value"),
        State("chk-nyquist-unit-circle", "value"),
        State("chk-nyquist-critical-point", "value"),
        State("bode-omega-min", "value"),
        State("bode-omega-max", "value"),
        State("bode-freq-min", "value"),
        State("bode-freq-max", "value"),
        State("bode-mag-min", "value"),
        State("bode-mag-max", "value"),
        State("bode-phase-min", "value"),
        State("bode-phase-max", "value"),
        State("theme-store", "data"),
        prevent_initial_call=True,
    )
    def on_calculate(
        n_clicks,
        tf_expr,
        show_nyquist,
        show_bode,
        nyquist_omega_min,
        nyquist_omega_max,
        nyquist_x_min,
        nyquist_x_max,
        nyquist_y_min,
        nyquist_y_max,
        nyquist_unit_circle,
        nyquist_critical_point,
        bode_omega_min,
        bode_omega_max,
        bode_freq_min,
        bode_freq_max,
        bode_mag_min,
        bode_mag_max,
        bode_phase_min,
        bode_phase_max,
        theme_data,
    ):
        if not n_clicks:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        dark_mode = (theme_data or {}).get("dark", False)
        nyquist_fig, bode_fig, invalid, feedback, feedback_style = handle_calculate(
            tf_expr or "",
            bool(show_nyquist),
            bool(show_bode),
            nyquist_omega_min,
            nyquist_omega_max,
            nyquist_x_min,
            nyquist_x_max,
            nyquist_y_min,
            nyquist_y_max,
            nyquist_unit_circle,
            nyquist_critical_point,
            bode_omega_min,
            bode_omega_max,
            bode_freq_min,
            bode_freq_max,
            bode_mag_min,
            bode_mag_max,
            bode_phase_min,
            bode_phase_max,
            dark_mode=dark_mode,
        )

        nyquist_style = {"display": "block"} if show_nyquist else {"display": "none"}
        bode_style = {"display": "block"} if show_bode else {"display": "none"}

        if invalid:
            calc_state = no_update
        else:
            calc_state = _build_calc_state(
                tf_expr or "",
                bool(show_nyquist),
                bool(show_bode),
                nyquist_omega_min,
                nyquist_omega_max,
                nyquist_x_min,
                nyquist_x_max,
                nyquist_y_min,
                nyquist_y_max,
                nyquist_unit_circle,
                nyquist_critical_point,
                bode_omega_min,
                bode_omega_max,
                bode_freq_min,
                bode_freq_max,
                bode_mag_min,
                bode_mag_max,
                bode_phase_min,
                bode_phase_max,
                dark_mode,
            )

        return (
            nyquist_fig,
            bode_fig,
            invalid,
            feedback,
            feedback_style,
            nyquist_style,
            bode_style,
            calc_state,
        )

    return app


def main():
    """Run the Dash development server."""
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
