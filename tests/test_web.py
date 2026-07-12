"""
Tests for Plotly web plot builders and calculate handler.
"""

import pytest
import control

from ctrl_viz.web.app import EMPTY_FIG, handle_calculate
from ctrl_viz.web.plots import build_bode_fig, build_nyquist_fig


@pytest.fixture
def simple_system():
    return control.TransferFunction([1], [1, 1])


class TestWebPlots:
    """Tests for Plotly figure builders."""

    def test_build_bode_fig_returns_subplots(self, simple_system):
        fig = build_bode_fig(simple_system)
        assert len(fig.data) == 2
        assert hasattr(fig.layout, "xaxis2")
        assert hasattr(fig.layout, "yaxis2")

    def test_build_nyquist_fig_has_traces(self, simple_system):
        fig = build_nyquist_fig(simple_system)
        trace_names = {trace.name for trace in fig.data}
        assert "ω > 0" in trace_names
        assert "ω < 0" in trace_names
        assert "Critical point (-1, 0)" in trace_names

    def test_build_nyquist_fig_unit_circle(self, simple_system):
        fig = build_nyquist_fig(simple_system, unit_circle=True)
        trace_names = {trace.name for trace in fig.data}
        assert "Unit circle" in trace_names

    def test_build_nyquist_fig_no_unit_circle(self, simple_system):
        fig = build_nyquist_fig(simple_system, unit_circle=False)
        trace_names = {trace.name for trace in fig.data}
        assert "Unit circle" not in trace_names


class TestHandleCalculate:
    """Tests for the calculate handler logic."""

    def test_nyquist_only(self):
        nyquist_fig, bode_fig, invalid, feedback, style = handle_calculate(
            "1/(s+1)", show_nyquist=True, show_bode=False
        )
        assert not invalid
        assert len(nyquist_fig.data) > 0
        assert bode_fig == EMPTY_FIG
        assert feedback == ""

    def test_bode_only(self):
        nyquist_fig, bode_fig, invalid, feedback, style = handle_calculate(
            "1/(s+1)", show_nyquist=False, show_bode=True
        )
        assert not invalid
        assert nyquist_fig == EMPTY_FIG
        assert len(bode_fig.data) == 2
        assert feedback == ""

    def test_both_plots(self):
        nyquist_fig, bode_fig, invalid, feedback, style = handle_calculate(
            "1/(s^2+0.5*s+1)", show_nyquist=True, show_bode=True
        )
        assert not invalid
        assert len(nyquist_fig.data) > 0
        assert len(bode_fig.data) == 2

    def test_no_plot_selected(self):
        _, _, invalid, feedback, style = handle_calculate(
            "1/(s+1)", show_nyquist=False, show_bode=False
        )
        assert invalid
        assert "at least one" in feedback.lower()
        assert style["display"] == "block"

    def test_invalid_transfer_function(self):
        _, _, invalid, feedback, style = handle_calculate(
            "not-a-tf", show_nyquist=True, show_bode=False
        )
        assert invalid
        assert feedback
        assert style["display"] == "block"
