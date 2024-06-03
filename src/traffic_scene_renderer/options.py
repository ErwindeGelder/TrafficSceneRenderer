"""Class that does not allow for creating new attributes.

Author(s): Erwin de Gelder
"""

from typing import Any


class UnknownOptionError(Exception):
    """Error to be raised in case an unknown options would be used."""

    def __init__(self, key: str) -> None:
        """Description of error.

        :param key: The name of the options that is invalid.
        """
        super().__init__(f"Option '{key:s}' is not a valid option.")


class Options:
    """Contain options of objects.

    The goal of this class is to create objects that does not allow for creating
    new attributes. In this way, this cannot be done accidentily, as this can
    generally cause very weird errors.
    """

    __isfrozen = False

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401  # Allow Any
        """Create class for dealing with options.

        :param kwargs: define all options that need to be set.
        """
        for key, value in kwargs.items():
            try:
                self.__getattribute__(key)
            except AttributeError as attr_err:
                raise UnknownOptionError(key) from attr_err
            self.__setattr__(key, value)

        # Make sure that no new attributes are created outside the __init__ function.
        self.freeze()

    def __setattr__(self, key: str, value: Any) -> None:  # noqa: ANN401  # Allow Any
        """Set the attribute of this object.

        :param key: Name of the attribute to be set.
        :param value: Value of the attribute to be set.
        """
        if self.__isfrozen and not hasattr(self, key):
            raise FrozenOptionsError(self)
        object.__setattr__(self, key, value)

    def freeze(self) -> None:
        """Freeze the attributes, meaning that it is not possible to add attributes."""
        self.__isfrozen = True

    def unfreeze(self) -> None:
        """Unfreeze the attributes, meaning that it is possible to add attributes."""
        self.__isfrozen = False


class FrozenOptionsError(Exception):
    """Error to be raised when an option is being added while Options is in frozen mode."""

    def __init__(self, options: Options) -> None:
        """Description of error.

        :param options: Options for which another options is being added.
        """
        super().__init__(f"{options} is a frozen class")
