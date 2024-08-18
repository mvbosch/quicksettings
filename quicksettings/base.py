import os
from ast import literal_eval
from dataclasses import MISSING, InitVar, dataclass, fields
from typing import get_origin

from quicksettings.utils import validate_types


@dataclass(init=False)
class BaseSettings:
    """Base settings class."""

    _env_prefix: InitVar[str]

    def __init__(self) -> None:
        true_bool_values = ("true", "1", "yes", "y", "t")
        false_bool_values = ("false", "0", "no", "n", "f")
        required_missing = []
        env_prefix = self._env_prefix if hasattr(self, "_env_prefix") else ""

        for field_ in fields(self):
            if field_.name.startswith("_"):
                continue
            raw_value = os.getenv(f"{env_prefix}{field_.name}", field_.default)
            if raw_value is MISSING:
                required_missing.append(field_.name)

            if field_.type is bool:
                lowstr_value = os.getenv(
                    f"{env_prefix}{field_.name}", str(field_.default)
                ).lower()
                if lowstr_value in true_bool_values:
                    value = True
                elif lowstr_value in false_bool_values:
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
                    expected_type=field_.type,  # type: ignore[arg-type]
                    class_name=self.__class__.__name__,
                    field_name=field_.name,
                )
            else:
                raise TypeError(
                    f"Invalid type for {self.__class__.__name__}.{field_.name}\n\t"
                    f"Expected {field_.type.__name__}, got {type(raw_value).__name__}"
                )
            setattr(self, field_.name, value)

        if required_missing:
            raise ValueError(
                f"Missing required field for {self.__class__.__name__}:\n\t"
                + "\n\t".join(required_missing)
            )
