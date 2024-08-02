"""Scripts for testing connection.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest
from matplotlib.axes import Axes

from traffic_scene_renderer import (
    Connection,
    Crossing,
    InvalidConnectionError,
    Vertex,
    Way,
    WayOptions,
)

from .test_static_objects import save_fig
from .test_way import plot_way

mpl.use("Agg")


def plot_connection(axes: Axes, *connections: Connection) -> None:
    for connection in connections:
        connection.process()
        if connection.crossing is not None:
            connection.crossing.plot(axes)
    ways = set()
    for connection in connections:
        for way in (connection.way1, connection.way2):
            if way not in ways:
                way.process()
                plot_way(axes, way)
                ways.add(way)


def test_simple_connection() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 5)
    vertices = [
        Vertex(0, -10, 0),
        Vertex(1, -5, 0),
        Vertex(2, 0, 0),
        Vertex(3, 5, 0),
        Vertex(4, 10, 0),
    ]
    way1 = Way(vertices[:3], WayOptions(side_color=(1, 0, 0), line_color=(1, 0, 0)))
    way2 = Way(vertices[2:], WayOptions(side_color=(0, 0, 1), line_color=(0, 0, 1)))
    connection = Connection(0, way1, way2)
    plot_connection(axes, connection)
    save_fig(fig, axes, Path("connection") / "simple_connection.png", 10)


def test_lane_addition() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-8, 8)
    vertices = [
        Vertex(0, -10, 0),
        Vertex(1, -5, 0),
        Vertex(2, 0, 0),
        Vertex(3, 5, -0.7),
        Vertex(4, 10, -1.4),
    ]
    way1 = Way(vertices[2::-1], WayOptions(side_color=(1, 0, 0), line_color=(1, 0, 0)))
    way2 = Way(vertices[:1:-1], WayOptions(side_color=(0, 0, 1), line_color=(0, 0, 1), nlanes=3))
    connection = Connection(0, way2, way1)
    plot_connection(axes, connection)
    save_fig(fig, axes, Path("connection") / "lane_addition.png", 10)


def test_lane_merge() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-8, 8)
    vertices = [
        Vertex(0, -10, 0),
        Vertex(1, -5, 0),
        Vertex(2, 0, 0),
        Vertex(3, 5, 0.7),
        Vertex(4, 10, 1.4),
    ]
    way1 = Way(vertices[2::-1], WayOptions(side_color=(1, 0, 0), line_color=(1, 0, 0)))
    way2 = Way(
        vertices[2:],
        WayOptions(
            side_color=(0, 0, 1),
            line_color=(0, 0, 1),
            nlanes=3,
            turnlanes="left|none|none",
            marker_border_color=(0, 0, 0.5),
        ),
    )
    connection = Connection(0, way1, way2)
    plot_connection(axes, connection)
    way2.plot_markers(axes)
    save_fig(fig, axes, Path("connection") / "lane_merge.png", 10)


def test_connection_as_crossing() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 10)
    vertices = [Vertex(0, -10, 0), Vertex(1, 0, 0), Vertex(2, 2, 12)]
    way1 = Way([vertices[0], vertices[1]], WayOptions(side_color=(1, 0, 0), line_color=(1, 0, 0)))
    way2 = Way([vertices[2], vertices[1]], WayOptions(side_color=(0, 0, 1), line_color=(0, 0, 1)))
    connection = Connection(0, way1, way2)
    plot_connection(axes, connection)
    save_fig(fig, axes, Path("connection") / "connection_as_crossing.png", 10)


def test_invalid_connection_error() -> None:
    way1 = Way([Vertex(0, -10, 0), Vertex(1, 0, 0)])
    way2 = Way([Vertex(2, -10, 10), Vertex(3, 0, 10)])
    try:
        Connection(0, way1, way2)
    except InvalidConnectionError:
        pass
    else:
        pytest.fail("InvalidConnectionError should have been raised.")


def test_check_crossing_reprocessing() -> None:
    vertices = [
        Vertex(0, -20, 0),
        Vertex(1, -10, 0),
        Vertex(2, -10, 10),
        Vertex(3, 0, 0),
        Vertex(4, 10, 0),
        Vertex(5, 10, 10),
        Vertex(6, 20, 0),
    ]
    ways = [
        Way([vertices[0], vertices[1]]),
        Way([vertices[1], vertices[2]]),
        Way([vertices[1], vertices[3]]),
        Way([vertices[3], vertices[4]]),
        Way([vertices[4], vertices[5]]),
        Way([vertices[4], vertices[6]]),
    ]
    crossing1 = Crossing(10, vertices[1], ways[:3])
    crossing2 = Crossing(20, vertices[4], ways[3:])
    connection = Connection(0, ways[2], ways[3])
    assert connection.compute_distance_to_next_vertex()[1] == [crossing1.idx, crossing2.idx]
