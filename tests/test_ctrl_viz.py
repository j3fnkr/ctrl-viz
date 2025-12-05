"""
Tests for ctrl_viz package.
"""

import pytest
import numpy as np
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
import control

from ctrl_viz import bode_plot, bode_magnitude, bode_phase, nyquist_plot


@pytest.fixture
def simple_system():
    """Create a simple first-order transfer function for testing."""
    return control.TransferFunction([1], [1, 1])


@pytest.fixture
def second_order_system():
    """Create a second-order transfer function for testing."""
    return control.TransferFunction([1], [1, 0.5, 1])


class TestBodePlot:
    """Tests for bode_plot function."""

    def test_bode_plot_returns_figure_and_axes(self, simple_system):
        """Test that bode_plot returns a figure and axes."""
        fig, axes = bode_plot(simple_system)
        assert isinstance(fig, plt.Figure)
        assert len(axes) == 2
        plt.close(fig)

    def test_bode_plot_with_custom_omega(self, simple_system):
        """Test bode_plot with custom frequency range."""
        omega = np.logspace(-3, 3, 100)
        fig, axes = bode_plot(simple_system, omega=omega)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_bode_plot_with_title(self, simple_system):
        """Test bode_plot with custom title."""
        title = "Test Bode Plot"
        fig, axes = bode_plot(simple_system, title=title)
        assert axes[0].get_title() == title
        plt.close(fig)

    def test_bode_plot_linear_magnitude(self, simple_system):
        """Test bode_plot with linear magnitude scale."""
        fig, axes = bode_plot(simple_system, dB=False)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_bode_plot_radians_phase(self, simple_system):
        """Test bode_plot with radians phase."""
        fig, axes = bode_plot(simple_system, deg=False)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_bode_plot_hz_frequency(self, simple_system):
        """Test bode_plot with Hz frequency scale."""
        fig, axes = bode_plot(simple_system, Hz=True)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestBodeMagnitude:
    """Tests for bode_magnitude function."""

    def test_bode_magnitude_returns_figure_and_ax(self, simple_system):
        """Test that bode_magnitude returns a figure and axes."""
        fig, ax = bode_magnitude(simple_system)
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        plt.close(fig)

    def test_bode_magnitude_with_custom_title(self, simple_system):
        """Test bode_magnitude with custom title."""
        title = "Test Magnitude Plot"
        fig, ax = bode_magnitude(simple_system, title=title)
        assert ax.get_title() == title
        plt.close(fig)


class TestBodePhase:
    """Tests for bode_phase function."""

    def test_bode_phase_returns_figure_and_ax(self, simple_system):
        """Test that bode_phase returns a figure and axes."""
        fig, ax = bode_phase(simple_system)
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        plt.close(fig)

    def test_bode_phase_with_custom_title(self, simple_system):
        """Test bode_phase with custom title."""
        title = "Test Phase Plot"
        fig, ax = bode_phase(simple_system, title=title)
        assert ax.get_title() == title
        plt.close(fig)


class TestNyquistPlot:
    """Tests for nyquist_plot function."""

    def test_nyquist_plot_returns_figure_and_ax(self, simple_system):
        """Test that nyquist_plot returns a figure and axes."""
        fig, ax = nyquist_plot(simple_system)
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        plt.close(fig)

    def test_nyquist_plot_with_custom_omega(self, simple_system):
        """Test nyquist_plot with custom frequency range."""
        omega = np.logspace(-3, 3, 500)
        fig, ax = nyquist_plot(simple_system, omega=omega)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_nyquist_plot_with_title(self, simple_system):
        """Test nyquist_plot with custom title."""
        title = "Test Nyquist Plot"
        fig, ax = nyquist_plot(simple_system, title=title)
        assert ax.get_title() == title
        plt.close(fig)

    def test_nyquist_plot_without_unit_circle(self, simple_system):
        """Test nyquist_plot without unit circle."""
        fig, ax = nyquist_plot(simple_system, unit_circle=False)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_nyquist_plot_without_arrows(self, simple_system):
        """Test nyquist_plot without arrows."""
        fig, ax = nyquist_plot(simple_system, arrows=False)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestSecondOrderSystem:
    """Tests with second-order system."""

    def test_bode_plot_second_order(self, second_order_system):
        """Test bode_plot with second-order system."""
        fig, axes = bode_plot(second_order_system)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_nyquist_plot_second_order(self, second_order_system):
        """Test nyquist_plot with second-order system."""
        fig, ax = nyquist_plot(second_order_system)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestPackageImports:
    """Tests for package imports."""

    def test_package_version(self):
        """Test that package has version."""
        import ctrl_viz

        assert hasattr(ctrl_viz, "__version__")
        assert ctrl_viz.__version__ == "0.1.1"

    def test_all_exports(self):
        """Test that all expected functions are exported."""
        import ctrl_viz

        assert hasattr(ctrl_viz, "bode_plot")
        assert hasattr(ctrl_viz, "bode_magnitude")
        assert hasattr(ctrl_viz, "bode_phase")
        assert hasattr(ctrl_viz, "nyquist_plot")
