"""Traffic light.

Author(s): Erwin de Gelder
"""

from enum import Enum
from typing import Optional, Tuple

import numpy as np
from matplotlib.axes import Axes

from .options import Options
from .static_objects import StaticObject


class TrafficLightStatus(Enum):
    """Possible status for traffic light."""

    REMOVED = 0
    IDLE = 1
    RED = 2
    AMBER = 3
    GREEN = 4


class TrafficLightOptions(Options):
    """Class containing the default values of the options of a traffic light object."""

    radius: float = 0
    width: float = 0
    length: float = 0
    inter_dist: float = 0
    rectangle_color: Tuple[float, float, float] = (0, 0, 0)
    red_color: Tuple[float, float, float] = (1, 0, 0)
    amber_color: Tuple[float, float, float] = (1, 1, 0)
    green_color: Tuple[float, float, float] = (0, 1, 0)
    red_idle_color: Tuple[float, float, float] = (0.4, 0, 0)
    amber_idle_color: Tuple[float, float, float] = (0.4, 0.4, 0)
    green_idle_color: Tuple[float, float, float] = (0, 0.4, 0)
    signal_lines: int = 8
    signal_inner_radius: float = 0
    signal_outer_radius: float = 0
    amber: bool = True


class NoAmberError(Exception):
    """Error to be raised in case amber light is set while traffic light does not have amber."""

    def __init__(self) -> None:
        """Description of error."""
        super().__init__("Cannot show amber signal: traffic light signal has no amber.")


class TrafficLight(StaticObject):
    """A traffic light.

    Attributes:
        options (TrafficLightOptions): Options that can be set for the traffic light.
        axes (Axes): The axes that are used for plotting.
        status (TrafficLightStatus): The status of the traffic light.
    """

    def __init__(self, axes: Axes, options: Optional[TrafficLightOptions] = None) -> None:
        """Create a traffic light object.

        :param axes: The axes on which the traffic light is supposed to be drawn.
        :param options: Any options for the traffic light, see TrafficLightOptions.
        """
        self.options = TrafficLightOptions() if options is None else options
        self.axes = axes
        StaticObject.__init__(self, axes)
        if self.options.radius == 0:
            self.options.radius = np.diff(axes.get_xlim())[0] * 0.005
        if self.options.width == 0:
            self.options.width = self.options.radius * 2.6
        if self.options.length == 0:
            if self.options.amber:
                self.options.length = self.options.radius * 7.2
            else:
                self.options.length = self.options.radius * 4.9
        if self.options.inter_dist == 0:
            self.options.inter_dist = self.options.radius * 2.3
        if self.options.signal_inner_radius == 0:
            self.options.signal_inner_radius = self.options.radius * 1.8
        if self.options.signal_outer_radius == 0:
            self.options.signal_outer_radius = self.options.radius * 2.5
        self.status = TrafficLightStatus.REMOVED
        self.plot_idle()

    def plot_idle(self) -> None:
        """Plot an idle traffic light."""
        if self.status != TrafficLightStatus.REMOVED:
            self.remove()

        self.status = TrafficLightStatus.IDLE
        # Draw the rectangle.
        x_data = np.array(
            [
                -self.options.width / 2,
                self.options.width / 2,
                self.options.width / 2,
                -self.options.width / 2,
            ]
        )
        y_data = np.array(
            [
                self.options.length / 2,
                self.options.length / 2,
                -self.options.length / 2,
                -self.options.length / 2,
            ]
        )
        self.fills = (self.axes.fill(x_data, y_data, color=self.options.rectangle_color)[0],)

        # Draw the red, amber, and green signals.
        theta = np.linspace(0, 2 * np.pi, 30)
        x_data = self.options.radius * np.cos(theta)
        y_data = self.options.radius * np.sin(theta)
        if self.options.amber:
            self.fills += (
                self.axes.fill(
                    x_data, y_data + self.options.inter_dist, color=self.options.red_color
                )[0],
                self.axes.fill(x_data, y_data, color=self.options.amber_color)[0],
                self.axes.fill(
                    x_data, y_data - self.options.inter_dist, color=self.options.green_color
                )[0],
            )
        else:
            self.fills += (
                self.axes.fill(
                    x_data, y_data + 0.5 * self.options.inter_dist, color=self.options.red_color
                )[0],
                self.axes.fill(
                    x_data, y_data - 0.5 * self.options.inter_dist, color=self.options.green_color
                )[0],
            )

    def idle(self) -> None:
        """Plot an idle traffic light and reposition it."""
        self.plot_idle()
        self.set_position()

    def set_position(self) -> None:
        """Set the position of the traffic light correctly.

        It can happen that the position of the traffic light does not coincide with
        the information given by self.position. This happens when the traffic light
        is redrawn, e.g., using self.idle(). To set the position correcly again,
        this function can be used.
        """
        x_center, y_center = self.position.x_center, self.position.y_center
        angle = self.position.angle
        self.position.x_center, self.position.y_center, self.position.angle = 0, 0, 0
        self.change_pos(x_center, y_center, angle)

    def remove(self) -> None:
        """Remove the traffic light."""
        for fill in self.fills:
            fill.remove()
            del fill
        for plot in self.plots:
            plot.remove()
            del plot
        self.plots = ()
        self.fills = ()
        self.status = TrafficLightStatus.REMOVED

    def signal_data(self, signal: TrafficLightStatus) -> Tuple[np.ndarray, np.ndarray]:
        """Get the x and y data of the signal.

        :param signal: The signal to show.
        :return: x and y data of the signal.
        """
        xdata = np.zeros((2, self.options.signal_lines))
        ydata = np.array(np.zeros_like(xdata))
        for i, theta in enumerate(
            np.linspace(0, np.pi * 2, self.options.signal_lines, endpoint=False)
        ):
            xdata[0, i] = np.cos(theta) * self.options.signal_inner_radius
            xdata[1, i] = np.cos(theta) * self.options.signal_outer_radius
            ydata[0, i] = np.sin(theta) * self.options.signal_inner_radius
            ydata[1, i] = np.sin(theta) * self.options.signal_outer_radius
        if signal in (TrafficLightStatus.RED, TrafficLightStatus.GREEN):
            distance = self.options.inter_dist
            if not self.options.amber:
                distance = 0.5 * self.options.inter_dist
            if signal == TrafficLightStatus.RED:
                ydata += distance
            elif signal == TrafficLightStatus.GREEN:
                ydata -= distance
        return xdata, ydata

    def red(self) -> None:
        """Show red light signal."""
        self.remove()
        self.plot_idle()
        self.status = TrafficLightStatus.RED
        xdata, ydata = self.signal_data(self.status)
        self.plots = (self.axes.plot(xdata, ydata, color=self.options.red_color)[0],)
        if self.options.amber:
            self.fills[2].set_color(self.options.amber_idle_color)
            self.fills[3].set_color(self.options.green_idle_color)
        else:
            self.fills[2].set_color(self.options.green_idle_color)
        self.set_position()

    def amber(self) -> None:
        """Show amber light signal."""
        if not self.options.amber:
            raise NoAmberError
        self.remove()
        self.plot_idle()
        self.status = TrafficLightStatus.AMBER
        xdata, ydata = self.signal_data(self.status)
        self.plots = (self.axes.plot(xdata, ydata, color=self.options.amber_color)[0],)
        self.fills[1].set_color(self.options.red_idle_color)
        self.fills[3].set_color(self.options.green_idle_color)
        self.set_position()

    def green(self) -> None:
        """Show green light signal."""
        self.remove()
        self.plot_idle()
        self.status = TrafficLightStatus.GREEN
        xdata, ydata = self.signal_data(self.status)
        self.plots = (self.axes.plot(xdata, ydata, color=self.options.green_color)[0],)
        self.fills[1].set_color(self.options.red_idle_color)
        if self.options.amber:
            self.fills[2].set_color(self.options.amber_idle_color)
        self.set_position()

    def set_status(self, status: TrafficLightStatus) -> None:
        """Set the status of the traffic light.

        :param status: The new status of the traffic light.
        """
        if status == TrafficLightStatus.REMOVED:
            self.remove()
        elif status == TrafficLightStatus.IDLE:
            self.idle()
        elif status == TrafficLightStatus.RED:
            self.red()
        elif status == TrafficLightStatus.AMBER:
            self.amber()
        elif status == TrafficLightStatus.GREEN:
            self.green()

    def __str__(self) -> str:
        """Provide simple description of traffic light.

        :return: Text with current status of traffic light.
        """
        return f"Traffic light, status={self.status.name:s}"
