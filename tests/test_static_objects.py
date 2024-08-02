"""Scripts for testing static_objects.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from traffic_scene_renderer import (
    Building,
    MaxSpeed,
    MaxSpeedOptions,
    Stripes,
    StripesOptions,
    TurnArrow,
    TurnArrowOptions,
)

mpl.use("Agg")


def save_fig(figure: Figure, axes: Axes, filename: Path, fwidth: float = 10) -> None:
    filename = Path("tests") / "created_images" / filename
    Path.unlink(filename, missing_ok=True)
    Path.mkdir(filename.parent, parents=True, exist_ok=True)
    xlim = axes.get_xlim()
    ylim = axes.get_ylim()
    figure.set_size_inches((fwidth, fwidth * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])))
    axes.set_axis_off()
    figure.savefig(filename, bbox_inches="tight", pad_inches=0.0, facecolor=axes.get_facecolor())
    plt.close(figure)


def test_max_speed_creation() -> None:
    fig, axes = plt.subplots()
    MaxSpeed(axes, "50", MaxSpeedOptions(fontsize=50))
    save_fig(fig, axes, Path("static_objects") / "max_speed.png", 2)


def test_max_speed_different_radii() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-4.5, 4.5)
    axes.set_ylim(-2, 2)
    MaxSpeed(axes, "50", MaxSpeedOptions(fontsize=30, outer_radius=1.2, inner_radius=0.8))
    max_speed2 = MaxSpeed(axes, "50", MaxSpeedOptions(fontsize=45, outer_radius=1.5))
    max_speed2.change_pos(-3, 0)
    max_speed3 = MaxSpeed(axes, "50", MaxSpeedOptions(fontsize=20, inner_radius=0.53))
    max_speed3.change_pos(3, 0)
    save_fig(fig, axes, Path("static_objects") / "max_speed_different_sizes.png", 6)


def test_creation_of_all_turn_arrows() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-0.5, 16.5)
    axes.set_ylim(-1.5, 4.5)
    for i, direction in enumerate(
        ("through", "left", "right", "leftright", "leftthrough", "throughright")
    ):
        turn_arrow = TurnArrow(
            axes, direction=direction, options=TurnArrowOptions(face_color=(1 - 0.1 * i, 0.8, 0.8))
        )
        turn_arrow.change_pos(i * 3, 0)
        turn_arrow = TurnArrow(
            axes, direction=direction, options=TurnArrowOptions(face_color=(0.8, 1 - 0.1 * i, 0.8))
        )
        turn_arrow.change_pos(i * 3, 3, np.pi)
    save_fig(fig, axes, Path("static_objects") / "turn_arrows.png", 10)


def test_building_creation() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-2, 2)
    Building(axes)
    save_fig(fig, axes, Path("static_objects") / "building.png", 2)


def test_stripes_creation() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-2, 2)
    Stripes(axes, options=StripesOptions(width=0.5, length=3.5, nstripes=20))
    save_fig(fig, axes, Path("static_objects") / "stripes.png", 3)


def test_stripes_change_colors() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-2, 2)
    stripes = Stripes(axes, options=StripesOptions(width=0.5, length=3.5))
    stripes.change_color(face_color=(0, 0, 0), edge_color=(1, 0, 0), face_color2=(1, 1, 0))
    save_fig(fig, axes, Path("static_objects") / "stripes_different_color.png", 3)


def test_stripes_rotate() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-2, 2)
    stripes = Stripes(axes, options=StripesOptions(width=0.5, length=3.5))
    stripes.change_pos(0, 0, np.pi / 2)
    save_fig(fig, axes, Path("static_objects") / "stripes_rotated.png", 3)
