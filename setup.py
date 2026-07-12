from setuptools import setup, find_packages
import pathlib

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ctrl-viz",
    version="0.1.1",
    description="Utilities for visualizing transfer functions (Bode/Nyquist plots, etc.)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jan Fenker",
    author_email="coding@fenker.eu",
    url="https://github.com/j3f-me/ctrl-viz",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"ctrl_viz": ["web/assets/*"]},
    include_package_data=True,
    install_requires=[
        "control>=0.9.0",
        "scipy>=1.9.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"],  # local install: pip install ".[dev,demo]"
        "demo": ["jupyterlab>=3.0.0"],
        "web": [
            "dash>=2.14",
            "plotly>=5.18",
            "dash-bootstrap-components>=1.5",
            "gunicorn>=21.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering",
    ],
)
