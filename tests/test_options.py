"""Scripts for testing options.py.

Author(s): Erwin de Gelder
"""

import pytest

from traffic_scene_renderer import FrozenOptionsError, Options, UnknownOptionError


class OptionsTest(Options):
    """Class to test the functionality of Options."""

    test: bool = True


def test_normal_functionality_options() -> None:
    my_options = OptionsTest(test=False)

    # We can add an option when we unfreeze the object
    my_options.unfreeze()
    my_options.test = False


def test_unknown_option_error() -> None:
    # Create an Options object and try to add an option that is not valid.
    try:
        Options(test=True)
    except UnknownOptionError:
        pass
    else:
        pytest.fail("UnknownOptionError should be raised.")


def test_frozen_options_error() -> None:
    # Create an Options object and then try to add an option that is not valid.
    my_options = OptionsTest()
    try:
        my_options.test_me_too = True
    except FrozenOptionsError:
        pass
    else:
        pytest.fail("FrozenOptionsError should be raised.")
