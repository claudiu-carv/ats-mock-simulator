import re
import json
from typing import Dict, Any, List, Union
from pydantic import BaseModel, ValidationError as PydanticValidationError
from email_validator import validate_email, EmailNotValidError
from backend.models import FieldValidation, ValidationError, ValidationResult


class RequestValidator:
    """Validates incoming requests against defined schemas."""

    def __init__(self):
        pass

    def validate_request(
        self, data: Dict[str, Any], validations: List[FieldValidation]
    ) -> ValidationResult:
        """
        Validate request data against field validation rules.

        Args:
            data: The incoming request data
            validations: List of field validation rules

        Returns:
            ValidationResult with validation status and any errors
        """
        errors = []

        for validation in validations:
            field_name = validation.field_name
            field_type = validation.field_type
            required = validation.required

            # Check if field exists
            if field_name not in data:
                if required:
                    errors.append(
                        ValidationError(
                            field=field_name, message="Field is required", value=None
                        )
                    )
                continue

            value = data[field_name]

            # Skip validation for None values if field is not required
            if value is None and not required:
                continue

            # Validate field type and constraints
            field_errors = self._validate_field(
                field_name=field_name, value=value, validation=validation
            )
            errors.extend(field_errors)

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def _validate_field(
        self, field_name: str, value: Any, validation: FieldValidation
    ) -> List[ValidationError]:
        """Validate a single field against its validation rules."""
        errors = []
        field_type = validation.field_type

        try:
            # Type validation and conversion
            if field_type == "string":
                if not isinstance(value, str):
                    value = str(value)
                errors.extend(self._validate_string(field_name, value, validation))

            elif field_type == "int":
                if not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        errors.append(
                            ValidationError(
                                field=field_name,
                                message="Value must be an integer",
                                value=value,
                            )
                        )
                        return errors
                errors.extend(self._validate_numeric(field_name, value, validation))

            elif field_type == "float":
                if not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        errors.append(
                            ValidationError(
                                field=field_name,
                                message="Value must be a number",
                                value=value,
                            )
                        )
                        return errors
                errors.extend(self._validate_numeric(field_name, value, validation))

            elif field_type == "bool":
                if not isinstance(value, bool):
                    if isinstance(value, str):
                        if value.lower() in ("true", "1", "yes", "on"):
                            value = True
                        elif value.lower() in ("false", "0", "no", "off"):
                            value = False
                        else:
                            errors.append(
                                ValidationError(
                                    field=field_name,
                                    message="Value must be a boolean",
                                    value=value,
                                )
                            )
                    else:
                        errors.append(
                            ValidationError(
                                field=field_name,
                                message="Value must be a boolean",
                                value=value,
                            )
                        )

            elif field_type == "email":
                if not isinstance(value, str):
                    value = str(value)
                errors.extend(self._validate_email(field_name, value))

            else:
                errors.append(
                    ValidationError(
                        field=field_name,
                        message=f"Unknown field type: {field_type}",
                        value=value,
                    )
                )

        except Exception as e:
            errors.append(
                ValidationError(
                    field=field_name, message=f"Validation error: {str(e)}", value=value
                )
            )

        return errors

    def _validate_string(
        self, field_name: str, value: str, validation: FieldValidation
    ) -> List[ValidationError]:
        """Validate string field constraints."""
        errors = []

        # Length validation
        if validation.min_length is not None and len(value) < validation.min_length:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value must be at least {validation.min_length} characters long",
                    value=value,
                )
            )

        if validation.max_length is not None and len(value) > validation.max_length:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value must be no more than {validation.max_length} characters long",
                    value=value,
                )
            )

        # Pattern validation
        if validation.pattern:
            try:
                if not re.match(validation.pattern, value):
                    errors.append(
                        ValidationError(
                            field=field_name,
                            message=f"Value does not match required pattern: {validation.pattern}",
                            value=value,
                        )
                    )
            except re.error:
                errors.append(
                    ValidationError(
                        field=field_name,
                        message=f"Invalid regex pattern: {validation.pattern}",
                        value=value,
                    )
                )

        # Choices validation
        if validation.choices and value not in validation.choices:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value must be one of: {', '.join(validation.choices)}",
                    value=value,
                )
            )

        return errors

    def _validate_numeric(
        self, field_name: str, value: Union[int, float], validation: FieldValidation
    ) -> List[ValidationError]:
        """Validate numeric field constraints."""
        errors = []

        if validation.min_value is not None and value < validation.min_value:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value must be at least {validation.min_value}",
                    value=value,
                )
            )

        if validation.max_value is not None and value > validation.max_value:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value must be no more than {validation.max_value}",
                    value=value,
                )
            )

        return errors

    def _validate_email(self, field_name: str, value: str) -> List[ValidationError]:
        """Validate email format."""
        errors = []

        try:
            validate_email(value)
        except EmailNotValidError:
            errors.append(
                ValidationError(
                    field=field_name, message="Invalid email format", value=value
                )
            )

        return errors

    @staticmethod
    def parse_validations(validations_json: str) -> List[FieldValidation]:
        """Parse validation rules from JSON string."""
        try:
            validations_data = json.loads(validations_json)
            return [FieldValidation(**validation) for validation in validations_data]
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in validations: {str(e)}")
        except Exception as e:
            raise ValueError(f"Invalid validation format: {str(e)}")

    @staticmethod
    def serialize_validations(validations: List[FieldValidation]) -> str:
        """Serialize validation rules to JSON string."""
        return json.dumps([validation.dict() for validation in validations], indent=2)
