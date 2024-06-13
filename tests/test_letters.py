"""Scripts for testing letters.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest

from traffic_scene_renderer import Letters, LettersOptions
from traffic_scene_renderer.utilities import hsl2rgb

from .test_static_objects import save_fig

mpl.use("Agg")


def test_all_letters() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-8, 8)
    axes.set_ylim(-0.8, 0.8)
    Letters(axes, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", LettersOptions(length=1, width=15))
    save_fig(fig, axes, Path("letters") / "alfabet.png", 16)


def test_not_implemented_letter() -> None:
    fig, axes = plt.subplots()
    try:
        Letters(axes, "#")
    except NotImplementedError:
        pass
    else:
        pytest.fail("NotImplementedError should have been raised.")


def test_colored_alfabet() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-8, 8)
    axes.set_ylim(-0.8, 0.8)
    letters = Letters(axes, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", LettersOptions(length=1, width=15))
    letters.change_color(face_color=(1, 0.5, 0.5), edge_color=(0.8, 0, 0))
    save_fig(fig, axes, Path("letters") / "colored.png", 16)


def test_move_letters() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-3.5, 3.5)
    axes.set_ylim(-3.5, 3.5)
    alfabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(13):
        letters = Letters(
            axes,
            alfabet[2 * i : 2 * (i + 1)],
            LettersOptions(
                length=1,
                width=1,
                face_color=hsl2rgb(i / 13, 1, 0.6),
                edge_color=hsl2rgb(i / 13, 1, 0.3),
            ),
        )
        letters.change_pos(
            2.7 * np.sin(2 * np.pi * i / 13), 2.7 * np.cos(2 * np.pi * i / 13), 2 * np.pi * i / 13
        )
    save_fig(fig, axes, Path("letters") / "moved.png", 12)
