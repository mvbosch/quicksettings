from dataclasses import fields, is_dataclass
from datetime import date
from types import GenericAlias, UnionType
from typing import get_args, get_origin, Any
from inspect import isclass


def validate_types(
    value: Any, expected_type: GenericAlias, class_name: str, field_name: str
) -> Any:
    """Recursively validate that the value matches the expected type."""

    origin = get_origin(expected_type)
    if origin is list:
        if not isinstance(value, list):
            raise TypeError(
                f"Invalid type for {class_name}.{field_name}\n\tExpected list, got {type(value).__name__}"
            )
        item_type = get_args(expected_type)[0]
        return [
            validate_types(
                value=item,
                expected_type=item_type,
                class_name=class_name,
                field_name=field_name,
            )
            for item in value
        ]
    elif origin is dict:
        if not isinstance(value, dict):
            raise TypeError(
                f"Invalid type for {class_name}.{field_name}\n\tExpected dict, got {type(value).__name__}"
            )
        key_type, value_type = get_args(expected_type)
        return {
            validate_types(
                value=k,
                expected_type=key_type,
                class_name=class_name,
                field_name=field_name,
            ): validate_types(
                value=v,
                expected_type=value_type,
                class_name=class_name,
                field_name=field_name,
            )
            for k, v in value.items()
        }
    elif is_dataclass(expected_type):
        if not isinstance(value, dict):
            raise TypeError(
                f"Invalid type for {class_name}.{field_name}\n\tExpected dict, got {type(value).__name__}"
            )
        return instantiate_dataclass(expected_type, value)
    else:
        if not isinstance(value, expected_type):  # type: ignore[arg-type]
            raise TypeError(
                f"Invalid type for {class_name}.{field_name}\n\t"
                f"Expected {expected_type}, got {type(value).__name__}"
            )
        return value


def cast_value(value: Any, target_type: Any) -> Any:
    if target_type == date and isinstance(value, str):
        return date.fromisoformat(value)
    if target_type in (int, float, str):
        return target_type(value)
    elif is_dataclass(target_type):
        return instantiate_dataclass(target_type, value)  # type: ignore[arg-type]
    elif get_origin(target_type) is list:
        item_type = get_args(target_type)[0]
        return [cast_value(item, item_type) for item in value]
    else:
        return value


def instantiate_dataclass(cls: type[Any], data: dict) -> Any:
    if not is_dataclass(cls) or not isclass(cls):
        raise ValueError(f"{cls} is not a dataclass")

    init_values = {}

    for field in fields(cls):
        field_value = data.get(field.name)

        if field_value is not None:
            init_values[field.name] = cast_value(field_value, field.type)
        elif field_value is None and is_optional(field.type):
            init_values[field.name] = None
        else:
            raise TypeError(f"Field {field.name} is missing from the input data")

    return cls(**init_values)


def is_optional(t: type[Any] | str | Any) -> bool:
    origin = get_origin(t)
    return origin is UnionType and type(None) in get_args(t)
