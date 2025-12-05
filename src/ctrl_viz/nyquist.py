"""
Nyquist plot utilities for control systems visualization.

This module provides functions for creating Nyquist plots
of transfer functions using the python-control library.
"""

import numpy as np
import matplotlib.pyplot as plt
import control


def nyquist_plot(system, omega=None, title=None, figsize=(8, 8),
                 grid=True, unit_circle=True, arrows=True):
    """
    Create a Nyquist plot for a given transfer function.

    Parameters
    ----------
    system : control.TransferFunction or control.StateSpace
        The system to plot.
    omega : array_like, optional
        Frequency range in rad/s. If None, automatically determined.
    title : str, optional
        Title for the plot. Default is "Nyquist Plot".
    figsize : tuple, optional
        Figure size. Default is (8, 8).
    grid : bool, optional
        If True, show grid. Default is True.
    unit_circle : bool, optional
        If True, draw the unit circle. Default is True.
    arrows : bool, optional
        If True, show direction arrows on the plot. Default is True.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    ax : matplotlib.axes.Axes
        The axes object.
    """
    if omega is None:
        omega = np.logspace(-2, 2, 1000)
    
    # Compute frequency response
    mag, phase, omega_out = control.frequency_response(system, omega)
    
    # Convert to complex representation
    response = mag * np.exp(1j * phase)
    real_part = np.real(response).flatten()
    imag_part = np.imag(response).flatten()
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot Nyquist curve for positive frequencies
    ax.plot(real_part, imag_part, 'b-', linewidth=1.5, label='ω > 0')
    
    # Plot mirror image for negative frequencies
    ax.plot(real_part, -imag_part, 'b--', linewidth=1.5, alpha=0.7, label='ω < 0')
    
    # Add arrows to show direction if requested
    if arrows:
        # Add arrow for positive frequencies
        mid_idx = len(real_part) // 2
        if mid_idx > 0 and mid_idx < len(real_part) - 1:
            dx = real_part[mid_idx + 1] - real_part[mid_idx]
            dy = imag_part[mid_idx + 1] - imag_part[mid_idx]
            ax.annotate('', xy=(real_part[mid_idx] + dx, imag_part[mid_idx] + dy),
                       xytext=(real_part[mid_idx], imag_part[mid_idx]),
                       arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    
    # Draw unit circle if requested
    if unit_circle:
        theta = np.linspace(0, 2 * np.pi, 100)
        ax.plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.3, label='Unit circle')
    
    # Mark the critical point (-1, 0)
    ax.plot(-1, 0, 'rx', markersize=10, markeredgewidth=2, label='Critical point (-1, 0)')
    
    # Set labels and title
    ax.set_xlabel('Real')
    ax.set_ylabel('Imaginary')
    ax.set_title(title or "Nyquist Plot")
    
    # Make the plot aspect ratio equal
    ax.set_aspect('equal')
    
    # Add grid if requested
    if grid:
        ax.grid(True, linestyle='-', alpha=0.7)
    
    # Add legend
    ax.legend(loc='best')
    
    # Add axis lines
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    
    plt.tight_layout()
    
    return fig, ax
