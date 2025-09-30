import random
import re
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Union
from faker import Faker


class MockDataGenerator:
    def __init__(self):
        self.fake = Faker()

    def generate_int(self, length_spec: str = None) -> int:
        if length_spec:
            match = re.match(r"\[(\d+)-(\d+)\]", length_spec)
            if match:
                min_len, max_len = int(match.group(1)), int(match.group(2))
                return self.fake.random_int({min: min_len, max: max_len})
        return self.fake.random_int()

    def generate_string(self, length_spec: str = None) -> str:
        if length_spec:
            # Parse length specification like [6-10]
            match = re.match(r"\[(\d+)-(\d+)\]", length_spec)
            if match:
                min_len, max_len = int(match.group(1)), int(match.group(2))
                length = random.randint(min_len, max_len)
                return "".join(
                    random.choices(
                        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                        k=length,
                    )
                )

        return self.fake.text(max_nb_chars=20).replace("\n", " ").strip()

    def generate_date_now(self) -> str:
        return datetime.utcnow().isoformat()

    def generate_url(self) -> str:
        return self.fake.url()

    def generate_email(self) -> str:
        return self.fake.email()

    def generate_name(self) -> str:
        return self.fake.name()

    def generate_uuid(self) -> str:
        return str(uuid.uuid4())

    def generate_bool(self) -> bool:
        return random.choice([True, False])

    def generate_enum(self, choices_spec: str) -> str:
        # Parse choices like [val1,val2,val3]
        match = re.match(r"\[(.*?)\]", choices_spec)
        if match:
            choices = [choice.strip() for choice in match.group(1).split(",")]
            return random.choice(choices)
        return "unknown"

    def generate_timestamp(self) -> int:
        return int(datetime.utcnow().timestamp())

    def generate_phone(self) -> str:
        return self.fake.phone_number()


class TemplateEngine:
    def __init__(self):
        self.mock_generator = MockDataGenerator()
        # Pattern to match ${...} placeholders
        self.placeholder_pattern = re.compile(r"\$\{([^}]+)\}")

    def render(self, template: str, request_data: Dict[str, Any] = None) -> str:
        """
        Render a template string by replacing ${} placeholders with actual values.

        Supported placeholders:
        - ${request.field_name} - Value from request data
        - ${mock.int} - Random integer
        - ${mock.string[6-10]} - Random string with length 6-10
        - ${mock.date.now} - Current date ISO format
        - ${mock.email} - Random email
        - ${mock.name} - Random name
        - ${mock.uuid} - Random UUID
        - ${mock.bool} - Random boolean
        - ${mock.enum[val1,val2]} - Random choice from list
        - ${mock.timestamp} - Current timestamp
        - ${mock.phone} - Random phone number
        """
        if request_data is None:
            request_data = {}

        def replace_placeholder(match):
            placeholder = match.group(1)
            return self._resolve_placeholder(placeholder, request_data)

        # Replace all placeholders
        result = self.placeholder_pattern.sub(replace_placeholder, template)

        # Try to parse as JSON to validate structure
        try:
            json.loads(result)
        except json.JSONDecodeError:
            # If it's not valid JSON, return as-is (might be plain text)
            pass

        return result

    def _resolve_placeholder(
        self, placeholder: str, request_data: Dict[str, Any]
    ) -> str:
        """Resolve a single placeholder to its value."""

        if placeholder.startswith("request."):
            # Extract value from request data
            field_name = placeholder[8:]  # Remove 'request.' prefix
            value = self._get_nested_value(request_data, field_name)
            return str(value) if value is not None else ""

        elif placeholder.startswith("mock."):
            # Generate mock data
            mock_type = placeholder[5:]  # Remove 'mock.' prefix
            return str(self._generate_mock_value(mock_type))

        else:
            # Unknown placeholder type, return as-is
            return f"${{{placeholder}}}"

    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get a value from nested dictionary using dot notation."""
        keys = field_path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def _generate_mock_value(self, mock_type: str) -> Union[str, int, bool]:
        """Generate a mock value based on the mock type specification."""

        if mock_type == "int":
            length_match = re.search(r"\[(\d+-\d+)\]", mock_type)
            if length_match:
                return self.mock_generator.generate_int(f"[{length_match.group(1)}]")
            return self.mock_generator.generate_int()

        elif mock_type.startswith("string"):
            # Check for length specification
            length_match = re.search(r"\[(\d+-\d+)\]", mock_type)
            if length_match:
                return self.mock_generator.generate_string(f"[{length_match.group(1)}]")
            return self.mock_generator.generate_string()

        elif mock_type == "date.now":
            return self.mock_generator.generate_date_now()

        elif mock_type == "email":
            return self.mock_generator.generate_email()

        elif mock_type == "url":
            return self.mock_generator.generate_url()

        elif mock_type == "name":
            return self.mock_generator.generate_name()

        elif mock_type == "uuid":
            return self.mock_generator.generate_uuid()

        elif mock_type == "bool":
            return self.mock_generator.generate_bool()

        elif mock_type.startswith("enum"):
            # Extract choices from enum[val1,val2,val3]
            choices_match = re.search(r"enum(\[.*?\])", mock_type)
            if choices_match:
                return self.mock_generator.generate_enum(choices_match.group(1))
            return "unknown"

        elif mock_type == "timestamp":
            return self.mock_generator.generate_timestamp()

        elif mock_type == "phone":
            return self.mock_generator.generate_phone()

        else:
            # Unknown mock type
            return f"mock.{mock_type}"

    def validate_template(self, template: str) -> Dict[str, Any]:
        """
        Validate a template and return information about placeholders found.
        """
        placeholders = self.placeholder_pattern.findall(template)

        result = {
            "valid": True,
            "placeholders": placeholders,
            "request_fields": [],
            "mock_fields": [],
            "errors": [],
        }

        for placeholder in placeholders:
            if placeholder.startswith("request."):
                field_name = placeholder[8:]
                result["request_fields"].append(field_name)
            elif placeholder.startswith("mock."):
                mock_type = placeholder[5:]
                result["mock_fields"].append(mock_type)
            else:
                result["errors"].append(f"Unknown placeholder type: {placeholder}")
                result["valid"] = False

        # Try to parse template as JSON to validate structure
        try:
            # Create a test render with dummy data
            test_data = {}
            for field in result["request_fields"]:
                test_data[field] = "test_value"

            rendered = self.render(template, test_data)
            json.loads(rendered)
        except json.JSONDecodeError as e:
            result["errors"].append(f"Invalid JSON template: {str(e)}")
            result["valid"] = False
        except Exception as e:
            result["errors"].append(f"Template rendering error: {str(e)}")
            result["valid"] = False

        return result
