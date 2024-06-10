"""Scripts for testing bus.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from traffic_scene_renderer import Bus, BusOptions

from .test_static_objects import save_fig

mpl.use("Agg")


def test_bus_creation() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-4, 4)
    Bus(axes, BusOptions(color2=(0.8, 0.8, 1)))
    save_fig(fig, axes, Path("bus") / "standard_bus.png", 2)


def test_bus_different_colors() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-26, 26)
    axes.set_ylim(-4, 4)
    bus = Bus(axes, BusOptions(color=(0.5, 0.5, 0.5)))
    bus.change_pos(-24, 0)
    bus = Bus(axes, BusOptions(color=(0.8, 0, 0)))
    bus.change_pos(-20, 0)
    bus = Bus(axes, BusOptions(color=(0.8, 0.4, 0)))
    bus.change_pos(-16, 0)
    bus = Bus(axes, BusOptions(color=(0.8, 0.8, 0)))
    bus.change_pos(-12, 0)
    bus = Bus(axes, BusOptions(color=(0.4, 0.8, 0)))
    bus.change_pos(-8, 0)
    bus = Bus(axes, BusOptions(color=(0, 0.8, 0)))
    bus.change_pos(-4, 0)
    Bus(axes, BusOptions(color=(0, 0.8, 0.4)))
    bus = Bus(axes, BusOptions(color=(0, 0.8, 0.8)))
    bus.change_pos(4, 0)
    bus = Bus(axes, BusOptions(color=(0, 0.4, 0.8)))
    bus.change_pos(8, 0)
    bus = Bus(axes, BusOptions(color=(0, 0, 0.8)))
    bus.change_pos(12, 0)
    bus = Bus(axes, BusOptions(color=(0.4, 0, 0.8)))
    bus.change_pos(16, 0)
    bus = Bus(axes, BusOptions(color=(0.8, 0, 0.8)))
    bus.change_pos(20, 0)
    bus = Bus(axes, BusOptions(color=(0.8, 0, 0.4)))
    bus.change_pos(24, 0)
    save_fig(fig, axes, Path("bus") / "different_colors.png", 26)


def test_bus_change_color_and_pos() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(0, 8)
    axes.set_ylim(0, 4)
    bus = Bus(axes)
    bus.change_color(face_color=(1, 0, 0))
    bus.change_pos(4, 2, np.pi / 2)
    save_fig(fig, axes, Path("bus") / "recolored_bus.png", 4)
