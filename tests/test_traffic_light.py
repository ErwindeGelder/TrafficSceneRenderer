"""Scripts for testing traffic_light.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

from traffic_scene_renderer import (
    NoAmberError,
    TrafficLight,
    TrafficLightOptions,
    TrafficLightStatus,
)

from .test_static_objects import save_fig

mpl.use("Agg")


def test_traffic_light_creation() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-1, 1)
    axes.set_ylim(-2, 2)
    TrafficLight(axes, TrafficLightOptions(radius=0.5))
    save_fig(fig, axes, Path("traffic_light") / "idle.png", 4)


def test_traffic_light_without_amber() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-50, 50)  # Set large, in order to get a large traffic light.
    axes.set_ylim(-2, 2)
    TrafficLight(axes, TrafficLightOptions(amber=False))
    axes.set_xlim(-1, 1)
    save_fig(fig, axes, Path("traffic_light") / "no_amber.png", 4)


def test_traffic_light_status() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-4, 4)
    axes.set_ylim(-2, 2)
    traffic_light = TrafficLight(axes, TrafficLightOptions(radius=0.5))
    traffic_light.change_pos(-3, 0)
    traffic_light.set_status(TrafficLightStatus.IDLE)
    traffic_light = TrafficLight(axes, TrafficLightOptions(radius=0.5))
    traffic_light.change_pos(-1, 0)
    traffic_light.set_status(TrafficLightStatus.RED)
    traffic_light = TrafficLight(axes, TrafficLightOptions(radius=0.5))
    traffic_light.change_pos(1, 0)
    traffic_light.set_status(TrafficLightStatus.AMBER)
    traffic_light = TrafficLight(axes, TrafficLightOptions(radius=0.5))
    traffic_light.change_pos(3, 0)
    traffic_light.set_status(TrafficLightStatus.GREEN)
    traffic_light = TrafficLight(axes, TrafficLightOptions(radius=0.5))
    traffic_light.set_status(TrafficLightStatus.RED)
    traffic_light.set_status(TrafficLightStatus.REMOVED)
    save_fig(fig, axes, Path("traffic_light") / "different_status.png", 8)


def test_traffic_light_status_no_amber() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-2, 2)
    axes.set_ylim(-2, 2)
    traffic_light = TrafficLight(axes, TrafficLightOptions(radius=0.5, amber=False))
    traffic_light.change_pos(-1, 0)
    traffic_light.set_status(TrafficLightStatus.RED)
    traffic_light = TrafficLight(axes, TrafficLightOptions(radius=0.5, amber=False))
    traffic_light.change_pos(1, 0)
    traffic_light.set_status(TrafficLightStatus.GREEN)
    save_fig(fig, axes, Path("traffic_light") / "no_amber_status.png", 8)


def test_no_amber_error() -> None:
    fig, axes = plt.subplots()
    traffic_light = TrafficLight(axes, TrafficLightOptions(amber=False))
    try:
        traffic_light.set_status(TrafficLightStatus.AMBER)
    except NoAmberError:
        pass
    else:
        pytest.fail("NoAmberError should be raised.")
    plt.close(fig)


def test_str() -> None:
    fig, axes = plt.subplots()
    traffic_light = TrafficLight(axes)
    assert str(traffic_light) == "Traffic light, status=IDLE"
    traffic_light.set_status(TrafficLightStatus.REMOVED)
    assert str(traffic_light) == "Traffic light, status=REMOVED"
    traffic_light.set_status(TrafficLightStatus.RED)
    assert str(traffic_light) == "Traffic light, status=RED"
    traffic_light.set_status(TrafficLightStatus.AMBER)
    assert str(traffic_light) == "Traffic light, status=AMBER"
    traffic_light.set_status(TrafficLightStatus.GREEN)
    assert str(traffic_light) == "Traffic light, status=GREEN"
