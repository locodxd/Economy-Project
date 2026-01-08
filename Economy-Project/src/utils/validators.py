from typing import Any

def validate_positive_integer(value: Any) -> bool:
    """Validate that the input is a positive integer."""
    if isinstance(value, int) and value > 0:
        return True
    return False

def validate_non_empty_string(value: Any) -> bool:
    """Validate that the input is a non-empty string."""
    return isinstance(value, str) and bool(value.strip())

def validate_user_id(value: Any) -> bool:
    """Validate that the input is a valid user ID (positive integer)."""
    return validate_positive_integer(value)

def validate_amount(value: Any) -> bool:
    """Validate that the input is a valid amount (positive integer)."""
    return validate_positive_integer(value)

def validate_job_name(value: Any) -> bool:
    """Validate that the job name is a non-empty string."""
    return validate_non_empty_string(value)

def validate_item_name(value: Any) -> bool:
    """Validate that the item name is a non-empty string."""
    return validate_non_empty_string(value)