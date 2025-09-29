import json
import yaml
from typing import Dict, Any, List, Optional, Tuple
from openapi_spec_validator import validate_spec
try:
    from backend.models import (
        EndpointCreate, RequestSchemaCreate, ResponseTemplateCreate,
        FieldValidation
    )
except ImportError:
    from models import (
        EndpointCreate, RequestSchemaCreate, ResponseTemplateCreate,
        FieldValidation
    )


class OpenAPIImporter:
    """Converts OpenAPI specs to ATS Mock API endpoints, schemas, and templates."""

    def __init__(self):
        self.type_mapping = {
            'string': 'string',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'string',  # Simplified for now
            'object': 'string'  # Simplified for now
        }

    def import_spec(self, spec_content: str, spec_format: str = 'auto') -> Dict[str, Any]:
        """Import OpenAPI spec and return structured data for endpoint creation."""

        # Parse spec (YAML or JSON)
        if spec_format == 'auto':
            spec_format = self._detect_format(spec_content)

        if spec_format == 'yaml':
            spec_data = yaml.safe_load(spec_content)
        else:
            spec_data = json.loads(spec_content)

        # Validate OpenAPI spec
        validate_spec(spec_data)

        # Extract endpoints, schemas, and generate templates
        results = {
            'endpoints': [],
            'total_endpoints': 0,
            'errors': [],
            'warnings': []
        }

        paths = spec_data.get('paths', {})

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    try:
                        endpoint_data = self._convert_operation_to_endpoint(
                            path, method.upper(), operation, spec_data
                        )
                        results['endpoints'].append(endpoint_data)
                        results['total_endpoints'] += 1
                    except Exception as e:
                        results['errors'].append(f"Error processing {method.upper()} {path}: {str(e)}")

        return results

    def _convert_operation_to_endpoint(
        self, path: str, method: str, operation: Dict[str, Any], spec_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert OpenAPI operation to endpoint with schema and templates."""

        # Create endpoint
        endpoint = EndpointCreate(
            path=path,
            method=method,
            name=operation.get('summary', f"{method} {path}"),
            description=operation.get('description', ''),
            is_active=True
        )

        # Generate request schema for all methods (parameters for GET/DELETE, requestBody for others)
        schema = self._generate_request_schema(operation, spec_data, method)

        # Generate response templates
        templates = self._generate_response_templates(operation, spec_data)

        return {
            'endpoint': endpoint,
            'schema': schema,
            'templates': templates
        }

    def _generate_request_schema(
        self, operation: Dict[str, Any], spec_data: Dict[str, Any], method: str
    ) -> Optional[RequestSchemaCreate]:
        """Generate request schema from OpenAPI requestBody or parameters."""

        validations = []

        # Handle request body for POST/PUT/PATCH methods
        if method in ['POST', 'PUT', 'PATCH']:
            request_body = operation.get('requestBody')
            if request_body:
                # Resolve $ref if present in requestBody
                if '$ref' in request_body:
                    request_body = self._resolve_ref(request_body['$ref'], spec_data)

                if request_body:
                    content = request_body.get('content', {})
                    json_content = content.get('application/json')

                    if not json_content or 'schema' not in json_content:
                        # Try form data as fallback
                        form_content = content.get('application/x-www-form-urlencoded')
                        if form_content and 'schema' in form_content:
                            json_content = form_content

                    if json_content and 'schema' in json_content:
                        schema_def = json_content['schema']

                        # Resolve $ref if present in schema
                        if '$ref' in schema_def:
                            schema_def = self._resolve_ref(schema_def['$ref'], spec_data)

                        if schema_def:
                            validations.extend(self._convert_schema_to_validations(schema_def, spec_data))

        # Handle parameters for all methods (query, path, header parameters)
        parameters = operation.get('parameters', [])
        if parameters:
            param_validations = self._convert_parameters_to_validations(parameters, spec_data)
            validations.extend(param_validations)

        # Only create schema if we have validations
        if not validations:
            return None

        schema_name = operation.get('operationId', 'OpenAPI Schema')
        return RequestSchemaCreate(
            name=f"{schema_name} Schema",
            validations=json.dumps([v.dict() for v in validations]),
            is_default=True
        )

    def _convert_schema_to_validations(
        self, schema: Dict[str, Any], spec_data: Dict[str, Any], required_fields: List[str] = None
    ) -> List[FieldValidation]:
        """Convert OpenAPI schema to FieldValidation objects."""

        validations = []
        required_fields = required_fields or schema.get('required', [])

        # Resolve $ref if present
        if '$ref' in schema:
            schema = self._resolve_ref(schema['$ref'], spec_data)
            if not schema:
                return validations

        # Handle different schema types
        schema_type = schema.get('type', 'object')

        if schema_type == 'object':
            properties = schema.get('properties', {})

            for field_name, field_schema in properties.items():
                # Resolve $ref if present in field schema
                if '$ref' in field_schema:
                    resolved_field_schema = self._resolve_ref(field_schema['$ref'], spec_data)
                    if resolved_field_schema:
                        field_schema = resolved_field_schema

                field_type = field_schema.get('type', 'string')

                # Enhanced type mapping
                if field_type == 'string' and field_schema.get('format') == 'email':
                    mapped_type = 'email'
                elif field_type == 'string' and field_schema.get('format') in ['date', 'date-time']:
                    mapped_type = 'string'  # Keep as string but with pattern validation
                elif field_type == 'array':
                    mapped_type = 'string'  # Simplified for validation purposes
                elif field_type == 'object':
                    mapped_type = 'string'  # Simplified for validation purposes
                else:
                    mapped_type = self.type_mapping.get(field_type, 'string')

                validation = FieldValidation(
                    field_name=field_name,
                    field_type=mapped_type,
                    required=field_name in required_fields,
                    min_length=field_schema.get('minLength'),
                    max_length=field_schema.get('maxLength'),
                    min_value=field_schema.get('minimum'),
                    max_value=field_schema.get('maximum'),
                    pattern=field_schema.get('pattern'),
                    choices=field_schema.get('enum')
                )

                validations.append(validation)

        elif schema_type == 'array':
            # For array schemas at the root level, create a validation for the array itself
            items_schema = schema.get('items', {})
            if items_schema:
                # For arrays, we'll create a generic array validation
                validation = FieldValidation(
                    field_name='items',
                    field_type='string',  # Simplified
                    required=True,
                    min_length=schema.get('minItems'),
                    max_length=schema.get('maxItems')
                )
                validations.append(validation)

        # If it's a simple type schema (not object/array), create a single validation
        elif schema_type in ['string', 'integer', 'number', 'boolean']:
            validation = FieldValidation(
                field_name='value',
                field_type=self.type_mapping.get(schema_type, 'string'),
                required=True,
                min_length=schema.get('minLength'),
                max_length=schema.get('maxLength'),
                min_value=schema.get('minimum'),
                max_value=schema.get('maximum'),
                pattern=schema.get('pattern'),
                choices=schema.get('enum')
            )
            validations.append(validation)

        return validations

    def _convert_parameters_to_validations(
        self, parameters: List[Dict[str, Any]], spec_data: Dict[str, Any]
    ) -> List[FieldValidation]:
        """Convert OpenAPI parameters to FieldValidation objects."""

        validations = []

        for param in parameters:
            # Resolve $ref if present
            if '$ref' in param:
                resolved_param = self._resolve_ref(param['$ref'], spec_data)
                if not resolved_param:
                    continue
                param = resolved_param

            param_name = param.get('name')
            param_in = param.get('in')  # query, path, header, cookie
            param_schema = param.get('schema', {})
            required = param.get('required', False)

            if not param_name:
                continue

            # Skip certain headers and path parameters that aren't typically user input
            if param_in == 'header' and param_name.lower().startswith('x-'):
                continue
            if param_in == 'path':
                # Path parameters are typically part of URL structure, not user input validation
                continue

            # Focus on query parameters and relevant headers
            if param_in not in ['query', 'header']:
                continue

            # Map parameter schema to validation
            param_type = param_schema.get('type', 'string')
            mapped_type = self.type_mapping.get(param_type, 'string')

            validation = FieldValidation(
                field_name=param_name,
                field_type=mapped_type,
                required=required,
                min_length=param_schema.get('minLength'),
                max_length=param_schema.get('maxLength'),
                min_value=param_schema.get('minimum'),
                max_value=param_schema.get('maximum'),
                pattern=param_schema.get('pattern'),
                choices=param_schema.get('enum')
            )

            validations.append(validation)

        return validations

    def _generate_response_templates(
        self, operation: Dict[str, Any], spec_data: Dict[str, Any]
    ) -> List[ResponseTemplateCreate]:
        """Generate response templates from OpenAPI responses."""

        templates = []
        responses = operation.get('responses', {})

        # Track if we have a default template
        has_default = False

        for status_code, response_def in responses.items():
            # Resolve $ref if present in response definition
            if '$ref' in response_def:
                response_def = self._resolve_ref(response_def['$ref'], spec_data)
                if not response_def:
                    continue

            if status_code.startswith('2') and not has_default:  # First success response becomes default
                template = self._create_response_template(
                    status_code, response_def, spec_data, True
                )
                if template:
                    templates.append(template)
                    has_default = True
            elif status_code.startswith('2') or status_code.startswith('4') or status_code.startswith('5'):  # Success/error responses
                template = self._create_response_template(
                    status_code, response_def, spec_data, False
                )
                if template:
                    templates.append(template)

        return templates

    def _create_response_template(
        self, status_code: str, response_def: Dict[str, Any],
        spec_data: Dict[str, Any], is_default: bool
    ) -> Optional[ResponseTemplateCreate]:
        """Create a response template from OpenAPI response definition."""

        content = response_def.get('content', {})
        json_content = content.get('application/json')

        if json_content and 'schema' in json_content:
            # Use the schema to generate template
            schema_def = json_content['schema']
            # Resolve $ref if present in schema
            if '$ref' in schema_def:
                schema_def = self._resolve_ref(schema_def['$ref'], spec_data)

            if schema_def:
                template_json = self._generate_mock_template_from_schema(schema_def, spec_data)
            else:
                template_json = self._get_fallback_template(status_code)
        else:
            # Create a fallback template based on status code and response description
            template_json = self._get_fallback_template(status_code, response_def.get('description', ''))

        return ResponseTemplateCreate(
            name=f"HTTP_{status_code}",
            template=json.dumps(template_json, indent=2),
            status_code=int(status_code),
            content_type="application/json",
            is_default=is_default
        )

    def _get_fallback_template(self, status_code: str, description: str = '') -> Dict[str, Any]:
        """Generate a fallback template when no schema is available."""

        if status_code.startswith('2'):
            # Success response template
            template = {
                "status_code": int(status_code),
                "status": "OK",
                "service": "${mock.string[5-10]}",
                "resource": "${mock.string[8-15]}",
                "operation": "${mock.string[6-12]}",
                "data": {}
            }

            # Add common success fields based on status code
            if status_code == '200':
                template["data"] = {
                    "id": "${mock.uuid}",
                    "created_at": "${mock.date.now}",
                    "updated_at": "${mock.date.now}"
                }
            elif status_code == '201':
                template["data"] = {
                    "id": "${mock.uuid}",
                    "created_at": "${mock.date.now}"
                }
            elif status_code == '204':
                # No content
                return {}

        else:
            # Error response template
            template = {
                "status_code": int(status_code),
                "error": True,
                "message": description or f"HTTP {status_code} Error",
                "detail": "${mock.string[20-50]}",
                "timestamp": "${mock.timestamp}"
            }

            # Add error-specific fields
            if status_code == '400':
                template["type"] = "BadRequestError"
                template["validation_errors"] = [
                    {
                        "field": "${mock.string[5-10]}",
                        "message": "${mock.string[10-30]}"
                    }
                ]
            elif status_code == '401':
                template["type"] = "UnauthorizedError"
            elif status_code == '404':
                template["type"] = "NotFoundError"
            elif status_code == '422':
                template["type"] = "ValidationError"

        return template

    def _generate_mock_template_from_schema(
        self, schema: Dict[str, Any], spec_data: Dict[str, Any], visited_refs: set = None
    ) -> Dict[str, Any]:
        """Generate a mock template with placeholders from OpenAPI schema."""

        if visited_refs is None:
            visited_refs = set()

        # Resolve $ref if present
        if '$ref' in schema:
            # Prevent circular references
            if schema['$ref'] in visited_refs:
                return {"_circular_ref": schema['$ref']}
            visited_refs.add(schema['$ref'])
            schema = self._resolve_ref(schema['$ref'], spec_data)
            if not schema:  # If reference couldn't be resolved
                return {"_unresolved_ref": "Schema reference could not be resolved"}

        schema_type = schema.get('type', 'object')

        if schema_type == 'object':
            return self._generate_object_template(schema, spec_data, visited_refs)
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            item_template = self._generate_mock_template_from_schema(items_schema, spec_data, visited_refs.copy())
            return [item_template]  # Return array with single item as example
        else:
            return self._generate_primitive_template(schema)

    def _generate_object_template(
        self, schema: Dict[str, Any], spec_data: Dict[str, Any], visited_refs: set = None
    ) -> Dict[str, Any]:
        """Generate object template with mock placeholders."""

        if visited_refs is None:
            visited_refs = set()

        template = {}
        properties = schema.get('properties', {})

        for prop_name, prop_schema in properties.items():
            if '$ref' in prop_schema:
                # Prevent circular references
                if prop_schema['$ref'] in visited_refs:
                    template[prop_name] = {"_circular_ref": prop_schema['$ref']}
                    continue
                visited_refs.add(prop_schema['$ref'])
                resolved_schema = self._resolve_ref(prop_schema['$ref'], spec_data)
                if not resolved_schema:
                    template[prop_name] = {"_unresolved_ref": prop_schema['$ref']}
                    continue
                prop_schema = resolved_schema

            prop_type = prop_schema.get('type', 'string')

            if prop_type == 'object':
                template[prop_name] = self._generate_object_template(prop_schema, spec_data, visited_refs.copy())
            elif prop_type == 'array':
                items_schema = prop_schema.get('items', {})
                item_template = self._generate_mock_template_from_schema(items_schema, spec_data, visited_refs.copy())
                template[prop_name] = [item_template]
            else:
                template[prop_name] = self._generate_primitive_placeholder(prop_name, prop_schema)

        return template

    def _generate_primitive_placeholder(
        self, field_name: str, schema: Dict[str, Any]
    ) -> str:
        """Generate appropriate mock placeholder for primitive types."""

        field_type = schema.get('type', 'string')
        field_format = schema.get('format')
        field_name_lower = field_name.lower()

        # Check if this might be a request field
        common_request_fields = ['name', 'email', 'phone', 'description', 'title', 'message']
        if any(req_field in field_name_lower for req_field in common_request_fields):
            return f"${{request.{field_name}}}"

        # Generate appropriate mock placeholder
        if field_type == 'string':
            if field_format == 'email' or 'email' in field_name_lower:
                if any(req_field in field_name_lower for req_field in ['email']):
                    return f"${{request.{field_name}}}"
                return "${mock.email}"
            elif field_format == 'date-time' or any(date_word in field_name_lower for date_word in ['date', 'created', 'updated', 'time']):
                return "${mock.date.now}"
            elif field_format == 'date':
                return "${mock.date}"
            elif field_format == 'time':
                return "${mock.time}"
            elif 'name' in field_name_lower:
                return f"${{request.{field_name}}}"
            elif 'phone' in field_name_lower:
                return f"${{request.{field_name}}}"
            elif any(id_word in field_name_lower for id_word in ['id', 'uuid']):
                return "${mock.uuid}"
            elif any(url_word in field_name_lower for url_word in ['url', 'link', 'href']):
                return "${mock.url}"
            elif 'price' in field_name_lower or 'cost' in field_name_lower:
                return "${mock.currency}"
            elif 'category' in field_name_lower or 'type' in field_name_lower or 'status' in field_name_lower:
                return f"${{mock.string[8-15]}}"
            elif schema.get('enum'):
                enum_values = ','.join(str(v) for v in schema['enum'])
                return f"${{mock.enum[{enum_values}]}}"
            else:
                min_len = schema.get('minLength', 5)
                max_len = schema.get('maxLength', 20)
                return f"${{mock.string[{min_len}-{max_len}]}}"

        elif field_type == 'integer':
            if 'id' in field_name_lower:
                return "${mock.id}"
            elif 'count' in field_name_lower or 'total' in field_name_lower:
                return "${mock.int[1-100]}"
            elif 'price' in field_name_lower or 'cost' in field_name_lower:
                return "${mock.int[1-10000]}"
            else:
                min_val = schema.get('minimum', 1)
                max_val = schema.get('maximum', 1000)
                return f"${{mock.int[{min_val}-{max_val}]}}"

        elif field_type == 'number':
            if 'price' in field_name_lower or 'cost' in field_name_lower:
                return "${mock.float[1.00-999.99]}"
            else:
                min_val = schema.get('minimum', 0.1)
                max_val = schema.get('maximum', 100.0)
                return f"${{mock.float[{min_val}-{max_val}]}}"

        elif field_type == 'boolean':
            return "${mock.bool}"

        else:
            return "${mock.string[10-30]}"

    def _generate_primitive_template(self, schema: Dict[str, Any]) -> str:
        """Generate primitive template for non-object schemas."""
        field_type = schema.get('type', 'string')

        if field_type == 'string':
            if schema.get('enum'):
                enum_values = ','.join(str(v) for v in schema['enum'])
                return f"${{mock.enum[{enum_values}]}}"
            else:
                min_len = schema.get('minLength', 5)
                max_len = schema.get('maxLength', 20)
                return f"${{mock.string[{min_len}-{max_len}]}}"
        elif field_type == 'integer':
            min_val = schema.get('minimum', 1)
            max_val = schema.get('maximum', 1000)
            return f"${{mock.int[{min_val}-{max_val}]}}"
        elif field_type == 'number':
            min_val = schema.get('minimum', 0.1)
            max_val = schema.get('maximum', 100.0)
            return f"${{mock.float[{min_val}-{max_val}]}}"
        elif field_type == 'boolean':
            return "${mock.bool}"
        else:
            return "${mock.string[10-30]}"

    def _resolve_ref(self, ref: str, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve OpenAPI $ref reference."""

        # Handle #/components/schemas/ModelName format
        if ref.startswith('#/'):
            path_parts = ref[2:].split('/')
            current = spec_data

            for part in path_parts:
                if not isinstance(current, dict) or part not in current:
                    # Return empty dict if path doesn't exist
                    return {}
                current = current[part]

            return current if isinstance(current, dict) else {}

        return {}

    def _detect_format(self, content: str) -> str:
        """Detect if content is YAML or JSON."""
        content = content.strip()

        if content.startswith('{'):
            return 'json'
        else:
            return 'yaml'