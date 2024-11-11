import os
from ast import literal_eval
from dataclasses import MISSING, InitVar, dataclass, fields
from enum import Enum
from typing import Literal, get_origin, get_args
from types import UnionType

from quicksettings.utils import validate_types


@dataclass(init=False)
class BaseSettings:
    """Base settings class."""

    env_prefix: InitVar[str]

    def __init__(self) -> None:
        true_bool_values = ("true", "1", "yes", "y", "t")
        false_bool_values = ("false", "0", "no", "n", "f")
        required_missing: list[str] = []
        validation_errors: list[str] = []
        env_prefix = self.env_prefix if hasattr(self, "env_prefix") else ""

        for field_ in fields(self):
            if field_.name.startswith("_"):
                continue

            if isinstance(field_.type, str):
                raise ValueError(
                    f"Invalid type hint for {self.__class__.__name__}.{field_.name}\n\t"
                    f"Forward references are not supported"
                )

            origin, origin_args = get_origin(field_.type), get_args(field_.type)
            field_required = origin is not UnionType and type(None) not in origin_args
            value = (
                field_.default_factory()
                if field_.default_factory is not MISSING
                else MISSING
            )
            raw_value = os.getenv(f"{env_prefix}{field_.name}", field_.default)
            if value is not MISSING and raw_value is MISSING:
                raw_value = value

            if field_required and raw_value is MISSING:
                value = MISSING
                required_missing.append(field_.name)
            elif not field_required and raw_value is MISSING:
                value = None
            elif field_.type is bool:
                lowstr_value = os.getenv(
                    f"{env_prefix}{field_.name}", str(field_.default)
                ).lower()
                if lowstr_value in true_bool_values:
                    value = True
                elif lowstr_value in false_bool_values:
                    value = False
                else:
                    validation_errors.append(
                        f"Invalid value for {self.__class__.__name__}.{field_.name}\n\t"
                        f"`{raw_value}` is not a valid boolean value"
                    )
            elif field_.type is str:
                value = str(raw_value)
            elif origin is Literal:
                if raw_value not in origin_args:
                    validation_errors.append(
                        f"Invalid value for {self.__class__.__name__}.{field_.name}\n\t"
                        f"`{raw_value}` is not a valid option"
                    )
                value = raw_value
            elif field_.type in (int, float) or issubclass(field_.type, Enum):  # type: ignore[arg-type]
                try:
                    value = field_.type(raw_value)
                except ValueError:
                    validation_errors.append(
                        f"Invalid value for {self.__class__.__name__}.{field_.name}\n\t"
                        f"`{raw_value}` cannot be cast to type `{field_.type.__name__}`"
                    )
            elif isinstance(raw_value, str) and origin in (list, dict):
                value = literal_eval(raw_value.strip(" \n"))
                validate_types(
                    value=value,
                    expected_type=field_.type,  # type: ignore[arg-type]
                    class_name=self.__class__.__name__,
                    field_name=field_.name,
                )

            setattr(self, field_.name, value)

        if required_missing:
            validation_errors.append(
                f"Missing required field for {self.__class__.__name__}:\n\t"
                + "\n\t".join(required_missing)
            )

        if validation_errors:
            raise ValueError("\n".join(validation_errors))
