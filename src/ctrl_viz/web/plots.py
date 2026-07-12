"""
Plotly figure builders for the ctrl-viz web UI.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ctrl_viz.frequency import compute_frequency_response


def build_bode_fig(system, omega=None, title=None):
    """
    Build a Plotly Bode plot figure (magnitude + phase).

    Parameters
    ----------
    system : control.TransferFunction or control.StateSpace
        The system to plot.
    omega : array_like, optional
        Frequency range in rad/s.
    title : str, optional
        Plot title.

    Returns
    -------
    plotly.graph_objects.Figure
        Bode plot figure with two subplots.
    """
    mag, phase, omega_out = compute_frequency_response(system, omega)
    freq_plot = omega_out.flatten()
    mag_plot = 20 * np.log10(np.abs(mag)).flatten()
    phase_plot = np.rad2deg(phase).flatten()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=("Magnitude (dB)", "Phase (deg)"),
    )

    fig.add_trace(
        go.Scatter(
            x=freq_plot,
            y=mag_plot,
            mode="lines",
            name="Magnitude",
            line=dict(color="blue"),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=freq_plot,
            y=phase_plot,
            mode="lines",
            name="Phase",
            line=dict(color="red"),
        ),
        row=2,
        col=1,
    )

    fig.update_xaxes(type="log", title_text="Frequency (rad/s)", row=2, col=1)
    fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
    fig.update_yaxes(title_text="Phase (deg)", row=2, col=1)

    fig.update_layout(
        title=title or "Bode Plot",
        showlegend=False,
        height=600,
        margin=dict(l=60, r=30, t=60, b=50),
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgray", row=1, col=1)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgray", row=2, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgray", row=1, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgray", row=2, col=1)

    return fig


def build_nyquist_fig(
    system, omega=None, title=None, unit_circle=True, arrows=True
):
    """
    Build a Plotly Nyquist plot figure.

    Parameters
    ----------
    system : control.TransferFunction or control.StateSpace
        The system to plot.
    omega : array_like, optional
        Frequency range in rad/s.
    title : str, optional
        Plot title.
    unit_circle : bool, optional
        Draw the unit circle. Default is True.
    arrows : bool, optional
        Show direction arrow. Default is True.

    Returns
    -------
    plotly.graph_objects.Figure
        Nyquist plot figure.
    """
    if omega is None:
        omega = np.logspace(-2, 2, 1000)

    mag, phase, _omega_out = compute_frequency_response(
        system, omega, unwrap_phase=False
    )

    response = mag * np.exp(1j * phase)
    real_part = np.real(response).flatten()
    imag_part = np.imag(response).flatten()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=real_part,
            y=imag_part,
            mode="lines",
            name="ω > 0",
            line=dict(color="blue", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=real_part,
            y=-imag_part,
            mode="lines",
            name="ω < 0",
            line=dict(color="blue", width=2, dash="dash"),
            opacity=0.7,
        )
    )

    if unit_circle:
        theta = np.linspace(0, 2 * np.pi, 100)
        fig.add_trace(
            go.Scatter(
                x=np.cos(theta),
                y=np.sin(theta),
                mode="lines",
                name="Unit circle",
                line=dict(color="black", dash="dash"),
                opacity=0.3,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[-1],
            y=[0],
            mode="markers",
            name="Critical point (-1, 0)",
            marker=dict(color="red", size=12, symbol="x"),
        )
    )

    annotations = []
    if arrows and len(real_part) > 2:
        mid_idx = len(real_part) // 2
        if 0 < mid_idx < len(real_part) - 1:
            x0 = real_part[mid_idx]
            y0 = imag_part[mid_idx]
            x1 = real_part[mid_idx + 1]
            y1 = imag_part[mid_idx + 1]
            annotations.append(
                dict(
                    x=x1,
                    y=y1,
                    ax=x0,
                    ay=y0,
                    xref="x",
                    yref="y",
                    axref="x",
                    ayref="y",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=2,
                    arrowcolor="blue",
                )
            )

    fig.update_layout(
        title=title or "Nyquist Plot",
        xaxis_title="Real",
        yaxis_title="Imaginary",
        height=500,
        margin=dict(l=60, r=30, t=60, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        annotations=annotations,
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightgray",
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="black",
        scaleanchor="y",
        scaleratio=1,
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightgray",
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="black",
    )

    return fig
