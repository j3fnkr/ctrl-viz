"""
ctrl_viz - Control Systems Visualization Library

A Python library for creating Bode and Nyquist plots using python-control.
"""

from ctrl_viz.bode import bode_plot, bode_magnitude, bode_phase
from ctrl_viz.nyquist import nyquist_plot

__version__ = "0.1.1"
__all__ = ["bode_plot", "bode_magnitude", "bode_phase", "nyquist_plot"]
