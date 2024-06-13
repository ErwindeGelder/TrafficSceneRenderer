"""Ambulance object.

Author(s): Erwin de Gelder
"""

from typing import Optional, Tuple

import numpy as np
from matplotlib.axes import Axes

from .bus import Bus, BusOptions
from .polygon import Polygon


class AmbulanceOptions(BusOptions):
    """The default values of the options of an ambulance.

    The following list shows the options (within parentheses default values):
        length (4.8): The length of the ambulance.
        width (2.5): The width of the ambulance.
        line_width (1): The line width for plotting the ambulance.
        x_position_init (0): The initial horizontal position of the ambulance.
        y_position_init (0): The initial vertical position of the ambulance.
        angle_init (0): The initial angle of the ambulance.
        color ((.8, .8, .8)): Main color of the ambulance.
        color2 (None): Secondary color of the truck. By default, lighter version
            of color.
        luminance_diff (0.3): If color2 is not set, specify luminance difference
            between color2 and color.
        window_color (.2, .2, .2): Color of the windscreen.
        front_light_color (1, 1, 1): Color of front light beam.
        emergency_color (.9, .15, .15): Color of emergency light.
        hospital_sign_color (.25, .5, .75): Color of the hospital signs.
        edgecolor ((0, 0, 0)): Not used.
        layer (2): The layer in which the ambulance will be plotted.
    """

    length: float = 4.8
    width: float = 2.5
    color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    color2: Optional[Tuple[float, float, float]] = None
    luminance_diff: float = 0.3
    window_color: Tuple[float, float, float] = (0.2, 0.2, 0.2)
    front_light_color: Tuple[float, float, float] = (1, 1, 1)
    emergency_color: Tuple[float, float, float] = (0.9, 0.15, 0.15)
    hospital_sign_color: Tuple[float, float, float] = (0.25, 0.5, 0.75)


class Ambulance(Bus):
    """Plot an ambulance on the scene.

    Create an ambulance object using Ambulance(axes, options).

    Attributes:
        options (TruckOptions): All options. For a detailed description, see above.
        axes (Axes): The axes that is used for plotting.
    """

    def __init__(self, axes: Axes, options: Optional[AmbulanceOptions] = None) -> None:
        """Create an ambulance.

        :param axes: Axes on which the ambulance has to be plotted.
        :param options: Options for configuring the appearance of the ambulance.
        """
        if options is None:
            options = AmbulanceOptions()
        Bus.__init__(self, axes, options)
        self.options: AmbulanceOptions

    def plot_vehicle(self) -> None:
        """Plot the ambulance."""
        yoffset = 158
        yscale = 304
        xoffset = 81.5
        xscale = 158

        # Fill with main color, mirror.
        xdata = np.array([37, 30, 24, 21, 20, 20, 12, 9, 6, 5, 5, 9, 15, 20, 20, 21, 25, 28])
        ydata = np.array(
            [6, 8, 13, 18, 23, 96, 96, 97, 100, 103, 105, 105, 104, 104, 302, 305, 309, 310]
        )
        xdata = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
        ydata = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata * self.options.width,
                -ydata * self.options.length,
                facecolor=self.options.color,
                edgecolor=None,
                zorder=self.options.layer,
            ),
        )

        # Secondary, mirror
        xdatas = (
            np.array([36, 33, 27, 26, 26, 28, 47, 52, 52, 55, 68]),
            np.array([65, 56, 50, 45, 42, 40, 40, 42]),
        )
        ydatas = (
            np.array([16, 17, 23, 26, 88, 88, 83, 29, 83, 82, 81]),
            np.array([118, 119, 120, 121, 122, 124, 297, 299]),
        )
        for xdata, ydata in zip(xdatas, ydatas):
            xdata_new = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
            ydata_new = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
            self.fills += (
                Polygon(
                    self.axes,
                    xdata_new * self.options.width,
                    -ydata_new * self.options.length,
                    facecolor=Bus.determine_color2(self),
                    edgecolor=None,
                    zorder=self.options.layer,
                    fixed_color=True,
                ),
            )

        # Front light beam, 2x
        xdata = np.array([54, 36, 32, 27, 27, 29, 34, 39, 54])
        ydata = np.array([8, 8, 9, 13, 19, 17, 14, 13, 13])
        for xdata2 in (xdata, 2 * xoffset - xdata):
            self.fills += (
                Polygon(
                    self.axes,
                    (xdata2 - xoffset) / xscale * self.options.width,
                    -(ydata - yoffset) / yscale * self.options.length,
                    facecolor=self.options.front_light_color,
                    edgecolor=None,
                    zorder=self.options.layer,
                    fixed_color=True,
                ),
            )

        # Emergency lights, 2x
        for xdata, ydata in (
            (np.array([70, 45, 45, 70]), np.array([145, 145, 167, 167])),
            (np.array([32, 25, 25, 27, 32]), np.array([168, 168, 300, 300, 298])),
            (np.array([54, 32, 32, 54]), np.array([305, 305, 308, 308])),
        ):
            for xdata2 in (xdata, 2 * xoffset - xdata):
                self.fills += (
                    Polygon(
                        self.axes,
                        (xdata2 - xoffset) / xscale * self.options.width,
                        -(ydata - yoffset) / yscale * self.options.length,
                        facecolor=self.options.emergency_color,
                        edgecolor=None,
                        zorder=self.options.layer,
                        fixed_color=True,
                    ),
                )

        # Main
        xdata = (np.array([70, 70, 93, 93]) - xoffset) / xscale
        ydata = (np.array([145, 167, 167, 145]) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata * self.options.width,
                -ydata * self.options.length,
                facecolor=self.options.color,
                edgecolor=None,
                zorder=self.options.layer,
            ),
        )

        # Hospital signs
        for ysign, rsign, dsign in ((47, 16, 6), (255, 28, 10.5)):
            xdata = np.zeros(18)
            ydata = np.zeros(18)
            theta = 0.0
            for i in range(6):
                xdata[i * 3] = np.sin(theta) * rsign + np.cos(theta) * dsign / 2
                ydata[i * 3] = np.cos(theta) * rsign - np.sin(theta) * dsign / 2
                xdata[i * 3 + 1] = (
                    np.sin(theta) * dsign / 2 * np.sqrt(3) + np.cos(theta) * dsign / 2
                )
                ydata[i * 3 + 1] = (
                    np.cos(theta) * dsign / 2 * np.sqrt(3) - np.sin(theta) * dsign / 2
                )
                theta += np.pi / 3
                xdata[i * 3 + 2] = np.sin(theta) * rsign - np.cos(theta) * dsign / 2
                ydata[i * 3 + 2] = np.cos(theta) * rsign + np.sin(theta) * dsign / 2
            self.fills += (
                Polygon(
                    self.axes,
                    xdata / xscale * self.options.width,
                    (yoffset - ysign) / yscale * self.options.length
                    - ydata / xscale * self.options.width,
                    facecolor=self.options.hospital_sign_color,
                    edgecolor=None,
                    zorder=self.options.layer,
                    fixed_color=True,
                ),
            )

        # Windscreen, mirror
        xdata = np.array([68, 55, 52, 47, 28, 42, 45, 50, 56, 65])
        ydata = np.array([81, 82, 83, 83, 88, 122, 121, 120, 119, 118])
        xdata = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
        ydata = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata * self.options.width,
                -ydata * self.options.length,
                facecolor=self.options.window_color,
                edgecolor=None,
                zorder=self.options.layer,
                fixed_color=True,
            ),
        )

        # Windscreen, 2x
        xdata = np.array([25, 38, 38, 25])
        ydata = np.array([168, 168, 127, 97])
        for xdata2 in (xdata, 2 * xoffset - xdata):
            self.fills += (
                Polygon(
                    self.axes,
                    (xdata2 - xoffset) / xscale * self.options.width,
                    -(ydata - yoffset) / yscale * self.options.length,
                    facecolor=self.options.window_color,
                    edgecolor=None,
                    zorder=self.options.layer,
                    fixed_color=True,
                ),
            )
