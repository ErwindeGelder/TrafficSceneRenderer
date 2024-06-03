"""Scripts for testing options.py.

Author(s): Erwin de Gelder
"""

from traffic_scene_renderer.options import Options, UnknownOptionError, FrozenOptionsError


class OptionsTest(Options):
    """Class to test the functionality of Options."""
    test: bool = True


def test_options():
    """Test the normal functionality of Options."""
    # Create object with no options
    my_options = OptionsTest(test=False)

    # We can add an option when we unfreeze the object
    my_options.unfreeze()
    my_options.test = "hi world"


def test_unknown_option_error():
    """Test whether the UnknownOptionError is being raised.

    Create an object and try to add an option that is not valid.
    This should raise an UnknownOptionError.
    """
    try:
        my_options = Options(test=True)
    except UnknownOptionError:
        pass


def test_frozen_options_error():
    """Test whether the FrozenOptionsError is being raised.

    Create an object and then try to add an option that is not valid.
    This should raise an FrozenOptionsError.
    """
    my_options = OptionsTest()
    try:
        my_options.test_me_too = True
    except FrozenOptionsError:
        pass
