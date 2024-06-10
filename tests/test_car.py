"""Scripts for testing car.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest

from traffic_scene_renderer import (
    Car,
    CarOptions,
    CarType,
    InvalidCarTypeError,
    MoveVehicleNoPathFollowerDefinedError,
    PathFollower,
)

from .test_static_objects import save_fig

mpl.use("Agg")


def test_car_creation_without_options() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-3, 3)
    axes.set_ylim(-3, 3)
    Car(axes)
    save_fig(fig, axes, Path("car") / "default_car.png", 3)


def test_cars_transparent() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-5, 5)
    axes.set_ylim(-3, 3)
    for i, car_type in enumerate(
        (CarType.VEHICLE, CarType.STATION_WAGON, CarType.PICKUP_TRUCK, CarType.SEDAN)
    ):
        car = Car(axes, CarOptions(fill=False, icar=car_type))
        car.change_pos(-3.75 + 2.5 * i, 0)
    save_fig(fig, axes, Path("car") / "transparent_cars.png", 5)


def test_invalid_car_type_error() -> None:
    fig, axes = plt.subplots()
    try:
        Car(axes, CarOptions(fill=False, icar=5))
    except InvalidCarTypeError:
        pass
    else:
        pytest.fail("InvalidCarTypeError should be raised.")
    finally:
        plt.close(fig)


def test_car_change_color() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-3, 3)
    axes.set_ylim(-3, 3)
    car = Car(axes)
    car.change_color(face_color=(1, 0, 0), edge_color=(0.4, 0, 0))
    save_fig(fig, axes, Path("car") / "red_car.png", 3)


def test_car_get_coordinates() -> None:
    fig, axes = plt.subplots()
    car = Car(axes, CarOptions(length=2))
    assert car.get_front_x() == 0.0
    assert car.get_front_y() == 1.0
    assert car.get_rear_x() == 0.0
    assert car.get_rear_y() == -1.0
    plt.close(fig)


def test_car_set_front_xy() -> None:
    fig, axes = plt.subplots()
    car = Car(axes, CarOptions(length=2))
    car.set_front_xy(1, 0, np.pi / 2)
    assert (car.get_front_x(), car.get_front_y()) == (1.0, 0.0)
    plt.close(fig)


def test_car_braking() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-3, 3)
    axes.set_ylim(-3, 3)
    car_braking = Car(axes)
    car_braking.change_pos(-1.5, 0)
    car_braking.start_braking()

    car_not_braking = Car(axes)
    car_not_braking.change_pos(1.5, 0)
    car_not_braking.start_braking()
    car_not_braking.stop_braking()

    axes.text(-1.5, 2.5, "Braking", horizontalalignment="center")
    axes.text(1.5, 2.5, "Not braking", horizontalalignment="center")
    save_fig(fig, axes, Path("car") / "braking_car.png", 3)


def test_move_vehicle_no_path_follower_defined_error() -> None:
    fig, axes = plt.subplots()
    car = Car(axes)
    try:
        car.move_vehicle(1)
    except MoveVehicleNoPathFollowerDefinedError:
        pass
    else:
        pytest.fail("MoveVehicleNoPathFollowerDefinedError should be raised.")
    finally:
        plt.close(fig)


def test_car_moving() -> None:
    fig, axes = plt.subplots()
    path_follower = PathFollower(np.array([0, 0]), np.array([0, 10]))
    car = Car(axes, path_follower=path_follower)
    car.move_vehicle(car.options.length)
    assert car.get_rear_y() == car.options.length
    plt.close(fig)
