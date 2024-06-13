"""Truck object.

Author(s): Erwin de Gelder
"""

from typing import Optional, Tuple, Union

import numpy as np
from matplotlib.axes import Axes

from .polygon import Polygon
from .utilities import rotate
from .vehicle import Vehicle, VehicleOptions


class TruckOptions(VehicleOptions):
    """The default values of the options of a truck.

    The following list shows the options (within parentheses default values):
        length (4.5): The length of the truck.
        width (2.5): The width of the truck.
        line_width (1): The line width for plotting the truck.
        x_position_init (0): The initial horizontal position of the truck.
        y_position_init (0): The initial vertical position of the truck.
        angle_init (0): The initial angle of the truck.
        color ((0, 0.4375, 0.75)): Main color of the truck.
        color2 ((0.02, 0.02, 0.02)): Secondary color of the truck.
        color3 ((0.2, 0.2, 0.2)): Tertiary color of the truck.
        trailer (False): Whether the truck has a trailer.
        l_trailer (9.0): Distance front trailer towards pivot point.
        w_trailer (None): Width of trailer (by default, same as width truck).
        l_pivot_truck (1.2): Distance center truck towards pivot point.
        l_pivot_trailer (0.7): Distance front trailer towards pivot point.
        edgecolor ((0, 0, 0)): In case of a non-transparent truck, the color of
            the lines is set using this option.
        layer (2): The layer in which the truck will be plotted.
    """

    length: float = 4.5
    width: float = 2.5
    color2: Tuple[float, float, float] = (0.02, 0.02, 0.02)
    color3: Tuple[float, float, float] = (0.2, 0.2, 0.2)

    trailer: bool = False
    l_trailer: float = 9.0
    w_trailer: float = 0
    l_pivot_truck: float = 1.2
    l_pivot_trailer: float = 0.7

    def __init__(self, **kwargs: Union[bool, float, Tuple[float, float, float]]) -> None:
        """Class containing all kinds of options for a truck.

        :param kwargs: Any options can be set through kwargs.
        """
        VehicleOptions.__init__(self, **kwargs)
        if self.w_trailer == 0:
            self.w_trailer = self.width


class Truck(Vehicle):
    """Plot a truck on the scene.

    Create a truck object using Truck(axes, options).

    Attributes:
        options (TruckOptions): All options. For a detailed description, see above.
        trailer_angle (float): The angle of the trailer wrt the truck.
        axes (Axes): The axes that is used for plotting.
    """

    def __init__(self, axes: Axes, options: Optional[TruckOptions] = None) -> None:
        """Create a truck, possibly with a trailer.

        :param axes: The axes on which the truck must be plotted.
        :param options: Any options for configuring the truck.
        """
        if options is None:
            options = TruckOptions()
        self.trailer_angle = 0.0
        Vehicle.__init__(self, axes, options)
        self.options: TruckOptions

    def plot_vehicle(self) -> None:
        """Plot the truck on the axes."""
        # Plot the truck.
        yoffset = 160.5
        yscale = 301
        xoffset = 103
        xscale = 170

        # Fill with main color, mirror.
        xdata = np.array([103, 32, 32, 19, 17, 18, 21, 22, 25, 30, 38, 47, 63, 103])
        ydata = np.array([152, 152, 156, 156, 153, 86, 49, 38, 24, 18, 13, 11, 10, 10])
        xdata = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
        ydata = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata * self.options.width,
                -ydata * self.options.length,
                facecolor=self.options.color,
                edgecolor=self.options.edgecolor,
                zorder=self.options.layer,
            ),
        )

        # Fill fuel tank, both sides.
        xdata = (np.array([28, 28, 65, 65]) - xoffset) / xscale
        ydatas = [
            np.array([171, 182, 182, 171]),
            np.array([184, 203, 203, 184]),
            np.array([205, 224, 224, 205]),
            np.array([226, 237, 237, 226]),
        ]
        for ydata in ydatas:
            ydata_new = (ydata - yoffset) / yscale
            self.fills += (
                Polygon(
                    self.axes,
                    xdata * self.options.width,
                    -ydata_new * self.options.length,
                    facecolor=self.options.color,
                    edgecolor=self.options.edgecolor,
                    zorder=self.options.layer,
                ),
                Polygon(
                    self.axes,
                    -xdata * self.options.width,
                    -ydata_new * self.options.length,
                    facecolor=self.options.color,
                    edgecolor=self.options.edgecolor,
                    zorder=self.options.layer,
                ),
            )

        # Fill mirror and other black (color2) part, both sides.
        xdatas = [np.array([21, 7, 7, 11, 22]), np.array([37, 37, 58, 58])]
        ydatas = [np.array([49, 45, 41, 38, 38]), np.array([152, 168, 168, 152])]
        for xdata, ydata in zip(xdatas, ydatas):
            xdata_new = (xdata - xoffset) / xscale
            ydata_new = (ydata - yoffset) / yscale
            self.fills += (
                Polygon(
                    self.axes,
                    xdata_new * self.options.width,
                    -ydata_new * self.options.length,
                    facecolor=self.options.color2,
                    edgecolor=self.options.edgecolor,
                    linewidth=self.options.line_width,
                    zorder=self.options.layer,
                    fixed_color=True,
                ),
                Polygon(
                    self.axes,
                    -xdata_new * self.options.width,
                    -ydata_new * self.options.length,
                    facecolor=self.options.color2,
                    edgecolor=self.options.edgecolor,
                    linewidth=self.options.line_width,
                    zorder=self.options.layer,
                    fixed_color=True,
                ),
            )

        # Draw a line on top of the truck.
        xdata = (np.array([40, 42, 164, 166]) - xoffset) / xscale
        ydata = (np.array([152, 106, 106, 152]) - yoffset) / yscale
        self.plots += (
            self.axes.plot(
                xdata * self.options.width,
                -ydata * self.options.length,
                color=self.options.edgecolor,
                linewidth=self.options.line_width,
                zorder=self.options.layer,
            )[0],
        )

        # Draw the contour of the back of the truck, mirror.
        xdata = np.array(
            [
                63,
                63,
                74,
                74,
                27,
                27,
                74,
                74,
                27,
                27,
                74,
                74,
                27,
                27,
                74,
                74,
                30,
                28,
                26,
                26,
                27,
                30,
                30,
                70,
                70,
                73,
                73,
                104,
            ]
        )
        ydata = np.array(
            [
                152,
                165,
                165,
                182,
                182,
                184,
                184,
                203,
                203,
                205,
                205,
                224,
                224,
                226,
                226,
                241,
                241,
                244,
                252,
                300,
                304,
                305,
                311,
                311,
                307,
                307,
                314,
                314,
            ]
        )
        xdata3 = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
        ydata3 = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
        self.plots += (
            self.axes.plot(
                xdata3 * self.options.width,
                -ydata3 * self.options.length,
                color=self.options.edgecolor,
                linewidth=self.options.line_width,
                zorder=self.options.layer,
            )[0],
        )

        # Draw part to which trailer could be attached (color3), mirror.
        xdata2 = np.array([103, 102, 100, 99, 96, 94, 91, 89, 84, 80, 80, 83, 88, 93, 99, 103])
        ydata2 = np.array(
            [262, 263, 268, 277, 286, 288, 288, 286, 276, 262, 250, 241, 235, 232, 231, 231]
        )
        xdata3 = (np.concatenate((xdata2, 2 * xoffset - np.flipud(xdata2))) - xoffset) / xscale
        ydata3 = (np.concatenate((ydata2, np.flipud(ydata2))) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata3 * self.options.width,
                -ydata3 * self.options.length,
                facecolor=self.options.color3,
                edgecolor=self.options.edgecolor,
                linewidth=self.options.line_width,
                zorder=self.options.layer,
                fixed_color=True,
            ),
        )

        # Draw back part of the truck, twice.
        xdata = np.concatenate(
            (xdata, xdata2, np.array([103, 80, 80, 98, 98, 80, 80, 98, 98, 103, 103]))
        )
        ydata = np.concatenate(
            (ydata, ydata2, np.array([228, 228, 205, 205, 194, 194, 170, 170, 228, 228, 152]))
        )
        xdata = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
        ydata = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata * self.options.width,
                -ydata * self.options.length,
                facecolor=self.options.color2,
                linewidth=0,
                zorder=self.options.layer,
                fixed_color=True,
            ),
        )

        # Plot the trailer.
        if self.options.trailer:
            y_truck = (
                self.options.l_pivot_trailer
                - self.options.l_pivot_truck
                - self.options.l_trailer / 2
            )
            xdata = np.array([-1, 1, 1, -1]) * self.options.w_trailer / 2
            ydata = np.array([1, 1, -1, -1]) * self.options.l_trailer / 2 + y_truck
            self.fills += (
                Polygon(
                    self.axes,
                    xdata,
                    ydata,
                    facecolor=self.options.color,
                    edgecolor=self.options.edgecolor,
                    linewidth=self.options.line_width,
                    zorder=self.options.layer + 1,
                ),
            )

    def change_trailer_angle(self, angle: float) -> None:
        """Change the angle of the trailer.

        :param angle: The angle of the trailer wrt the truck.
        """
        x_pivot = self.position.x_center - np.sin(self.position.angle) * self.options.l_pivot_truck
        y_pivot = self.position.y_center - np.cos(self.position.angle) * self.options.l_pivot_truck
        xy_data = self.fills[-1].get_xy() - [x_pivot, y_pivot]
        xy_data[:, 0], xy_data[:, 1] = rotate(
            xy_data[:, 0], xy_data[:, 1], self.position.angle + self.trailer_angle
        )
        xy_data[:, 0], xy_data[:, 1] = rotate(
            xy_data[:, 0], xy_data[:, 1], -self.position.angle - angle
        )
        xy_data[:, 0] += x_pivot
        xy_data[:, 1] += y_pivot
        self.fills[-1].set_xy(xy_data)
        self.trailer_angle = angle
