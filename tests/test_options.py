"""Scripts for testing options.py.

Author(s): Erwin de Gelder
"""

import contextlib

from traffic_scene_renderer.options import FrozenOptionsError, Options, UnknownOptionError


class OptionsTest(Options):
    """Class to test the functionality of Options."""

    test: bool = True


def test_options() -> None:
    """Test the normal functionality of Options."""
    # Create object with no options
    my_options = OptionsTest(test=False)

    # We can add an option when we unfreeze the object
    my_options.unfreeze()
    my_options.test = False


def test_unknown_option_error() -> None:
    """Test whether the UnknownOptionError is being raised.

    Create an object and try to add an option that is not valid.
    This should raise an UnknownOptionError.
    """
    with contextlib.suppress(UnknownOptionError):
        Options(test=True)


def test_frozen_options_error() -> None:
    """Test whether the FrozenOptionsError is being raised.

    Create an object and then try to add an option that is not valid.
    This should raise an FrozenOptionsError.
    """
    my_options = OptionsTest()
    with contextlib.suppress(FrozenOptionsError):
        my_options.test_me_too = True
