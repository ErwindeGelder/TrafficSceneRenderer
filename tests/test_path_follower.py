"""Scripts for testing path_follower.py.

Author(s): Erwin de Gelder
"""

import numpy as np
import pytest

from traffic_scene_renderer import PathFollower
from traffic_scene_renderer.path_follower import PathFollowerLengthNotSetError

XDATA = np.array([0.0, 0.0, 5.0, 5.0, 5.1, 5.1, 5.2, 5.2, 20.0])
YDATA = np.array([0.0, 5.0, 5.0, 4.9, 4.9, 4.8, 4.8, 4.7, 4.7])


def test_path_follower_creation() -> None:
    PathFollower(XDATA, YDATA, 1)


def test_path_follower_start_at_1m() -> None:
    # Let's start with lambda=0.2, meaning at (0.0, 1.0)
    path_follower = PathFollower(XDATA, YDATA, 1, (0, 0.2))
    assert path_follower.get_rear_xy() == (0.0, 1.0)


def test_path_follower_location_front() -> None:
    path_follower = PathFollower(XDATA, YDATA, 2)
    assert path_follower.get_location_front() == (1, 0.4)  # 40% of first segment


def test_path_follower_front_xy() -> None:
    path_follower = PathFollower(XDATA, YDATA, 5)
    assert path_follower.get_front_xy() == (0.0, 5.0)


def test_path_follower_move_4m() -> None:
    path_follower = PathFollower(XDATA, YDATA, np.sqrt(2))
    path_follower.move_vehicle(4)
    assert path_follower.get_center_coordinates() == pytest.approx((0.5, 4.5, np.pi / 4))
    path_follower.move_vehicle(2)
    assert path_follower.get_rear_xy() == pytest.approx((1.0, 5.0))
    path_follower.move_vehicle(5)
    assert path_follower.get_rear_xy() == pytest.approx((5.7, 4.7))


def test_path_follower_length_not_set_error() -> None:
    path_follower = PathFollower(XDATA, YDATA)
    try:
        path_follower.get_front_xy()
    except PathFollowerLengthNotSetError:
        pass
    else:
        pytest.fail("PathFollowerLengthNotSetError should be raised.")
