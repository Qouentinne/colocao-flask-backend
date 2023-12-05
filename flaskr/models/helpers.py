from typing import Literal


def convert_unit_in_days(frequency_number: int, frequency_unit: Literal["day", "week", "month"]):
    match frequency_unit:
        case "day":
            return frequency_number
        case "week":
            return frequency_number * 7
        case "month":
            return frequency_number * 30
    raise ValueError(f"Unknown frequency_unit {frequency_unit}")
         