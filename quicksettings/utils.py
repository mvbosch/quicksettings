from types import GenericAlias
from typing import get_args, get_origin, Any


def validate_types(
    value: Any, expected_type: GenericAlias, class_name: str, field_name: str
) -> None:
    """Recursively validate that the value matches the expected type."""

    origin = get_origin(expected_type)
    if origin is list:
        if not isinstance(value, list):
            raise TypeError(
                f"Invalid type for {class_name}.{field_name}\n\tExpected list, got {type(value).__name__}"
            )
        item_type = get_args(expected_type)[0]
        for item in value:
            validate_types(
                value=item,
                expected_type=item_type,
                class_name=class_name,
                field_name=field_name,
            )
    elif origin is dict:
        if not isinstance(value, dict):
            raise TypeError(
                f"Invalid type for {class_name}.{field_name}\n\tExpected dict, got {type(value).__name__}"
            )
        key_type, value_type = get_args(expected_type)
        for k, v in value.items():
            validate_types(
                value=k,
                expected_type=key_type,
                class_name=class_name,
                field_name=field_name,
            )
            validate_types(
                value=v,
                expected_type=value_type,
                class_name=class_name,
                field_name=field_name,
            )
    else:
        if not isinstance(value, expected_type):  # type: ignore[arg-type]
            raise TypeError(
                f"Invalid type for {class_name}.{field_name}\n\t"
                f"Expected {expected_type}, got {type(value).__name__}"
            )
