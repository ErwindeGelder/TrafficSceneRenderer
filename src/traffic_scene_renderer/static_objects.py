"""Constructing static objects.

Author(s): Erwin de Gelder
"""

from abc import ABC
from typing import Dict, Optional, Tuple, Union

import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon as PPolygon
from matplotlib.text import Text

from .options import Options
from .polygon import Polygon
from .utilities import rotate


class StaticObjectPosition(Options):
    """Parameters of a static object, containing the (x,y)-coordinates and the angle."""

    x_center: float = 0
    y_center: float = 0
    angle: float = 0


class StaticObject(ABC):
    """Abstract class for dealing with static objects.

    Attributes:
        axes (Axes): The axes object that is used to draw the sign.
        position (StaticObjectPosition): The (x,y)-coordinates of the center of the sign.
        fills (Tuple): A tuple containing the handles for the filled areas.
        plots (Tuple): A tuple containing the handles for the line plots.
        texts (Tuple): A tuple containing the handles for text objects.
    """

    axes: Axes
    fills: Tuple[Union[PPolygon, Polygon], ...]
    plots: Tuple[Line2D, ...]
    texts: Tuple[Text, ...]
    position: StaticObjectPosition

    def __init__(self, axes: Axes) -> None:
        """Creating a static object.

        :param axes: The axes on which the object is supposed to be drawn.
        """
        self.axes = axes
        self.fills = ()
        self.plots = ()
        self.texts = ()
        self.position = StaticObjectPosition()

    def change_pos(self, x_center: float, y_center: float, angle: float = 0) -> None:
        """Change the position of the static object.

        :param x_center: The new x-coordinate of the static object.
        :param y_center: The new y-coordinate of the static object.
        :param angle: The new angle of the static object.
        """
        for plot in self.plots:
            xdata = plot.get_xdata() - np.array(self.position.x_center)
            ydata = plot.get_ydata() - np.array(self.position.y_center)
            xdata, ydata = rotate(xdata, ydata, self.position.angle)
            xdata, ydata = rotate(xdata, ydata, -angle)
            plot.set_xdata(xdata + x_center)
            plot.set_ydata(ydata + y_center)

        for fill in self.fills:
            xy_data = fill.get_xy() - [self.position.x_center, self.position.y_center]
            xy_data[:, 0], xy_data[:, 1] = rotate(xy_data[:, 0], xy_data[:, 1], self.position.angle)
            xy_data[:, 0], xy_data[:, 1] = rotate(xy_data[:, 0], xy_data[:, 1], -angle)
            xy_data[:, 0] += x_center
            xy_data[:, 1] += y_center
            fill.set_xy(xy_data)

        for text in self.texts:
            text.set_position((x_center, y_center))

        self.position.x_center = x_center
        self.position.y_center = y_center
        self.position.angle = angle

    def change_color(
        self,
        face_color: Optional[Tuple[float, float, float]] = None,
        edge_color: Optional[Tuple[float, float, float]] = None,
    ) -> None:
        """Change the colors of the filled areas and the plotted lines.

        :param face_color: The new color of the filled area.
        :param edge_color: The new color of the edge of the filled areas and the lines.
        """
        if face_color is not None:
            for fill in self.fills:
                fill.set_facecolor(face_color)
        if edge_color is not None:
            for fill in self.fills:
                fill.set_edgecolor(edge_color)
            for plot in self.plots:
                plot.set_color(edge_color)


class MaxSpeedOptions(Options):
    """Class containing the default values of the options of a way object."""

    fontsize: Optional[float] = None
    outer_radius: Optional[float] = None
    inner_radius: Optional[float] = None
    outer_color: Tuple[float, float, float] = (1, 0, 0)
    inner_color: Tuple[float, float, float] = (1, 1, 1)


class MaxSpeed(StaticObject):
    """A max speed sign that is drawn on a given axes.

    Attributes:
        options (MaxSpeedOptions): Options that can be set for the sign.
    """

    def __init__(
        self, axes: Axes, text: Optional[str] = None, options: Optional[MaxSpeedOptions] = None
    ) -> None:
        """Creating a sign with the maximum allowable speed.

        :param axes: The axes on which the speed sign is supposed to be drawn.
        :param text: The text that should be places inside the sign.
        :param options: Additional options for the speed sign (see MaxSpeedOptions).
        """
        self.options = MaxSpeedOptions() if options is None else options
        self.set_radius(axes)
        StaticObject.__init__(self, axes)

        # Draw the sign
        theta = np.linspace(0, 2 * np.pi, 40)
        xouter = np.cos(theta) * self.options.outer_radius
        youter = np.sin(theta) * self.options.outer_radius
        xinner = np.cos(theta) * self.options.inner_radius
        yinner = np.sin(theta) * self.options.inner_radius
        self.position = StaticObjectPosition()
        self.fills = (
            axes.fill(
                xouter + self.position.x_center,
                youter + self.position.y_center,
                color=self.options.outer_color,
            )[0],
            axes.fill(
                xinner + self.position.x_center,
                yinner + self.position.y_center,
                color=self.options.inner_color,
            )[0],
        )

        # Show text
        if text is not None:
            self.texts = (
                axes.text(
                    self.position.x_center,
                    self.position.y_center,
                    text,
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=self.options.fontsize,
                ),
            )

    def set_radius(self, axes: Axes) -> None:
        """Set the radius of the sign if it is not already set.

        If both the inner radius and the outer radius is set, nothing is done. If only
        the outer radius is set, the inner radius will be set to 80 % of the outer
        radius. If only the inner radius is set, the outer radius will be set to 125 %
        of the inner radius. If both radii are not set, the outer radius is set to 3.3 %
        of the width of the axes and the inner radius is set to 80 % of the outer radius.

        :param axes: The axes that is used to plot the sign on.
        """
        if self.options.inner_radius is None and self.options.outer_radius is None:
            self.options.outer_radius = np.diff(axes.get_xlim())[0] * 0.033
            self.options.inner_radius = 0.8 * self.options.outer_radius
        elif self.options.inner_radius is None and self.options.outer_radius is not None:
            self.options.inner_radius = 0.8 * self.options.outer_radius
        elif self.options.outer_radius is None and self.options.inner_radius is not None:
            self.options.outer_radius = 1.25 * self.options.inner_radius


class TurnArrowOptions(Options):
    """Class containing the default values of the options of a turn arrow object."""

    width: float = 0.9
    length: float = 2.5
    face_color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    edge_color: Tuple[float, float, float] = (0, 0, 0)
    layer: int = 0


class TurnArrow(StaticObject):
    """A turning arrow that is typically drawn on the road.

    The turning arrow shows the supposed direction of vehicles driving in the
    specific lane. Currently, the directions 'left', 'right', 'leftright',
    'leftthrough', 'throughright', and 'through' are supported.

    Attributes:
        direction (str): The direction that is indicated by the turning arrow.
        options (TurnArrowOptions): Options that can be set for the sign.
    """

    def __init__(
        self,
        axes: Axes,
        direction: Optional[str] = None,
        options: Optional[TurnArrowOptions] = None,
    ) -> None:
        """Creating a turning arrow.

        :param axes: The axes on which the turning arrow is supposed to be drawn.
        :param direction: Choose between 'through' (default), 'left', 'right', 'leftright',
                         'leftthrough', and 'throughright'.
        :param options: Additional options for the turning arrow (see TurnArrowOptions).
        """
        self.options = TurnArrowOptions() if options is None else options
        StaticObject.__init__(self, axes)
        self.direction = direction

        # Get coordinates of the arrow
        if self.direction in ("right", "left"):
            xdata = [-0.3, 0.3, 0.12, 0.24, 0.42, 0.54, 0.54, 1.2, 0.54, 0.54, 0.3, 0.12, -0.12]
            ydata = [
                -0.5,
                -0.5,
                0.152,
                0.174,
                0.189,
                0.189,
                0.053,
                0.242,
                0.5,
                0.28,
                0.28,
                0.265,
                0.227,
            ]
            if self.direction == "left":
                xdata = [-xdata_element for xdata_element in xdata]
        elif self.direction == "leftright":
            xdata = [
                -0.3,
                0.3,
                0.12,
                0.24,
                0.42,
                0.54,
                0.54,
                1.2,
                0.54,
                0.54,
                0.3,
                0.12,
                -0.12,
                -0.3,
                -0.54,
                -0.54,
                -1.2,
                -0.54,
                -0.54,
                -0.42,
                -0.24,
                -0.12,
            ]
            ydata = [
                -0.5,
                -0.5,
                0.152,
                0.174,
                0.189,
                0.189,
                0.053,
                0.242,
                0.5,
                0.28,
                0.28,
                0.265,
                0.265,
                0.28,
                0.28,
                0.5,
                0.242,
                0.053,
                0.189,
                0.189,
                0.174,
                0.152,
            ]
        elif self.direction in ("leftthrough", "throughright"):
            xdata = [
                0.3,
                0.233,
                0.433,
                0.833,
                0.9,
                0.9,
                1.3,
                0.9,
                0.9,
                0.967,
                0.433,
                0.233,
                0.167,
                0.167,
                0.5,
                0,
                -0.5,
                -0.167,
                -0.3,
            ]
            ydata = [
                -0.5,
                -0.102,
                -0.078,
                -0.063,
                -0.063,
                -0.133,
                -0.023,
                0.102,
                0.023,
                0.023,
                0.016,
                0,
                0,
                0.117,
                0.117,
                0.5,
                0.117,
                0.117,
                -0.5,
            ]
            if self.direction == "leftthrough":
                xdata = [-xdata_element for xdata_element in xdata]
        else:
            xdata = [-0.3, 0.3, 0.167, 0.5, 0, -0.5, -0.167]
            ydata = [-0.5, -0.5, 0.105, 0.105, 0.5, 0.105, 0.105]

        # Set width and height
        xdata_array = np.concatenate((xdata, [xdata[0]])) * self.options.width
        ydata_array = np.concatenate((ydata, [ydata[0]])) * self.options.length

        # Plot the arrow
        self.position = StaticObjectPosition()
        self.fills = (
            axes.fill(
                xdata_array + self.position.x_center,
                ydata_array + self.position.y_center,
                facecolor=self.options.face_color,
                edgecolor=self.options.edge_color,
                zorder=self.options.layer,
            )[0],
        )


class BuildingOptions(Options):
    """Options for impassable objects."""

    size: float = 2
    size_x: Optional[float] = None
    size_y: Optional[float] = None
    x_data: Optional[np.ndarray] = None
    y_data: Optional[np.ndarray] = None
    face_color: Tuple[float, float, float] = (0.5, 0.5, 1)
    edge_color: Tuple[float, float, float] = (0, 0, 1)
    hatch: str = "//"


class Building(StaticObject):
    """A static object, e.g., a building, an impassable object, or a passable object."""

    def __init__(self, axes: Axes, options: Optional[BuildingOptions] = None) -> None:
        """Creating a 'building'.

        :param axes: The axes on which the building is supposed to be drawn.
        :param options: Additional options for the building (see BuildingOptions).
        """
        self.options = BuildingOptions() if options is None else options
        StaticObject.__init__(self, axes)

        if self.options.size_x is None:
            self.options.size_x = self.options.size
        if self.options.size_y is None:
            self.options.size_y = self.options.size

        if self.options.x_data is None:
            self.options.x_data = np.array([1, 1, -1, -1]) * self.options.size_x / 2
            self.options.y_data = np.array([1, -1, -1, 1]) * self.options.size_y / 2

        fill_options: Dict[str, Union[Tuple[float, float, float], str]]
        fill_options = {"facecolor": self.options.face_color, "edgecolor": self.options.edge_color}
        if self.options.hatch:
            fill_options["hatch"] = self.options.hatch
        self.fills = (axes.fill(self.options.x_data, self.options.y_data, **fill_options)[0],)


class StripesOptions(TurnArrowOptions):
    """Class containing the default values of the options of a stripes object."""

    face_color2: Tuple[float, float, float] = (1.0, 0.0, 0.0)
    nstripes: int = 10


class Stripes(StaticObject):
    """Class for drawing a rectangular object with diagonal stripes."""

    def __init__(self, axes: Axes, options: Optional[StripesOptions] = None) -> None:
        """Creating an object with diagonal stripes (e.g., for a road works sign).

        :param axes: The axes on which the turning arrow is supposed to be drawn.
        :param options: Additional options for the stripes object (see StripesOptions).
        """
        StaticObject.__init__(self, axes)
        self.options = StripesOptions() if options is None else options

        # Draw the rectangle.
        self.fills = (
            axes.fill(
                np.array([-1, 1, 1, -1]) * self.options.width / 2,
                np.array([1, 1, -1, -1]) * self.options.length / 2,
                facecolor=self.options.face_color,
                edgecolor=None,
                zorder=self.options.layer,
            )[0],
        )
        w_stripe = (self.options.width + self.options.length) / self.options.nstripes
        for i in range((self.options.nstripes + 1) // 2):
            alphai, betai = 2 * i * w_stripe, (2 * i + 1) * w_stripe

            xdata = [min(alphai, self.options.width)]
            ydata = [alphai - xdata[0]]

            if alphai < self.options.width < betai:
                xdata.append(self.options.width)
                ydata.append(0)

            xdata.append(min(betai, self.options.width))
            ydata.append(betai - xdata[-1])

            if i < self.options.nstripes - 1:
                ydata.append(min(betai, self.options.length))
                xdata.append(betai - ydata[-1])

            if alphai < self.options.length < betai:
                xdata.append(0)
                ydata.append(self.options.length)

            if i > 0:
                ydata.append(min(alphai, self.options.length))
                xdata.append(alphai - ydata[-1])

            self.fills += (
                axes.fill(
                    np.array(xdata) - self.options.width / 2,
                    self.options.length / 2 - np.array(ydata),
                    facecolor=self.options.face_color2,
                    edgecolor=None,
                    zorder=self.options.layer,
                )[0],
            )
        self.plots = (
            axes.plot(
                np.array([-1, 1, 1, -1, -1]) * self.options.width / 2,
                np.array([1, 1, -1, -1, 1]) * self.options.length / 2,
                color=self.options.edge_color,
                zorder=self.options.layer,
            )[0],
        )

    def change_color(
        self,
        face_color: Optional[Tuple[float, float, float]] = None,
        edge_color: Optional[Tuple[float, float, float]] = None,
        face_color2: Optional[Tuple[float, float, float]] = None,
    ) -> None:
        """Change the colors of the filled areas and the plotted lines.

        :param face_color: The new color of the filled area.
        :param edge_color: The new color of the edge of the filled areas and the lines.
        :param face_color2: The new color of the stripes.
        """
        if face_color is not None:
            self.fills[0].set_facecolor(face_color)
        if edge_color is not None:
            self.plots[0].set_color(edge_color)
        if face_color2 is not None:
            for fill in self.fills[1:]:
                fill.set_facecolor(face_color2)
