"""Arrow to indicate direction of an object.

Author(s): Erwin de Gelder
"""

from typing import Any, List, Union

import numpy as np
from matplotlib.axes import Axes

SVD_TOL = 0.001


def arrow(
    axes: Axes,
    xdata: Union[List, np.ndarray],
    ydata: Union[List, np.ndarray],
    size: float = 0.75,
    **kwargs: Any,  # noqa: ANN401  # Ignore because otherwise mypy will complain.
) -> None:
    """Draw an arrow on the axes.

    If only 2 coordinates are provided, the arrow will be a straight line.
    If 4 coordinates are provided, 2 straight lines are drawn based on the first two
    coordinates and the last 2 coordinates. These straight lines are connected using
    an ellipsoid. Obviously, this only works if these lines can be connected using
    an ellipsoid.
    If 4 coordinates are provided with 2 straight parallel lines, they are connected
    using a sinusoid.
    If more coordinates are given, a line is simply drawn through these coordinates.

    :param axes: The axes that is used for plotting.
    :param xdata: The x values of the coordinates.
    :param ydata: The y values of the coordinates.
    :param size: The size of the arrow.
    :param kwargs: Additional plotting parameters.
    """
    # Draw the arrow
    if len(xdata) == 4:  # noqa: PLR2004
        # Find center of ellipse
        matrix = np.array(
            [[ydata[1] - ydata[0], ydata[2] - ydata[3]], [xdata[0] - xdata[1], xdata[3] - xdata[2]]]
        )
        if np.linalg.svd(matrix)[1][-1] > SVD_TOL:
            xy_ellipse = compute_ellipse(xdata, ydata)
            axes.plot(
                np.concatenate(([xdata[0]], xy_ellipse[0], [xdata[3]])),
                np.concatenate(([ydata[0]], xy_ellipse[1], [ydata[3]])),
                **kwargs,
            )
        else:  # Almost singular, so connect with sinusoid.
            xy_sinus = compute_sinus(xdata, ydata)
            axes.plot(
                np.concatenate(([xdata[0]], xy_sinus[0] + xdata[1], [xdata[3]])),
                np.concatenate(([ydata[0]], xy_sinus[1] + ydata[1], [ydata[3]])),
                **kwargs,
            )
    else:
        axes.plot(xdata, ydata, **kwargs)

    # Draw the tip of the arrow
    theta = np.arctan2(xdata[-1] - xdata[-2], ydata[-1] - ydata[-2])
    rotation_mat = np.array([[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]])
    xydata = np.array([[-size, 0, size], [-size, 0, -size]])
    xydata = np.dot(rotation_mat, xydata)
    axes.plot(xdata[-1] + xydata[0], ydata[-1] + xydata[1], **kwargs)


def compute_ellipse(xdata: Union[List, np.ndarray], ydata: Union[List, np.ndarray]) -> np.ndarray:
    """Compute an ellipse connecting the four points.

    :param xdata: The x values of the coordinates.
    :param ydata: The y values of the coordinates.
    :return: The (x,y) data of the ellipse.
    """
    matrix = np.array(
        [[ydata[1] - ydata[0], ydata[2] - ydata[3]], [xdata[0] - xdata[1], xdata[3] - xdata[2]]]
    )
    vector = np.array([xdata[2] - xdata[1], ydata[2] - ydata[1]])
    solution = np.linalg.solve(matrix, vector)
    center = np.array(
        [xdata[1] + matrix[0, 0] * solution[0], ydata[1] + matrix[1, 0] * solution[0]]
    )
    matrix_transform = np.array(
        [[xdata[2] - center[0], xdata[1] - center[0]], [ydata[2] - center[1], ydata[1] - center[1]]]
    )
    xy_transformed = np.array(
        [np.sin(np.linspace(0, np.pi / 2, 20)), np.cos(np.linspace(0, np.pi / 2, 20))]
    )
    xy_ellipse = np.dot(matrix_transform, xy_transformed)
    xy_ellipse[0] += center[0]
    xy_ellipse[1] += center[1]
    return xy_ellipse


def compute_sinus(xdata: Union[List, np.ndarray], ydata: Union[List, np.ndarray]) -> np.ndarray:
    """Compute a sinus connecting the four points.

    :param xdata: The x values of the coordinates.
    :param ydata: The y values of the coordinates.
    :return: The (x,y) data of the sinus.
    """
    matrix = np.array(
        [[xdata[1] - xdata[0], ydata[2] - ydata[3]], [ydata[1] - ydata[0], xdata[3] - xdata[2]]]
    )
    vector = np.array([xdata[2] - xdata[1], ydata[2] - ydata[1]])
    solution = np.linalg.solve(matrix, vector)
    lateral = np.cos(np.linspace(-np.pi, 0, 20)) / 2 + 0.5
    longitudinal = np.linspace(0, 1, 20)
    return np.array(
        [
            longitudinal * solution[0] * matrix[0, 0] + lateral * solution[1] * matrix[0, 1],
            longitudinal * solution[0] * matrix[1, 0] + lateral * solution[1] * matrix[1, 1],
        ]
    )
