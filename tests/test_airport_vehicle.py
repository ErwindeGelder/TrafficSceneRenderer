"""Scripts for testing airport_vehicle.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest

from traffic_scene_renderer import AirportVehicle, AirportVehicleOptions, PathFollower

from .test_static_objects import save_fig

mpl.use("Agg")


def test_airport_vehicle_creation() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-4, 4)
    AirportVehicle(axes)
    save_fig(fig, axes, Path("airport_vehicle") / "standard_airport_vehicle.png", 5)


def test_airport_vehicle_with_trailers() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-3, 3)
    axes.set_ylim(-10, 4)
    AirportVehicle(axes, AirportVehicleOptions(n_trailers=2))
    save_fig(fig, axes, Path("airport_vehicle") / "airport_vehicle_with_trailers.png", 6)


def test_airport_vehicle_change_pos() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-4, 4)
    axes.set_ylim(-4, 4)
    vehicle = AirportVehicle(axes, AirportVehicleOptions(n_trailers=1))
    vehicle.change_pos(1, 2, np.pi / 2)
    save_fig(fig, axes, Path("airport_vehicle") / "airport_vehicle_change_pos.png", 8)


def test_airport_vehicle_move_vehicle() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-4, 4)
    axes.set_ylim(-2, 12)
    path_follower = PathFollower(np.array([0, 0]), np.array([0, 10]))
    vehicle = AirportVehicle(axes, AirportVehicleOptions(n_trailers=1), path_follower=path_follower)
    vehicle.move_vehicle(vehicle.options.length)
    assert vehicle.get_rear_y() == pytest.approx(vehicle.options.length)
    trailer_a, trailer_b = vehicle.trailers
    assert trailer_a.get_rear_y() < vehicle.get_rear_y()
    assert trailer_b.get_rear_y() < trailer_a.get_rear_y()
    save_fig(fig, axes, Path("airport_vehicle") / "airport_vehicle_moved.png", 8)


def test_airport_vehicle_different_colors() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-12, 12)
    axes.set_ylim(-4, 4)
    vehicle = AirportVehicle(axes, AirportVehicleOptions(color=(0.8, 0, 0)))
    vehicle.change_pos(-8, 0)
    vehicle = AirportVehicle(axes, AirportVehicleOptions(color=(0, 0.8, 0)))
    vehicle.change_pos(0, 0)
    vehicle = AirportVehicle(axes, AirportVehicleOptions(color=(0, 0, 0.8), color3=(0.2, 0.2, 0.2)))
    vehicle.change_pos(8, 0)
    save_fig(fig, axes, Path("airport_vehicle") / "airport_vehicle_different_colors.png", 24)


def test_airport_vehicle_with_path_follower() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 8)
    axes.set_ylim(-4, 14)
    x_path, y_path = np.array([0, 0, 1, 3, 23]), np.array([0, 2, 5, 7, 27])
    path_follower = PathFollower(x_path, y_path)
    vehicle = AirportVehicle(axes, AirportVehicleOptions(n_trailers=3), path_follower=path_follower)
    for _ in range(50):
        vehicle.move_vehicle(0.2)
    axes.plot(x_path, y_path, color="black", linewidth=0.5)
    save_fig(fig, axes, Path("airport_vehicle") / "airport_vehicle_with_path_follower.png", 8)
