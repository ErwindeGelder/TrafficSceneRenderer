"""Constructing letters.

Author(s): Erwin de Gelder
"""

import sys
from typing import NamedTuple, Optional, Tuple

import numpy as np
from matplotlib.axes import Axes

from .static_objects import StaticObject, TurnArrowOptions

BIN_A = 65  # ord("A")
BIN_Z = 90  # ord("Z")
LetterOptions = TurnArrowOptions


class LetterData(NamedTuple):
    """Named tuple for storing letter data."""

    xdata: np.ndarray
    ydata: np.ndarray
    xcenter: float
    ycenter: float
    xdata_plot: Optional[Tuple[np.ndarray, ...]] = None
    ydata_plot: Optional[Tuple[np.ndarray, ...]] = None


class Letter(StaticObject):
    """Draw a letter (A to Z (capital) implemented)."""

    def __init__(self, axes: Axes, letter: str, options: Optional[LetterOptions] = None) -> None:
        """Create a single letter.

        :param axes: Axes on which the letter should be plotted.
        :param letter: The letter (A to Z; only capital supported).
        :param options: Any options for configuring the letter.
        """
        self.options = LetterOptions() if options is None else options
        StaticObject.__init__(self, axes)

        width, height = 3.5, 7
        if len(letter) == 1 and BIN_A <= ord(letter) <= BIN_Z:
            data = getattr(sys.modules[__name__], f"capital_{letter.lower()}")()  # type: LetterData
        else:
            msg = f"Letter '{letter:s}' is not yet implemented."
            raise NotImplementedError(msg)

        self.fills += (
            axes.fill(
                (data.xdata - data.xcenter) * self.options.width / width,
                (data.ydata - data.ycenter) * self.options.length / height,
                facecolor=self.options.face_color,
                edgecolor=None,
                zorder=self.options.layer,
            )[0],
        )
        if data.xdata_plot and data.ydata_plot:
            for xdata, ydata in zip(data.xdata_plot, data.ydata_plot):
                self.plots += (
                    axes.plot(
                        (np.concatenate((xdata, np.array([xdata[0]]))) - data.xcenter)
                        * self.options.width
                        / width,
                        (np.concatenate((ydata, np.array([ydata[0]]))) - data.ycenter)
                        * self.options.length
                        / height,
                        color=self.options.edge_color,
                        zorder=self.options.layer,
                    )[0],
                )
        else:
            self.plots += (
                axes.plot(
                    (np.concatenate((data.xdata, np.array([data.xdata[0]]))) - data.xcenter)
                    * self.options.width
                    / width,
                    (np.concatenate((data.ydata, np.array([data.ydata[0]]))) - data.ycenter)
                    * self.options.length
                    / height,
                    color=self.options.edge_color,
                    zorder=self.options.layer,
                )[0],
            )

    def change_color(
        self,
        face_color: Optional[Tuple[float, float, float]] = None,
        edge_color: Optional[Tuple[float, float, float]] = None,
    ) -> None:
        """Change the colors of the letter.

        :param face_color: The new color of the filled area.
        :param edge_color: The new color of the edge of the filled areas and the lines.
        """
        StaticObject.change_color(self, face_color=face_color)
        if edge_color is not None:
            for plot in self.plots:
                plot.set_color(edge_color)


class LettersOptions(TurnArrowOptions):
    """Options for object with multiple letters."""

    margin_ratio: float = 0.4


class Letters(StaticObject):
    """A sign consisting of multiple letters."""

    def __init__(self, axes: Axes, sign: str, options: Optional[LettersOptions] = None) -> None:
        """Create a series of letters.

        :param axes: Axes on which the letters should be plotted.
        :param sign: String containing the letters.
        :param options: Any options for configuring the letter.
        """
        self.options = LettersOptions() if options is None else options
        StaticObject.__init__(self, axes)

        n_letters = len(sign)
        letter_width = self.options.width / (
            n_letters + (n_letters - 1) * self.options.margin_ratio
        )
        self.x_letters = (
            np.arange(n_letters) * (1 + self.options.margin_ratio) + 0.5
        ) * letter_width - self.options.width / 2
        letter_options = LetterOptions(
            width=letter_width,
            length=self.options.length,
            face_color=self.options.face_color,
            edge_color=self.options.edge_color,
            layer=self.options.layer,
        )
        self.letters = [Letter(axes, letter, options=letter_options) for letter in sign]
        for letter, xpos in zip(self.letters, self.x_letters):
            letter.change_pos(xpos, 0, 0)

    def change_color(
        self,
        face_color: Optional[Tuple[float, float, float]] = None,
        edge_color: Optional[Tuple[float, float, float]] = None,
    ) -> None:
        """Change the colors of the letters.

        :param face_color: The new face color of the letters (if any).
        :param edge_color: The new edge color of the letters (if any).
        """
        for letter in self.letters:
            letter.change_color(face_color, edge_color)

    def change_pos(self, xcenter: float, ycenter: float, angle: float = 0) -> None:
        """Change the position of the letters.

        :param xcenter: New x-coordinate.
        :param ycenter: New y-coordinate.
        :param angle: New angle.
        """
        for letter, xpos in zip(self.letters, self.x_letters):
            letter.change_pos(xcenter + np.cos(angle) * xpos, ycenter - np.sin(angle) * xpos, angle)


def capital_a() -> LetterData:
    """Return data for letter A."""
    xdata = np.array([1, 0, 0.875, 2.625, 3.5, 2.5, 2.25, 1.25, 1.375, 2.125, 1.75])
    ydata = np.array([0, 0, 7, 7, 0, 0, 2, 2, 3, 3, 6])
    return LetterData(
        xdata=xdata,
        ydata=ydata,
        xcenter=1.75,
        ycenter=3.5,
        xdata_plot=(xdata[:8], xdata[8:]),
        ydata_plot=(ydata[:8], ydata[8:]),
    )


def capital_b() -> LetterData:
    """Return data for letter B."""
    theta1 = np.linspace(0, np.arcsin(3 / 4) + np.pi / 2, 20)
    theta2 = np.linspace(0, np.pi, 20)
    xdata = np.concatenate(
        (
            [1, 0, 0, 1],
            1.5 + 2 * np.sin(theta1),
            1.5 + 2 * np.sin(np.flip(theta1)),
            [1, 1],
            1.5 + np.sin(theta2),
            [1, 1],
            1.5 + np.sin(theta2),
            [1],
        )
    )
    ydata = np.concatenate(
        (
            [0, 0, 7, 7],
            5 + 2 * np.cos(theta1),
            2 - 2 * np.cos(np.flip(theta1)),
            [0, 1],
            2 - np.cos(theta2),
            [3, 4],
            5 - np.cos(theta2),
            [6],
        )
    )
    return LetterData(
        xdata=xdata,
        ydata=ydata,
        xcenter=1.75,
        ycenter=3.5,
        xdata_plot=(xdata[:44], xdata[45:67], xdata[67:]),
        ydata_plot=(ydata[:44], ydata[45:67], ydata[67:]),
    )


def capital_c() -> LetterData:
    """Return data for letter C."""
    theta = np.linspace(0, np.pi, 20)
    return LetterData(
        xdata=np.concatenate(
            (
                [0.75, 1.75],
                1.75 * np.cos(theta),
                -1.75 * np.cos(theta),
                [1.75, 0.75],
                0.75 * np.cos(theta),
                -0.75 * np.cos(theta),
            )
        ),
        ydata=np.concatenate(
            (
                [5, 5],
                5.25 + 1.75 * np.sin(theta),
                1.75 - 1.75 * np.sin(theta),
                [2, 2],
                1.75 - 0.75 * np.sin(theta),
                5.25 + 0.75 * np.sin(theta),
            )
        ),
        xcenter=0,
        ycenter=3.5,
    )


def capital_d() -> LetterData:
    """Return data for letter D."""
    theta = np.linspace(0, np.pi / 2, 10)
    xdata = np.concatenate(
        (
            1.5 + 2 * np.sin(theta),
            1.5 + 2 * np.cos(theta),
            [0, 0, 1.5, 1.5, 1, 1],
            1.5 + np.sin(theta),
            1.5 + np.cos(theta),
        )
    )
    ydata = np.concatenate(
        (
            2 - 2 * np.cos(theta),
            5 + 2 * np.sin(theta),
            [7, 0, 0, 1, 1, 6],
            5 + np.cos(theta),
            2 - np.sin(theta),
        )
    )
    return LetterData(
        xdata=xdata,
        ydata=ydata,
        xcenter=1.75,
        ycenter=3.5,
        xdata_plot=(xdata[:22], xdata[23:]),
        ydata_plot=(ydata[:22], ydata[23:]),
    )


def capital_e() -> LetterData:
    """Return data for letter E."""
    return LetterData(
        xdata=np.array([0, 0, 3.5, 3.5, 1, 1, 3, 3, 1, 1, 3.5, 3.5]),
        ydata=np.array([7, 0, 0, 1, 1, 3, 3, 4, 4, 6, 6, 7]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_f() -> LetterData:
    """Return data for letter F."""
    return LetterData(
        xdata=np.array([0, 3.5, 3.5, 1, 1, 2.5, 2.5, 1, 1, 0]),
        ydata=np.array([7, 7, 6, 6, 4, 4, 3, 3, 0, 0]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_g() -> LetterData:
    """Return data for letter G."""
    theta = np.linspace(0, np.pi, 20)
    return LetterData(
        xdata=np.concatenate(
            (
                [2.5, 3.5],
                1.75 + 1.75 * np.cos(theta),
                1.75 - 1.75 * np.cos(theta),
                [3.5, 1.5, 1.5, 2.5],
                1.75 + 0.75 * np.cos(theta),
                1.75 - 0.75 * np.cos(theta),
            )
        ),
        ydata=np.concatenate(
            (
                [5, 5],
                5.25 + 1.75 * np.sin(theta),
                1.75 - 1.75 * np.sin(theta),
                [3, 3, 2, 2],
                1.75 - 0.75 * np.sin(theta),
                5.25 + np.sin(theta),
            )
        ),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_h() -> LetterData:
    """Return data for letter H."""
    return LetterData(
        xdata=np.array([0, 1, 1, 2.5, 2.5, 3.5, 3.5, 2.5, 2.5, 1, 1, 0]),
        ydata=np.array([7, 7, 4, 4, 7, 7, 0, 0, 3, 3, 0, 0]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_i() -> LetterData:
    """Return data for letter I."""
    return LetterData(
        xdata=np.array([0, 3.5, 3.5, 2.25, 2.25, 3.5, 3.5, 0, 0, 1.25, 1.25, 0]),
        ydata=np.array([7, 7, 6, 6, 1, 1, 0, 0, 1, 1, 6, 6]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_j() -> LetterData:
    """Return data for letter J."""
    theta = np.linspace(0, np.pi, 20)
    return LetterData(
        xdata=np.concatenate(
            ([0, 1], 1.75 - 0.75 * np.cos(theta), [2.5, 3.5], 1.75 + 1.75 * np.cos(theta))
        ),
        ydata=np.concatenate(
            ([2, 2], 1.75 - 0.75 * np.sin(theta), [7, 7], 1.75 - 1.75 * np.sin(theta))
        ),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_k() -> LetterData:
    """Return data for letter K."""
    return LetterData(
        xdata=np.array([0, 0, 1, 1, 1.5, 2.5, 3.5, 13 / 6, 3.5, 2.5, 1, 1]),
        ydata=np.array([7, 0, 0, 2.625, 3.5, 0, 0, 14 / 3, 7, 7, 4.375, 7]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_l() -> LetterData:
    """Return data for letter L."""
    return LetterData(
        xdata=np.array([0, 0, 3.5, 3.5, 1, 1]),
        ydata=np.array([7, 0, 0, 1, 1, 7]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_m() -> LetterData:
    """Return data for letter M."""
    return LetterData(
        xdata=np.array([0, 0, 1, 1, 1.75, 2.5, 2.5, 3.5, 3.5, 2.5, 1.75, 1]),
        ydata=np.array([7, 0, 0, 4, 1.75, 4, 0, 0, 7, 7, 4.75, 7]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_n() -> LetterData:
    """Return data for letter N."""
    return LetterData(
        xdata=np.array([0, 1, 2.5, 2.5, 3.5, 3.5, 2.5, 1, 1, 0]),
        ydata=np.array([7, 7, 2.8, 7, 7, 0, 0, 4.2, 0, 0]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_o() -> LetterData:
    """Return data for letter O."""
    theta = np.linspace(0, 2 * np.pi, 40)
    xdata = np.concatenate((1.75 * np.sin(theta), -0.75 * np.sin(theta)))
    ydata = np.concatenate((3.5 * np.cos(theta), 2.5 * np.cos(theta)))
    return LetterData(
        xdata=xdata,
        ydata=ydata,
        xcenter=0,
        ycenter=0,
        xdata_plot=(xdata[:40], xdata[40:]),
        ydata_plot=(ydata[:40], ydata[40:]),
    )


def capital_p() -> LetterData:
    """Return data for letter P."""
    theta = np.linspace(np.pi / 2, -np.pi / 2, 20)
    xdata = np.concatenate(([1, 0, 0], 1.5 + 2 * np.cos(theta), [1, 1], 1.5 + np.cos(theta), [1]))
    ydata = np.concatenate(([0, 0, 7], 5 + 2 * np.sin(theta), [3, 4], 5 - np.sin(theta), [6]))
    return LetterData(
        xdata=xdata,
        ydata=ydata,
        xcenter=1.75,
        ycenter=3.5,
        xdata_plot=(xdata[:24], xdata[24:]),
        ydata_plot=(ydata[:24], ydata[24:]),
    )


def capital_q() -> LetterData:
    """Return data for letter Q."""
    theta1 = np.linspace(
        -np.arcsin(1 / np.sqrt(41)) - np.arctan(4 / 5),
        2 * np.pi - np.arcsin(23 * np.sqrt(41) / 287) - np.arctan(4 / 5),
        40,
    )
    theta2 = np.linspace(
        2 * np.pi - np.arcsin(23 / np.sqrt(769)) - np.arctan(12 / 25),
        -np.arcsin(7 / np.sqrt(769)) - np.arctan(12 / 25),
        40,
    )
    xdata = np.concatenate((1.75 * np.cos(theta1), [0.75, 1.75, 0.5, -0.5], 0.75 * np.cos(theta2)))
    ydata = np.concatenate((3.5 * np.sin(theta1), [-3.5, -3.5, -1.5, -1.5], 2.5 * np.sin(theta2)))
    return LetterData(
        xdata=xdata,
        ydata=ydata,
        xcenter=0,
        ycenter=0,
        xdata_plot=(xdata[:42], xdata[42:]),
        ydata_plot=(ydata[:42], ydata[42:]),
    )


def capital_r() -> LetterData:
    """Return data for letter R."""
    theta1 = np.linspace(0, np.pi - np.arcsin(np.sqrt(10) / 20) - np.arctan(1 / 3), 20)
    theta2 = np.linspace(0, np.pi, 20)
    xdata = np.concatenate(
        ([1, 0, 0, 1], 1.5 + 2 * np.sin(theta1), [3.5, 2.5, 1.5, 1, 1], 1.5 + np.sin(theta2), [1])
    )
    ydata = np.concatenate(
        ([0, 0, 7, 7], 5 + 2 * np.cos(theta1), [0, 0, 3, 3, 4], 5 - np.cos(theta2), [6])
    )
    return LetterData(
        xdata=xdata,
        ydata=ydata,
        xcenter=1.75,
        ycenter=3.5,
        xdata_plot=(xdata[:28], xdata[28:]),
        ydata_plot=(ydata[:28], ydata[28:]),
    )


def capital_s() -> LetterData:
    """Return data for letter S."""
    theta = np.linspace(0, np.arcsin(5 / 7) + np.pi, 20)
    return LetterData(
        xdata=np.concatenate(
            (
                0.75 * np.cos(theta),
                -1.75 * np.cos(np.flip(theta)),
                -0.75 * np.cos(theta),
                1.75 * np.cos(np.flip(theta)),
            )
        ),
        ydata=np.concatenate(
            (
                1.75 + 0.75 * np.sin(theta),
                -1.75 - 1.75 * np.sin(np.flip(theta)),
                -1.75 - 0.75 * np.sin(theta),
                1.75 + 1.75 * np.sin(np.flip(theta)),
            )
        ),
        xcenter=0,
        ycenter=0,
    )


def capital_t() -> LetterData:
    """Return data for letter T."""
    return LetterData(
        xdata=np.array([0, 3.5, 3.5, 2.25, 2.25, 1.25, 1.25, 0]),
        ydata=np.array([7, 7, 6, 6, 0, 0, 6, 6]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_u() -> LetterData:
    """Return data for letter U."""
    theta1 = np.linspace(0, np.pi, 20)
    theta2 = np.linspace(0, np.arcsin(3 / 7) + np.pi / 2, 20)
    return LetterData(
        xdata=np.concatenate(
            (
                [0.75, 1.75, 1.75, 0.75],
                0.75 * np.cos(theta1),
                [-0.75, -1.75],
                -1.75 * np.cos(theta2),
            )
        ),
        ydata=np.concatenate(
            ([0, 0, 7, 7], 1.75 - 0.75 * np.sin(theta1), [7, 7], 1.75 - 1.75 * np.sin(theta2))
        ),
        xcenter=0,
        ycenter=3.5,
    )


def capital_v() -> LetterData:
    """Return data for letter V."""
    return LetterData(
        xdata=np.array([0, 1.25, 2.25, 3.5, 2.5, 1.75, 1]),
        ydata=np.array([7, 0, 0, 7, 7, 2.8, 7]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_w() -> LetterData:
    """Return data for letter W."""
    return LetterData(
        xdata=np.array([0, 0, 1, 1.75, 2.5, 3.5, 3.5, 2.5, 2.5, 1.75, 1, 1]),
        ydata=np.array([7, 0, 0, 2.25, 0, 0, 7, 7, 3, 5.25, 3, 7]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_x() -> LetterData:
    """Return data for letter X."""
    return LetterData(
        xdata=np.array([3.5, 2.5, 1.75, 1, 0, 1.25, 0, 1, 1.75, 2.5, 3.5, 2.25]),
        ydata=np.array([7, 7, 4.9, 7, 7, 3.5, 0, 0, 2.1, 0, 0, 3.5]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_y() -> LetterData:
    """Return data for letter Y."""
    return LetterData(
        xdata=np.array([0, 1.25, 1.25, 2.25, 2.25, 3.5, 2.5, 1.75, 1]),
        ydata=np.array([7, 3, 0, 0, 3, 7, 7, 4.6, 7]),
        xcenter=1.75,
        ycenter=3.5,
    )


def capital_z() -> LetterData:
    """Return data for letter Z."""
    return LetterData(
        xdata=np.array([0, 0, 2.5, 0, 0, 3.5, 3.5, 1, 3.5, 3.5]),
        ydata=np.array([7, 6, 6, 1, 0, 0, 1, 1, 6, 7]),
        xcenter=1.75,
        ycenter=3.5,
    )
