"""
Tests for Plotly web plot builders and calculate handler.
"""

import pytest
import control

from ctrl_viz.web.app import (
    _build_calc_state,
    _run_calc_from_state,
    empty_fig,
    handle_calculate,
)
from ctrl_viz.web.plots import SOFT_DARK_TEMPLATE, build_bode_fig, build_nyquist_fig


def _default_calculate_kwargs():
    return {
        "nyquist_omega_min": None,
        "nyquist_omega_max": None,
        "nyquist_x_min": None,
        "nyquist_x_max": None,
        "nyquist_y_min": None,
        "nyquist_y_max": None,
        "nyquist_unit_circle": True,
        "nyquist_critical_point": True,
        "bode_omega_min": None,
        "bode_omega_max": None,
        "bode_freq_min": None,
        "bode_freq_max": None,
        "bode_mag_min": None,
        "bode_mag_max": None,
        "bode_phase_min": None,
        "bode_phase_max": None,
        "dark_mode": False,
    }


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

    def test_build_bode_fig_freq_limits_log_scale(self, simple_system):
        fig = build_bode_fig(simple_system, freq_limits=(0.1, 10))
        assert fig.layout.xaxis2.range == (-1.0, 1.0)

    def test_build_bode_fig_autoscales_y_axes_with_freq_limits(self, simple_system):
        fig = build_bode_fig(simple_system, freq_limits=(0.1, 10))
        assert fig.layout.yaxis.autorange is True
        assert fig.layout.yaxis2.autorange is True
        assert fig.layout.yaxis.range is None
        assert fig.layout.yaxis2.range is None

    def test_build_bode_fig_mag_limits(self, simple_system):
        fig = build_bode_fig(simple_system, mag_limits=(-20, 20))
        assert fig.layout.yaxis.range == (-20, 20)
        assert fig.layout.yaxis.autorange is False

    def test_build_bode_fig_phase_limits(self, simple_system):
        fig = build_bode_fig(simple_system, phase_limits=(-90, 0))
        assert fig.layout.yaxis2.range == (-90, 0)
        assert fig.layout.yaxis2.autorange is False

    def test_build_bode_fig_soft_dark_template(self, simple_system):
        fig = build_bode_fig(simple_system, template=SOFT_DARK_TEMPLATE)
        bgcolor = fig.layout.template.layout.paper_bgcolor
        assert bgcolor in ("#2a2a3e", "rgb(42, 42, 62)")

    def test_build_nyquist_fig_has_traces(self, simple_system):
        fig = build_nyquist_fig(simple_system)
        trace_names = {trace.name for trace in fig.data}
        assert "ω > 0" in trace_names
        assert "ω < 0" in trace_names
        assert "Critical point (-1, 0)" in trace_names

    def test_build_nyquist_fig_no_critical_point(self, simple_system):
        fig = build_nyquist_fig(simple_system, critical_point=False)
        trace_names = {trace.name for trace in fig.data}
        assert "Critical point (-1, 0)" not in trace_names

    def test_build_nyquist_fig_axis_limits(self, simple_system):
        fig = build_nyquist_fig(simple_system, x_limits=(-1.5, 1.5), y_limits=(-1.5, 1.5))
        assert fig.layout.xaxis.range == (-1.5, 1.5)
        assert fig.layout.yaxis.range == (-1.5, 1.5)

    def test_build_nyquist_fig_unit_circle(self, simple_system):
        fig = build_nyquist_fig(simple_system, unit_circle=True)
        trace_names = {trace.name for trace in fig.data}
        assert "Unit circle" in trace_names

    def test_build_nyquist_fig_no_unit_circle(self, simple_system):
        fig = build_nyquist_fig(simple_system, unit_circle=False)
        trace_names = {trace.name for trace in fig.data}
        assert "Unit circle" not in trace_names

    def test_build_nyquist_fig_soft_dark_template(self, simple_system):
        fig = build_nyquist_fig(simple_system, template=SOFT_DARK_TEMPLATE)
        bgcolor = fig.layout.template.layout.paper_bgcolor
        assert bgcolor in ("#2a2a3e", "rgb(42, 42, 62)")


class TestHandleCalculate:
    """Tests for the calculate handler logic."""

    def test_nyquist_only(self):
        nyquist_fig, bode_fig, invalid, feedback, style = handle_calculate(
            "1/(s+1)", show_nyquist=True, show_bode=False, **_default_calculate_kwargs()
        )
        assert not invalid
        assert len(nyquist_fig.data) > 0
        assert bode_fig == empty_fig(False)
        assert feedback == ""

    def test_bode_only(self):
        nyquist_fig, bode_fig, invalid, feedback, style = handle_calculate(
            "1/(s+1)", show_nyquist=False, show_bode=True, **_default_calculate_kwargs()
        )
        assert not invalid
        assert nyquist_fig == empty_fig(False)
        assert len(bode_fig.data) == 2
        assert feedback == ""

    def test_both_plots(self):
        nyquist_fig, bode_fig, invalid, feedback, style = handle_calculate(
            "1/(s^2+0.5*s+1)",
            show_nyquist=True,
            show_bode=True,
            **_default_calculate_kwargs(),
        )
        assert not invalid
        assert len(nyquist_fig.data) > 0
        assert len(bode_fig.data) == 2

    def test_implicit_multiplication(self):
        nyquist_fig, bode_fig, invalid, feedback, style = handle_calculate(
            "4s/(s+1)",
            show_nyquist=True,
            show_bode=False,
            **_default_calculate_kwargs(),
        )
        assert not invalid
        assert len(nyquist_fig.data) > 0
        assert feedback == ""

    def test_nyquist_without_critical_point(self):
        kwargs = {**_default_calculate_kwargs(), "nyquist_critical_point": False}
        nyquist_fig, _, invalid, _, _ = handle_calculate(
            "1/(s+1)",
            show_nyquist=True,
            show_bode=False,
            **kwargs,
        )
        assert not invalid
        trace_names = {trace.name for trace in nyquist_fig.data}
        assert "Critical point (-1, 0)" not in trace_names

    def test_dark_mode_template(self):
        kwargs = {**_default_calculate_kwargs(), "dark_mode": True}
        _, bode_fig, invalid, _, _ = handle_calculate(
            "1/(s+1)",
            show_nyquist=False,
            show_bode=True,
            **kwargs,
        )
        assert not invalid
        bgcolor = bode_fig.layout.template.layout.paper_bgcolor
        assert bgcolor in ("#2a2a3e", "rgb(42, 42, 62)")

    def test_no_plot_selected(self):
        _, _, invalid, feedback, style = handle_calculate(
            "1/(s+1)", show_nyquist=False, show_bode=False, **_default_calculate_kwargs()
        )
        assert invalid
        assert "at least one" in feedback.lower()
        assert style["display"] == "block"

    def test_invalid_transfer_function(self):
        _, _, invalid, feedback, style = handle_calculate(
            "not-a-tf", show_nyquist=True, show_bode=False, **_default_calculate_kwargs()
        )
        assert invalid
        assert feedback
        assert style["display"] == "block"

    def test_invalid_nyquist_omega_range(self):
        _, _, invalid, feedback, style = handle_calculate(
            "1/(s+1)",
            show_nyquist=True,
            show_bode=False,
            nyquist_omega_min=100,
            nyquist_omega_max=10,
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
            dark_mode=False,
        )
        assert invalid
        assert "nyquist frequency sweep" in feedback.lower()
        assert style["display"] == "block"

    def test_bode_mag_limits_applied(self):
        kwargs = {
            **_default_calculate_kwargs(),
            "bode_mag_min": -20,
            "bode_mag_max": 0,
        }
        _, bode_fig, invalid, _, _ = handle_calculate(
            "1/(s+1)",
            show_nyquist=False,
            show_bode=True,
            **kwargs,
        )
        assert not invalid
        assert bode_fig.layout.yaxis.range == (-20, 0)
        assert bode_fig.layout.yaxis.autorange is False

    def test_bode_partial_mag_range_invalid(self):
        kwargs = {**_default_calculate_kwargs(), "bode_mag_min": -20}
        _, _, invalid, feedback, style = handle_calculate(
            "1/(s+1)",
            show_nyquist=False,
            show_bode=True,
            **kwargs,
        )
        assert invalid
        assert "bode magnitude view" in feedback.lower()
        assert style["display"] == "block"

    def test_invalid_bode_freq_range(self):
        _, _, invalid, feedback, style = handle_calculate(
            "1/(s+1)",
            show_nyquist=False,
            show_bode=True,
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
            bode_freq_min=10,
            bode_freq_max=0.1,
            bode_mag_min=None,
            bode_mag_max=None,
            bode_phase_min=None,
            bode_phase_max=None,
            dark_mode=False,
        )
        assert invalid
        assert "bode frequency view" in feedback.lower()
        assert style["display"] == "block"


class TestCalcStateRefresh:
    """Tests for calc-store refresh helpers."""

    def test_run_calc_from_state_theme_toggle(self):
        calc_state = _build_calc_state(
            "1/(s+1)",
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
            False,
        )
        _, bode_fig, invalid, _, _ = _run_calc_from_state(
            calc_state, theme_data={"dark": True}
        )
        assert not invalid
        assert bode_fig == empty_fig(True)

        nyquist_fig, _, invalid, _, _ = _run_calc_from_state(
            calc_state, theme_data={"dark": True}
        )
        assert not invalid
        bgcolor = nyquist_fig.layout.template.layout.paper_bgcolor
        assert bgcolor in ("#2a2a3e", "rgb(42, 42, 62)")

    def test_run_calc_from_state_nyquist_toggles(self):
        calc_state = _build_calc_state(
            "1/(s+1)",
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
            False,
        )
        nyquist_fig, _, invalid, _, _ = _run_calc_from_state(
            calc_state, unit_circle=False, critical_point=False
        )
        assert not invalid
        trace_names = {trace.name for trace in nyquist_fig.data}
        assert "Unit circle" not in trace_names
        assert "Critical point (-1, 0)" not in trace_names
