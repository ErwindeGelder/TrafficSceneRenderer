""" This file contains some simple functions that are useful but too small to have an own file.

Author(s): Erwin de Gelder
"""

from typing import Tuple
import utm              # Installation required (pip install utm)
import numpy as np


def wgs_to_utm(points_wgs: np.ndarray, force_zone_number: int = None) \
        -> Tuple[np.ndarray, int, str]:
    """ Convert WGS coordinates to UTM coordinates, such that zone is similar.

    :param points_wgs: N-by-2 array containing N lat-lon coordinates.
    :param force_zone_number: Zone number to be used. Set to none if zone number needs to be
                              determined by first datapoint (default: None).
    :return: A tuple with a N-by-2 array containing N easting-northing coordinates, an integer
             of the zone used for transformation, and the character of the zone.
    """

    n_points = points_wgs.shape[0]
    points_utm = np.empty((n_points, 2))
    zone_char = 'U'  # Make sure it is defined

    for i in range(0, n_points):
        point_utm = utm.from_latlon(points_wgs[i, 0], points_wgs[i, 1],
                                    force_zone_number=force_zone_number)
        points_utm[i, 0] = point_utm[0]
        points_utm[i, 1] = point_utm[1]
        if i == 0:
            force_zone_number = point_utm[2]
            zone_char = point_utm[3]

    return points_utm, force_zone_number, zone_char


def rotate(x_data: np.ndarray, y_data: np.ndarray, angle: float) -> Tuple[np.ndarray, np.ndarray]:
    """ Rotate the (x,y)-data around the origin by a specified angle.

    :param x_data: The x-coordinates of the data.
    :param y_data: The y-coordinates of the data.
    :param angle: The rotation angle.
    :return: A tuple containing the x-coordinates and the y-coordinates of the rotated data.
    """
    x_new = np.cos(angle) * x_data - np.sin(angle) * y_data
    y_new = np.sin(angle) * x_data + np.cos(angle) * y_data
    return x_new, y_new


def set_options(default: dict, options: dict) -> dict:
    """ Set options or keep default options if option is not specified.

    :param default: The default options.
    :param options: The set options. Can be None, in that case, default is returned.
    :return: All options.
    """
    if options is not None:
        for key, value in options.items():
            if key in default:
                default[key] = value
            else:
                raise KeyError("Option '{:s}' not defined for this object.".format(key))
    return default


def rgb2hsl(red: float, green: float, blue: float) -> Tuple[float, float, float]:
    """ Convert RGB color format to HSL color format.

    :param red: Red content (value from 0 to 1).
    :param green: Green content (value from 0 to 1).
    :param blue: Blue content (value from 0 to 1).
    :return: Tuple with Hue, Saturation, and Luminance (values from 0 to 1).
    """
    cmax = max(red, green, blue)
    cmin = min(red, green, blue)
    delta = cmax - cmin

    if delta == 0.0:
        hue = 0.0
    elif cmax == red:
        hue = (green - blue) / (6*delta) % 1
    elif cmax == green:
        hue = ((blue - red) / (2*delta) + 1) / 3
    else:
        hue = ((red - green) / (2*delta) + 2) / 3

    luminance = (cmax + cmin) / 2

    if delta == 0.0:
        saturation = 0.0
    else:
        saturation = delta / (1 - abs(2*luminance - 1))

    return hue, saturation, luminance


def hsl2rgb(hue: float, saturation: float, luminance: float) -> Tuple[float, float, float]:
    """ Convert HSL color format to RGB color format.

    :param hue: Hue value (value from 0 to 1).
    :param saturation: Saturation value (value from 0 to 1).
    :param luminance: Luminance value (value from 0 to 1).
    :return: Tuple with red, green, and blue content (values from 0 to 1).
    """
    first_color = (1 - abs(2*luminance - 1)) * saturation
    second_color = first_color * (1 - abs((6*hue % 2) - 1))
    mean_color = luminance - first_color/2

    if hue < 1/6:
        red, green, blue = first_color, second_color, 0.0
    elif hue < 1/3:
        red, green, blue = second_color, first_color, 0.0
    elif hue < 1/2:
        red, green, blue = 0.0, first_color, second_color
    elif hue < 2/3:
        red, green, blue = 0.0, second_color, first_color
    elif hue < 5/6:
        red, green, blue = second_color, 0.0, first_color
    else:
        red, green, blue = first_color, 0.0, second_color

    red += mean_color
    green += mean_color
    blue += mean_color
    return red, green, blue
