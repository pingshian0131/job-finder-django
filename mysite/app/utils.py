def salary_range_validator(value: str) -> None:
    """
    Validate the salary range format.
    Expected format: "min_salary~max_salary"
    """
    if not value:
        raise ValueError("salary_range cannot be empty")
    parts = value.split("~")
    if len(parts) != 2:
        if value != "面議":
            raise ValueError(
                "salary_range must be in the format 'min_salary~max_salary'"
            )

    try:
        min_salary = int(parts[0])
        max_salary = int(parts[1])
        if min_salary > max_salary:
            raise ValueError("salary_range min cannot be greater than max")
    except ValueError:
        raise ValueError("salary_range must contain valid numeric values")
