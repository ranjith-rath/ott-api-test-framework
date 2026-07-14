"""Helper for validating API responses against JSON schema contracts."""

import json
from pathlib import Path

from jsonschema import validate, ValidationError

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def validate_schema(payload: dict, schema_filename: str) -> None:
    """Validate a response payload against a named schema file.

    Raises:
        AssertionError: with a readable message if validation fails.
    """
    schema_path = SCHEMA_DIR / schema_filename
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        validate(instance=payload, schema=schema)
    except ValidationError as exc:
        raise AssertionError(
            f"Schema validation failed for {schema_filename}: {exc.message}"
        ) from exc
