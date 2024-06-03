"""Scripts for testing polygon.py.

Author(s): Erwin de Gelder
"""

import matplotlib.pyplot as plt
import numpy as np

from traffic_scene_renderer.polygon import Polygon

XDATA = np.array([0, 0, 1, 1])
YDATA = np.array([0, 1, 1, 0])
_, AXES = plt.subplots()


def test_polygon_creation() -> None:
    Polygon(AXES, XDATA, YDATA, fixed_color=False)


def test_polygon_get_xy_data() -> None:
    polygon = Polygon(AXES, XDATA, YDATA, fixed_color=False)
    xdata = polygon.get_xdata()
    ydata = polygon.get_ydata()
    assert np.all(polygon.get_xy() == np.array([xdata, ydata]).T)


def test_polygon_set_xy_data() -> None:
    polygon1 = Polygon(AXES, XDATA, YDATA, fixed_color=False)
    polygon1.set_xdata(XDATA + 1)
    polygon1.set_ydata(YDATA + 1)
    polygon2 = Polygon(AXES, XDATA, YDATA, fixed_color=False)
    polygon2.set_xy(np.array([XDATA + 1, YDATA + 1]).T)
    assert np.all(polygon1.get_xy() == polygon2.get_xy())


def test_polygon_set_colors() -> None:
    # Check whether colors have changed
    my_colors = (0.1, 0.2, 0.3)
    polygon = Polygon(AXES, XDATA, YDATA, fixed_color=False)
    polygon.set_color(my_colors)
    assert polygon.patch.get_edgecolor()[:3] == my_colors
    assert polygon.patch.get_facecolor()[:3] == my_colors

    # Check whether only facecolor have changed
    polygon = Polygon(AXES, XDATA, YDATA, fixed_color=False)
    polygon.set_facecolor(my_colors)
    assert polygon.patch.get_edgecolor()[:3] != my_colors
    assert polygon.patch.get_facecolor()[:3] == my_colors

    # Check whether only edgecolor have changed
    polygon = Polygon(AXES, XDATA, YDATA, fixed_color=False)
    polygon.set_edgecolor(my_colors)
    assert polygon.patch.get_edgecolor()[:3] == my_colors
    assert polygon.patch.get_facecolor()[:3] != my_colors

    # Check whether none of the color have changed
    polygon = Polygon(AXES, XDATA, YDATA, fixed_color=True)
    polygon.set_color(my_colors)
    polygon.set_facecolor(my_colors)
    polygon.set_edgecolor(my_colors)
    assert polygon.patch.get_edgecolor()[:3] != my_colors
    assert polygon.patch.get_facecolor()[:3] != my_colors

    # Check whether only facecolor have changed
    polygon = Polygon(AXES, XDATA, YDATA, fixed_color=True)
    polygon.set_facecolor_forced(my_colors)
    assert polygon.patch.get_edgecolor()[:3] != my_colors
    assert polygon.patch.get_facecolor()[:3] == my_colors
