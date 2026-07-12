# ctrl-viz

A Python library for visualizing control systems using Bode and Nyquist plots with the python-control library.

## Features

- **Bode Plots**: Create magnitude and phase plots of transfer functions
  - Full Bode plots (magnitude + phase)
  - Magnitude-only plots
  - Phase-only plots
  - Support for dB/linear magnitude and deg/rad phase
  - Frequency in rad/s or Hz

- **Nyquist Plots**: Visualize frequency response in the complex plane
  - Unit circle overlay
  - Critical point (-1, 0) marking
  - Direction arrows

## Installation

1. Clone the repository:
```bash
git clone https://github.com/j3f-me/ctrl-viz.git
cd ctrl-viz
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package in development mode:
```bash
pip install -e .
```

[optional] For development or when using the jupyter lab demo, install the package like this:
```bash
pip install -e ".[dev,lab]"
```

Or install directly:
```bash
pip install -e src/
```

## Quick Start

```python
import control
from ctrl_viz import bode_plot, nyquist_plot

# Create a transfer function (1 / (s^2 + 0.5 s + 1))
system = control.TransferFunction([1], [1, 0.5, 1])

# Create a Bode plot
fig, axes = bode_plot(system, title="My System")

# Create a Nyquist plot
fig, ax = nyquist_plot(system, title="Nyquist Diagram")
```

## Usage

### Bode Plots

```python
from ctrl_viz import bode_plot, bode_magnitude, bode_phase
import control
import numpy as np

# Create a transfer function
G = control.TransferFunction([1], [1, 1])

# Full Bode plot
fig, (mag_ax, phase_ax) = bode_plot(G)

# Magnitude only
fig, ax = bode_magnitude(G)

# Phase only
fig, ax = bode_phase(G)

# With custom options
omega = np.logspace(-3, 3, 1000)
fig, axes = bode_plot(G, omega=omega, dB=True, deg=True, Hz=False)
```

### Nyquist Plots

```python
from ctrl_viz import nyquist_plot
import control

# Create a transfer function
G = control.TransferFunction([1], [1, 0.5, 1])

# Basic Nyquist plot
fig, ax = nyquist_plot(G)

# With custom options
fig, ax = nyquist_plot(G, title="My Nyquist Plot", unit_circle=True)
```

## API Reference

### `bode_plot(system, omega=None, dB=True, deg=True, Hz=False, title=None, figsize=(10, 8), grid=True)`

Creates a complete Bode plot with magnitude and phase.

**Parameters:**
- `system`: Transfer function or state-space model
- `omega`: Frequency range in rad/s (auto if None)
- `dB`: Plot magnitude in decibels (default: True)
- `deg`: Plot phase in degrees (default: True)
- `Hz`: Use Hz instead of rad/s (default: False)
- `title`: Plot title
- `figsize`: Figure size tuple
- `grid`: Show grid (default: True)

**Returns:** `(fig, (mag_ax, phase_ax))`

### `bode_magnitude(system, omega=None, dB=True, Hz=False, title=None, figsize=(10, 4), grid=True)`

Creates a magnitude-only Bode plot.

### `bode_phase(system, omega=None, deg=True, Hz=False, title=None, figsize=(10, 4), grid=True)`

Creates a phase-only Bode plot.

### `nyquist_plot(system, omega=None, title=None, figsize=(8, 8), grid=True, unit_circle=True, arrows=True)`

Creates a Nyquist plot.

**Parameters:**
- `system`: Transfer function or state-space model
- `omega`: Frequency range in rad/s (auto if None)
- `title`: Plot title
- `figsize`: Figure size tuple
- `grid`: Show grid (default: True)
- `unit_circle`: Draw unit circle (default: True)
- `arrows`: Show direction arrows (default: True)

**Returns:** `(fig, ax)`

## Examples

See the [examples/demo.ipynb](examples/demo.ipynb) notebook for detailed usage examples.

## Web UI

Run an interactive local web app to plot transfer functions without writing a Python script:

```bash
pip install -e ".[web]"
python run_web.py
```

Then open **http://127.0.0.1:8050/** in your browser.

Enter a rational expression in `s`, for example `1/(s^2+0.5*s+1)`, choose Nyquist and/or Bode plots, and click **Calculate**. The input field validates syntax in real time; invalid expressions are highlighted in red with an error hint.

## Requirements

- Python 3.8+
- control
- scipy
- matplotlib
- pytest (for testing)

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## License

MIT License
