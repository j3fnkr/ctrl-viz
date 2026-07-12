"""
Bode plot utilities for control systems visualization.

This module provides functions for creating Bode plots (magnitude and phase)
of transfer functions using the python-control library.
"""

import numpy as np
import matplotlib.pyplot as plt

from ctrl_viz.frequency import compute_frequency_response


def bode_plot(
        system,
        omega=None,
        dB=True,
        deg=True,
        Hz=False,
        title=None,
        figsize=(10, 8),
        grid=True,
        labelsize=12,
        ticksize=10,
        freq_limits=None,
        mag_limits=None,
        phase_limits=None,
):
    """
    Create a Bode plot (magnitude and phase) for a given transfer function.

    Parameters
    ----------
    system :    control.TransferFunction or control. StateSpace
        The system to plot.
    omega :  array_like, optional
        Frequency range in rad/s. If None, automatically determined.
    dB : bool, optional
        If True, plot magnitude in decibels. Default is True.
    deg : bool, optional
        If True, plot phase in degrees.   Default is True.
    Hz : bool, optional
        If True, plot frequency in Hz instead of rad/s. Default is False.
    title : str, optional
        Title for the plot. Default is "Bode Plot".
    figsize : tuple, optional
        Figure size. Default is (10, 8).
    grid : bool, optional
        If True, show grid. Default is True.
    labelsize : int, optional
        Font size for axis labels.  Default is 12.
    ticksize : int, optional
        Font size for tick labels (numbers on axes). Default is 10.
    freq_limits : tuple, optional
        Frequency axis limits as (min, max). If None, auto-scaled.
    mag_limits : tuple, optional
        Magnitude axis limits as (min, max). If None, auto-scaled.
    phase_limits : tuple, optional
        Phase axis limits as (min, max). If None, auto-scaled.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    axes : tuple of matplotlib.axes.Axes
        Tuple containing (mag_ax, phase_ax).
    """
    mag, phase_unwrapped, omega_out = compute_frequency_response(system, omega)

    # Convert magnitude to dB if requested
    if dB:
        mag_plot = 20 * np.log10(np.abs(mag))
        mag_label = "Magnitude (dB)"
    else:
        mag_plot = np.abs(mag)
        mag_label = "Magnitude"

    # Convert phase to degrees if requested
    if deg:
        phase_plot = np.rad2deg(phase_unwrapped)
        phase_label = "Phase (deg)"
    else:
        phase_plot = phase_unwrapped
        phase_label = "Phase (rad)"

    # Convert frequency to Hz if requested
    if Hz:
        freq_plot = omega_out / (2 * np.pi)
        freq_label = "Frequency (Hz)"
    else:
        freq_plot = omega_out
        freq_label = "Frequency (rad/s)"

    # Create figure with two subplots
    fig, (mag_ax, phase_ax) = plt.subplots(2, 1, figsize=figsize, sharex=True)

    # Plot magnitude
    mag_ax.semilogx(freq_plot, mag_plot.flatten())
    mag_ax.set_ylabel(mag_label, fontsize=labelsize)
    mag_ax.set_title(title or "Bode Plot")
    mag_ax.tick_params(axis='both', which='major', labelsize=ticksize)
    if grid:
        mag_ax.grid(True, which="both", linestyle="-", alpha=0.7)

    # Set magnitude limits if specified
    if mag_limits is not None:
        mag_ax.set_ylim(mag_limits)

    # Plot phase (in red)
    phase_ax.semilogx(freq_plot, phase_plot.flatten(), color='red')
    phase_ax.set_xlabel(freq_label, fontsize=labelsize)
    phase_ax.set_ylabel(phase_label, fontsize=labelsize)
    phase_ax.tick_params(axis='both', which='major', labelsize=ticksize)
    if grid:
        phase_ax.grid(True, which="both", linestyle="-", alpha=0.7)

    # Set frequency limits if specified (applies to both since sharex=True)
    if freq_limits is not None:
        phase_ax.set_xlim(freq_limits)

    # Set phase limits if specified
    if phase_limits is not None:
        phase_ax.set_ylim(phase_limits)

    plt.tight_layout()

    return fig, (mag_ax, phase_ax)


def bode_magnitude(
    system, omega=None, dB=True, Hz=False, title=None, figsize=(10, 4), grid=True
):
    """
    Create a Bode magnitude plot for a given transfer function.

    Parameters
    ----------
    system : control.TransferFunction or control.StateSpace
        The system to plot.
    omega : array_like, optional
        Frequency range in rad/s. If None, automatically determined.
    dB : bool, optional
        If True, plot magnitude in decibels. Default is True.
    Hz : bool, optional
        If True, plot frequency in Hz instead of rad/s. Default is False.
    title : str, optional
        Title for the plot. Default is "Bode Magnitude Plot".
    figsize : tuple, optional
        Figure size. Default is (10, 4).
    grid : bool, optional
        If True, show grid. Default is True.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    ax : matplotlib.axes.Axes
        The axes object.
    """
    mag, _phase, omega_out = compute_frequency_response(system, omega)

    # Convert magnitude to dB if requested
    if dB:
        mag_plot = 20 * np.log10(np.abs(mag))
        mag_label = "Magnitude (dB)"
    else:
        mag_plot = np.abs(mag)
        mag_label = "Magnitude"

    # Convert frequency to Hz if requested
    if Hz:
        freq_plot = omega_out / (2 * np.pi)
        freq_label = "Frequency (Hz)"
    else:
        freq_plot = omega_out
        freq_label = "Frequency (rad/s)"

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot magnitude
    ax.semilogx(freq_plot, mag_plot.flatten())
    ax.set_xlabel(freq_label)
    ax.set_ylabel(mag_label)
    ax.set_title(title or "Bode Magnitude Plot")
    if grid:
        ax.grid(True, which="both", linestyle="-", alpha=0.7)

    plt.tight_layout()

    return fig, ax


def bode_phase(
    system, omega=None, deg=True, Hz=False, title=None, figsize=(10, 4), grid=True
):
    """
    Create a Bode phase plot for a given transfer function.

    Parameters
    ----------
    system : control.TransferFunction or control.StateSpace
        The system to plot.
    omega : array_like, optional
        Frequency range in rad/s. If None, automatically determined.
    deg : bool, optional
        If True, plot phase in degrees. Default is True.
    Hz : bool, optional
        If True, plot frequency in Hz instead of rad/s. Default is False.
    title : str, optional
        Title for the plot. Default is "Bode Phase Plot".
    figsize : tuple, optional
        Figure size. Default is (10, 4).
    grid : bool, optional
        If True, show grid. Default is True.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    ax : matplotlib.axes.Axes
        The axes object.
    """
    _mag, phase, omega_out = compute_frequency_response(
        system, omega, unwrap_phase=False
    )

    # Convert phase to degrees if requested
    if deg:
        phase_plot = np.rad2deg(phase)
        phase_label = "Phase (deg)"
    else:
        phase_plot = phase
        phase_label = "Phase (rad)"

    # Convert frequency to Hz if requested
    if Hz:
        freq_plot = omega_out / (2 * np.pi)
        freq_label = "Frequency (Hz)"
    else:
        freq_plot = omega_out
        freq_label = "Frequency (rad/s)"

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot phase
    ax.semilogx(freq_plot, phase_plot.flatten())
    ax.set_xlabel(freq_label)
    ax.set_ylabel(phase_label)
    ax.set_title(title or "Bode Phase Plot")
    if grid:
        ax.grid(True, which="both", linestyle="-", alpha=0.7)

    plt.tight_layout()

    return fig, ax
