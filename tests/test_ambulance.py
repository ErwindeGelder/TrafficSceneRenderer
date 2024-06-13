"""Scripts for testing ambulance.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

from traffic_scene_renderer import Ambulance

from .test_static_objects import save_fig

mpl.use("Agg")


def test_ambulance_creation() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-4, 4)
    Ambulance(axes)
    save_fig(fig, axes, Path("ambulance") / "standard_ambulance.png", 5)
