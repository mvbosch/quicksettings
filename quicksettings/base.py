import os
from ast import literal_eval
from dataclasses import MISSING, InitVar, dataclass, fields
from typing import get_origin

from quicksettings.utils import validate_types


@dataclass(init=False)
class BaseSettings:
    """Base settings class."""

    def __init__(self):
        required_missing = []
        for field_ in fields(self):
            if field_.name.startswith("_"):
                continue
            raw_value = os.getenv(f"{self._env_prefix}{field_.name}", field_.default)
            if raw_value is MISSING:
                required_missing.append(field_.name)

            if field_.type is bool:
                lowstr_value = os.getenv(
                    f"{self._env_prefix}{field_.name}", str(field_.default)
                ).lower()
                if lowstr_value in self._true_bool_values:
                    value = True
                elif lowstr_value in self._false_bool_values:
                    value = False
                else:
                    raise ValueError(
                        f"Invalid value for {self.__class__.__name__}.{field_.name}\n\t"
                        f"`{raw_value}` is not a valid boolean value"
                    )
            elif field_.type in (str, int, float):
                try:
                    value = field_.type(raw_value)
                except ValueError as e:
                    raise ValueError(
                        f"Invalid value for {self.__class__.__name__}.{field_.name}\n\t"
                        f"`{raw_value}` cannot be cast to type `{field_.type.__name__}`"
                    ) from e
            elif isinstance(raw_value, str) and get_origin(field_.type) in (list, dict):
                value = literal_eval(raw_value.strip(" \n"))
                validate_types(
                    value=value,
                    expected_type=field_.type,
                    class_name=self.__class__.__name__,
                    field_name=field_.name,
                )
            else:
                value = MISSING
            setattr(self, field_.name, value)

        if required_missing:
            raise ValueError(
                f"Missing required field for {self.__class__.__name__}:\n\t"
                + "\n\t".join(required_missing)
            )

    _env_prefix: InitVar[str] = ""
    _true_bool_values: InitVar[tuple] = ("true", "1", "yes", "y", "t")
    _false_bool_values: InitVar[tuple] = ("false", "0", "no", "n", "f")
