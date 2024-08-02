"""Bus object.

Author(s): Erwin de Gelder
"""

from typing import Optional, Tuple, Union

import numpy as np
from matplotlib.axes import Axes

from .path_follower import PathFollower
from .polygon import Polygon
from .utilities import hsl2rgb, rgb2hsl
from .vehicle import Vehicle, VehicleOptions


class BusOptions(VehicleOptions):
    """The default values of the options of a bus.

    The following list shows the options (within parentheses default values):
        length (0): The length of the bus (by default based on width and AR).
        width (2.0): The width of the bus.
        aspect_ratio (2.69): Aspect ratio of the bus' shape.
        line_width (1): The line width for plotting the bus.
        x_position_init (0): The initial horizontal position of the bus.
        y_position_init (0): The initial vertical position of the bus.
        angle_init (0): The initial angle of the bus.
        color ((0, 0.4375, 0.75)): Main color of the bus.
        color2 (None): Secondary color of the truck. By default, lighter version
            of color.
        luminance_diff (0.3): If color2 is not set, specify luminance difference
            between color2 and color.
        windowcolor ([1, 1, 1]): The color of the front window.
        edgecolor ((0, 0, 0)): In case of a non-transparent truck, the color of
            the lines is set using this option.
        layer (2): The layer in which the truck will be plotted.
    """

    length: float = 0
    width: float = 2.5
    aspect_ratio: float = 2.69
    window_color: Tuple[float, float, float] = (1, 1, 1)
    color2: Optional[Tuple[float, float, float]] = None
    luminance_diff: float = 0.3

    def __init__(self, **kwargs: Union[float, Tuple[float, float, float]]) -> None:
        """Create a container for all options for a bus.

        :param kwargs: Use kwargs to set any option other then the default option.
        """
        VehicleOptions.__init__(self, **kwargs)
        if self.length == 0:
            self.length = self.width * self.aspect_ratio


class Bus(Vehicle):
    """Plot a bus on the scene.

    Create a bus object using Bus(axes, options).

    Attributes:
        options (BusOptions): All options. For a detailed description, see above.
        is_braking (bool): Whether the car is braking or not.
        axes (Axes): The axes that is used for plotting.
        path_follower (PathFollower): Optional object, used when vehicle needs to follow a path.
    """

    def __init__(
        self,
        axes: Axes,
        options: Optional[BusOptions] = None,
        path_follower: Optional[PathFollower] = None,
    ) -> None:
        """Create a bus object.

        :param axes: The axes on which the car is supposed to be drawn.
        :param options: Various options for the car, see CarOptions.
        :param path_follower: Path that the car needs to follow (if any).
        """
        if options is None:
            options = BusOptions()
        Vehicle.__init__(self, axes, options, path_follower)
        self.options: BusOptions

    def determine_color2(self) -> Tuple[float, float, float]:
        """If defined, just return color2. If not, return lighter version of color.

        :return: RGB tuple of color.
        """
        if self.options.color2 is None:
            hue, saturation, luminance = rgb2hsl(*self.options.color)
            luminance = min(1.0, max(0.0, luminance + self.options.luminance_diff))
            return hsl2rgb(hue, saturation, luminance)
        return self.options.color2

    def plot_vehicle(self) -> None:
        """Plot the bus on the axes."""
        # Plot the bus.
        yoffset = 8 + 84 * self.options.aspect_ratio
        yscale = 168 * self.options.aspect_ratio
        xoffset = 106
        xscale = 168
        yrear = 8 + 168 * self.options.aspect_ratio

        # Fill with main color, mirror.
        xdata = np.array([76, 57, 36, 31, 25, 23, 22, 22, 23, 24, 27, 31, 35])
        ydata = np.array(
            [
                8,
                9,
                10,
                11,
                17,
                21,
                24,
                yrear - 14,
                yrear - 9,
                yrear - 7,
                yrear - 3,
                yrear - 1,
                yrear,
            ]
        )
        xdata_new = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
        ydata_new = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata_new * self.options.width,
                -ydata_new * self.options.length,
                facecolor=self.options.color,
                edgecolor=self.options.edgecolor,
                zorder=self.options.layer,
            ),
        )

        # Fill with window color, mirror.
        xdata = np.array([52, 34, 31, 31, 34, 78])
        ydata = np.array([12, 13, 16, 24, 63, 62])
        xdata_new = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
        ydata_new = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata_new * self.options.width,
                -ydata_new * self.options.length,
                facecolor=self.options.window_color,
                edgecolor=self.options.edgecolor,
                zorder=self.options.layer,
                fixed_color=True,
            ),
        )

        # Squares with lighter color.
        xdata = np.array([76, 136, 136, 76])
        for ysquare in (149, yrear - 113):
            ydata = np.array([30, 30, -30, -30]) + ysquare
            self.fills += (
                Polygon(
                    self.axes,
                    (xdata - xoffset) / xscale * self.options.width,
                    -(ydata - yoffset) / yscale * self.options.length,
                    facecolor=self.determine_color2(),
                    edgecolor=self.options.edgecolor,
                    zorder=self.options.layer,
                    fixed_color=True,
                ),
            )

        # Mirrors, on both sides
        xdata = np.array([22, 15, 15, 19, 19, 17, 11, 9, 9, 13, 13, 22])
        ydata = np.array([48, 41, 23, 23, 21, 20, 20, 21, 23, 23, 43, 52])
        for xdata2 in (xdata, 212 - xdata):
            self.fills += (
                Polygon(
                    self.axes,
                    (xdata2 - xoffset) / xscale * self.options.width,
                    -(ydata - yoffset) / yscale * self.options.length,
                    facecolor=self.options.edgecolor,
                    edgecolor=self.options.edgecolor,
                    zorder=self.options.layer,
                    fixed_color=True,
                ),
            )

        # Circles of ventilation
        for y_pos in (149, yrear - 113):
            for radius in (9, 20):
                xdata = radius * np.cos(np.linspace(0, 2 * np.pi, 50))
                ydata = y_pos + radius * np.sin(np.linspace(0, 2 * np.pi, 50))
                self.plots += (
                    self.axes.plot(
                        xdata / xscale * self.options.width,
                        -(ydata - yoffset) / yscale * self.options.length,
                        color=self.options.edgecolor,
                        linewidth=self.options.line_width,
                        zorder=self.options.layer,
                    )[0],
                )

        # Lines
        for x_pos, y_pos1, y_pos2 in zip(
            (52, 64, 76, 88, 100, 76, 88, 100),
            (119, 119, 191, 191, 191, yrear - 71, yrear - 71, yrear - 71),
            (
                yrear - 28,
                yrear - 28,
                yrear - 155,
                yrear - 155,
                yrear - 155,
                yrear - 28,
                yrear - 28,
                yrear - 28,
            ),
        ):
            for x_pos2 in (x_pos, 212 - x_pos):
                xdata = (np.ones(2) * x_pos2 - xoffset) / xscale * self.options.width
                ydata = -(np.array([y_pos1, y_pos2]) - yoffset) / yscale * self.options.length
                self.plots += (
                    self.axes.plot(
                        xdata,
                        ydata,
                        color=self.options.edgecolor,
                        linewidth=self.options.line_width,
                        zorder=self.options.layer,
                    )[0],
                )

    def change_color(
        self,
        face_color: Optional[Tuple[float, float, float]] = None,
        edge_color: Optional[Tuple[float, float, float]] = None,
    ) -> None:
        """Change the colors of the filled areas and the plotted lines.

        :param face_color: The new color of the filled area.
        :param edge_color: The new color of the edge of the filled areas and the lines.
        """
        Vehicle.change_color(self, face_color, edge_color)

        # Force face color change for two squares, which are the 3nd and 4th filled areas.
        # Note that these have a slight different color.
        if face_color is not None:
            self.options.color = face_color
            for fill in self.fills[2:4]:
                if isinstance(fill, Polygon):
                    fill.set_facecolor_forced(self.determine_color2())
