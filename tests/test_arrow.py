"""Scripts for testing arrow.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from traffic_scene_renderer import arrow

from .test_static_objects import save_fig

mpl.use("Agg")


def test_arrow() -> None:
    fig, axes = plt.subplots(1, 1)
    axes.set_xlim(-10, 10)
    axes.set_ylim(-10, 10)
    arrow(axes, [-8, -8], [-8, 8], color="r")  # Straight arrow
    arrow(axes, [-6, -6, -2, 8], [-8, 4, 8, 8], color="b")  # Arrow with 90 degrees corner
    arrow(axes, [-4, -4, 0, 0], [-8, -4, 2, 6], color="g")  # Arrow with s-bend
    theta = np.linspace(0, 3 * np.pi / 2, 50)
    arrow(axes, 5 + 4 * np.sin(theta), -4 + 4 * np.cos(theta), color="k")  # Random shape
    save_fig(fig, axes, Path("arrow") / "arrows.png")
