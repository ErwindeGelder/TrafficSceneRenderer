"""Scripts for testing truck.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from traffic_scene_renderer import PathFollower, Truck, TruckOptions
from traffic_scene_renderer.utilities import hsl2rgb

from .test_static_objects import save_fig

mpl.use("Agg")


def test_truck_creation() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-4, 4)
    Truck(axes)
    save_fig(fig, axes, Path("truck") / "standard_truck.png", 5)


def test_truck_braking() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-6, 4)
    truck = Truck(axes)
    truck.start_braking(3)
    save_fig(fig, axes, Path("truck") / "truck_braking.png", 5)


def test_truck_trailers() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-12, 4)
    for i in range(5):
        truck = Truck(axes, TruckOptions(trailer=True, l_trailer=4 + 1.5 * i))
        truck.change_color(face_color=hsl2rgb(i / 5, 0.8, 0.5))
        truck.change_pos(-7 + 3.5 * i, 0)
    save_fig(fig, axes, Path("truck") / "truck_trailers.png", 10)


def test_change_trailer_angle() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 4)
    axes.set_ylim(-3, 5)
    truck = Truck(axes, TruckOptions(trailer=True))
    truck.change_pos(0, 0, np.pi / 2)
    truck.change_trailer_angle(np.pi / 12)
    save_fig(fig, axes, Path("truck") / "truck_trailer_angle.png", 14)


def test_airport_vehicle_with_path_follower() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 8)
    axes.set_ylim(-4, 14)
    x_path, y_path = np.array([0, 0, 1, 3, 23]), np.array([0, 2, 5, 7, 27])
    path_follower = PathFollower(x_path, y_path)
    vehicle = Truck(axes, TruckOptions(trailer=True), path_follower=path_follower)
    for _ in range(50):
        vehicle.move_vehicle(0.2)
    axes.plot(x_path, y_path, color="black", linewidth=0.5)
    save_fig(fig, axes, Path("truck") / "truck_with_path_follower.png", 8)
