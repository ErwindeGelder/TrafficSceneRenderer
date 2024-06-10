"""Scripts for testing crossing.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from traffic_scene_renderer import Crossing, CrossingOptions, Vertex, Way, WayOptions
from traffic_scene_renderer.crossing import correct_angle

from .test_static_objects import save_fig
from .test_way import plot_way

mpl.use("Agg")


def plot_crossing(axes: Axes, *crossings: Crossing) -> None:
    ways_plotted = set()
    for crossing in crossings:
        crossing.process()
        crossing.plot(axes)
    for crossing in crossings:
        for way in crossing.ways:
            if way in ways_plotted:
                continue
            ways_plotted.add(way)
            way.process()
            plot_way(axes, way)


def crossing_creation(*, have_vertex_0_first: bool) -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-10, 10)
    vertices = [
        Vertex(*ixy) for ixy in ((0, 0, 0), (1, -10, 0), (2, 0, 10), (3, 10, 0), (4, 0, -10))
    ]
    if have_vertex_0_first:
        ways = [
            Way([vertices[0], vertices[i]], WayOptions(line_color=(0, 0, 0)))
            for i in range(1, len(vertices))
        ]
    else:
        ways = [
            Way([vertices[i], vertices[0]], WayOptions(line_color=(0, 0, 0)))
            for i in range(1, len(vertices))
        ]
    crossing = Crossing(0, vertices[0], ways)
    plot_crossing(axes, crossing)
    save_fig(
        fig, axes, Path("crossing") / f"simple_crossing{1 if have_vertex_0_first else 2}.png", 10
    )


def test_crossing_creation() -> None:
    crossing_creation(have_vertex_0_first=True)


def test_crossing_creation_reversed() -> None:
    crossing_creation(have_vertex_0_first=False)


def crossing_large_angle(filename: str, *, roundabout: bool) -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-10, 10)
    vertices = [Vertex(*ixy) for ixy in ((0, 0, 0), (1, -10, 1), (2, 0, 10), (3, 10, 1))]
    ways = [
        Way(way_vertices, WayOptions(line_color=(0, 0, 0)))
        for way_vertices in (
            [vertices[0], vertices[1]],
            [vertices[0], vertices[2]],
            [vertices[3], vertices[0]],
        )
    ]
    crossing = Crossing(0, vertices[0], ways, CrossingOptions(roundabout=roundabout))
    plot_crossing(axes, crossing)
    save_fig(fig, axes, Path("crossing") / filename, 10)


def test_crossing_large_angle() -> None:
    crossing_large_angle("crossing_large_angle.png", roundabout=False)


def test_roundabout() -> None:
    crossing_large_angle("roundabout.png", roundabout=True)


def create_zebra(*, with_blocks: bool) -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-7, 7)
    vertices = [
        Vertex(*ixy) for ixy in ((0, 0, 0), (1, -10, 0), (2, 0, 10), (3, 10, 0), (4, 0, -10))
    ]
    ways = [
        Way([vertices[0], vertices[1]], WayOptions(line_color=(0, 0, 0))),
        Way([vertices[0], vertices[2]], WayOptions(side_color=(0, 0, 0), highway="footway")),
        Way([vertices[0], vertices[3]], WayOptions(line_color=(0, 0, 0))),
        Way([vertices[0], vertices[4]], WayOptions(side_color=(0, 0, 0), highway="footway")),
    ]
    ways[1].options.highway = "footway"
    ways[3].options.highway = "footway"
    crossing = Crossing(0, vertices[0], ways, CrossingOptions(zebra_square_markings=with_blocks))
    plot_crossing(axes, crossing)
    save_fig(
        fig,
        axes,
        Path("crossing") / f"zebra_crossing{'_with_blocks' if with_blocks else ''}.png",
        10,
    )


def test_zebra() -> None:
    create_zebra(with_blocks=False)


def test_zebra_with_blocks() -> None:
    create_zebra(with_blocks=True)


def test_footway_different_radii() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-7, 7)
    vertices = [
        Vertex(*ixy)
        for ixy in (
            (0, -10, 0),
            (1, -3, 0),
            (2, -3, 10),
            (3, -3, -10),
            (4, 4, 1),
            (5, 2, 10),
            (6, 2, -10),
            (7, 12, 8),
            (8, 12, -8),
        )
    ]
    ways = [
        Way([vertices[i], vertices[j]], WayOptions(side_color=(1, 0, 0), highway="footway"))
        for i, j in ((0, 1), (1, 2), (1, 3), (1, 4), (4, 5), (4, 6), (4, 7), (4, 8))
    ]
    crossing1 = Crossing(0, vertices[1], ways[:4])
    crossing2 = Crossing(1, vertices[4], ways[3:], CrossingOptions(radius=1))
    plot_crossing(axes, crossing1, crossing2)
    save_fig(fig, axes, Path("crossing") / "footways.png", 10)


def test_warning_zebra_no_2_footways() -> None:
    fig, axes = plt.subplots()
    vertices = [Vertex(0, 0, 0), Vertex(1, 10, 0), Vertex(2, 0, 10), Vertex(3, 0, -10)]
    ways = [Way(vertices[:2]), Way(vertices[1:3]), Way(vertices[2:])]
    crossing = Crossing(0, vertices[0], ways)
    crossing.parms.zebra = True
    with pytest.warns(UserWarning):
        crossing.plot_zebra(axes)
    plt.close(fig)


def test_warning_zebra_no_2_roadways() -> None:
    fig, axes = plt.subplots()
    vertices = [Vertex(0, 0, 0), Vertex(1, 10, 0), Vertex(2, 0, 10), Vertex(3, 0, -10)]
    ways = [
        Way(vertices[:2], WayOptions(highway="footway")),
        Way(vertices[1:3], WayOptions(highway="footway")),
        Way(vertices[2:]),
    ]
    crossing = Crossing(0, vertices[0], ways)
    crossing.parms.zebra = True
    with pytest.warns(UserWarning):
        crossing.plot_zebra(axes)
    plt.close(fig)


def test_correct_angle() -> None:
    assert correct_angle(0, 1.5 * np.pi, big_angle=False) == pytest.approx(2 * np.pi)
    assert correct_angle(1.5 * np.pi, 0, big_angle=False) == pytest.approx(-0.5 * np.pi)
    assert correct_angle(0, 0.5 * np.pi, big_angle=True) == pytest.approx(2 * np.pi)
    assert correct_angle(0.5 * np.pi, 0, big_angle=True) == pytest.approx(-1.5 * np.pi)
