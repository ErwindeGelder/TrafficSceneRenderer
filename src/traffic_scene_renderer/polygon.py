"""Plotting filled polygons like matplotlib, but provide additional option of having fixed color.

Author(s): Erwin de Gelder
"""

from typing import Any, Tuple

import numpy as np
from matplotlib import patches
from matplotlib.axes import Axes


class Polygon:
    """The polygon that is filled with the specified color.

    Attributes:
        xdata (np.ndarray): The x-coordinates of the vertices the polygon.
        ydata (np.ndarray): The y-coordinates of the vertices the polygon.
        patch (patches.Patch): Matplotlib's patch object that is used for plotting the polygon.
        fixed_color (bool): Whether or not the color is fixed.
    """

    def __init__(
        self,
        axes: Axes,
        xdata: np.ndarray,
        ydata: np.ndarray,
        *,
        fixed_color: bool = False,
        **kwargs: Any,  # noqa: ANN401  # Allow Any
    ) -> None:
        """Create a polygon object with the possibility to fix its color.

        Here, fixing a color means that `set_color`, `set_facecolor`, and `set_edgecolor` will have
        no effect.

        :param axes: The axes object that is used to draw the polygon.
        :param xdata: The x-coordinates of the polygon.
        :param ydata: The y-coordinates of the polygon.
        :fixed_color: Whether or not the color should be fixed (default=False).
        :kwargs: Any additional arguments that will be passed to matplotlib's polygon functionality.
        """
        self.xdata = xdata
        self.ydata = ydata
        self.patch = patches.Polygon(np.array([xdata, ydata]).T, **kwargs)
        axes.add_patch(self.patch)
        self.fixed_color = fixed_color

    def get_xdata(self) -> np.ndarray:
        """Get the x-coordinates of the vertices of the polygon.

        :return: Numpy array with the x-coordinates of the vertices of the polygon.
        """
        return self.xdata

    def get_ydata(self) -> np.ndarray:
        """Get the y-coordinates of the vertices of the polygon.

        :return: Numpy array with the y-coordinates of the vertices of the polygon.
        """
        return self.ydata

    def get_xy(self) -> np.ndarray:
        """Get the (x,y)-coordinates of the vertices of the polygon.

        :return: Numpy array (N-by-2) with the (x,y)-coordinates of the vertices of the polygon.
        """
        return np.array([self.xdata, self.ydata]).T

    def set_xdata(self, xdata: np.ndarray) -> None:
        """Set the x-coordinates of the vertices of the polygon.

        :param xdata: Numpy array with the x-coordinates of the vertices of the polygon.
        """
        self.xdata = xdata
        self.set_xy(np.array([self.xdata, self.ydata]).T)

    def set_ydata(self, ydata: np.ndarray) -> None:
        """Set the y-coordinates of the vertices of the polygon.

        :param ydata: Numpy array with the y-coordinates of the vertices of the polygon.
        """
        self.ydata = ydata
        self.set_xy(np.array([self.xdata, self.ydata]).T)

    def set_xy(self, xydata: np.ndarray) -> None:
        """Set the (x,y)-coordinates of the vertices of the polygon.

        :param xydata: Numpy array (N-by-2) with the (x,y)-coordinates of the vertices of the
                       polygon.
        """
        self.xdata = xydata[:, 0]
        self.ydata = xydata[:, 1]
        self.patch.set_xy(xydata)

    def set_color(self, color: Tuple[float, float, float]) -> None:
        """Set the color of the polygon.

        If the polygon has a fixed color, nothing is done.

        :param color: The color of the polygon.
        """
        if not self.fixed_color:
            self.patch.set_color(color)

    def set_facecolor(self, color: Tuple[float, float, float]) -> None:
        """Set the face color of the polygon.

        If the polygon has a fixed color, nothing is done.

        :param color: The face color of the polygon.
        :param force: Set to True if color must be changed, even if it is fixed.
        """
        if not self.fixed_color:
            self.patch.set_facecolor(color)

    def set_facecolor_forced(self, color: Tuple[float, float, float]) -> None:
        """Set the face color of the polygon, regardless of whether the color is fixed.

        :param color: The face color of the polygon.
        """
        self.patch.set_facecolor(color)

    def set_edgecolor(self, color: Tuple[float, float, float]) -> None:
        """Set the edge color of the polygon.

        If the polygon has a fixed color, nothing is done.

        :param color: The edge color of the polygon.
        """
        if not self.fixed_color:
            self.patch.set_edgecolor(color)

    def remove(self) -> None:
        """Remove the patch."""
        self.patch.remove()
