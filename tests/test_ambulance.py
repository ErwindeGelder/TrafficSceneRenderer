"""Scripts for testing ambulance.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from traffic_scene_renderer import Ambulance, PathFollower

from .test_static_objects import save_fig

mpl.use("Agg")


def test_ambulance_creation() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-4, 4)
    Ambulance(axes)
    save_fig(fig, axes, Path("ambulance") / "standard_ambulance.png", 5)


def test_ambulance_with_path_follower() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 8)
    axes.set_ylim(-4, 14)
    x_path, y_path = np.array([0, 0, 1, 3, 23]), np.array([0, 2, 5, 7, 27])
    path_follower = PathFollower(x_path, y_path)
    ambulance = Ambulance(axes, path_follower=path_follower)
    for _ in range(50):
        ambulance.move_vehicle(0.2)
    axes.plot(x_path, y_path, color="black", linewidth=0.5)
    save_fig(fig, axes, Path("ambulance") / "ambulance_with_path_follower.png", 8)
