"""
Shared frequency-response computation for ctrl-viz plotting.
"""

import numpy as np
import control


def compute_frequency_response(system, omega=None, unwrap_phase=True):
    """
    Compute magnitude, phase, and frequency for a control system.

    Parameters
    ----------
    system : control.TransferFunction or control.StateSpace
        The system to analyze.
    omega : array_like, optional
        Frequency range in rad/s. If None, uses logspace(-2, 2, 500).
    unwrap_phase : bool, optional
        If True, unwrap phase angles. Default is True.

    Returns
    -------
    mag : ndarray
        Magnitude response.
    phase : ndarray
        Phase response (radians).
    omega_out : ndarray
        Frequency points used.
    """
    if omega is None:
        omega = np.logspace(-2, 2, 500)

    mag, phase, omega_out = control.frequency_response(system, omega)

    if unwrap_phase:
        phase = np.unwrap(phase)

    return mag, phase, omega_out
