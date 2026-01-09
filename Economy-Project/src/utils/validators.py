from typing import Any

def validate_positive_integer(value: Any) -> bool:
    if isinstance(value, int) and value > 0:
        return True
    return False

def validate_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def validate_user_id(value: Any) -> bool:
    return validate_positive_integer(value)

def validate_amount(value: Any) -> bool:
    return validate_positive_integer(value)

def validate_job_name(value: Any) -> bool:
    return validate_non_empty_string(value)

def validate_item_name(value: Any) -> bool:
    return validate_non_empty_string(value)