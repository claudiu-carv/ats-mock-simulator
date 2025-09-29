# ATS Mock API Server

A Python-based application that simulates an ATS (Applicant Tracking System) integration, acting as a mock API server with dynamic URL configuration, request validation, and templated responses.

## Features

- **Dynamic Endpoints**: Create and manage API endpoints through a web interface
- **Request Schema Validation**: Define validation rules for incoming requests
- **Template Engine**: Powerful response templates with mock data generation
- **Force Response Templates**: Override default responses using `X-Force-Response` header for testing
- **OpenAPI Import**: Import existing OpenAPI specifications to automatically generate endpoints
- **Web Dashboard**: React-based UI for configuration management
- **SQLite Database**: Persistent storage for configurations
- **Mock Data Generation**: Rich set of mock data generators for realistic responses

## Tech Stack

- **Backend**: FastAPI with SQLModel/Pydantic
- **Frontend**: React with TailwindCSS
- **Database**: SQLite
- **Mock Data**: Faker library
- **Template Engine**: Custom implementation with Jinja2-like syntax

## Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm/yarn

### Backend Setup

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:

   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install Node.js dependencies & Start:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The web interface will be available at `http://localhost:3000`

## 📖 Usage

### 1. Create an Endpoint

1. Open the web dashboard at `http://localhost:3000`
2. Click "New Endpoint"
3. Fill in the endpoint details:
   - **Name**: Human-readable name
   - **Path**: URL path (e.g., `/webhook/candidate`)
   - **Method**: HTTP method (GET, POST, PUT, DELETE, PATCH)
   - **Description**: Optional description

### 2. Define Request Schema

1. Go to the endpoint detail page
2. Click "Add Schema" in the Request Schemas section
3. Define validation rules for each field:
   - **Field Name**: The parameter name
   - **Type**: string, int, float, bool, email
   - **Required**: Whether the field is mandatory
   - **Constraints**: Length limits, value ranges, patterns, choices

### 3. Create Response Template

1. In the endpoint detail page, click "Add Template"
2. Design your JSON response template using placeholders:
   - `${request.field_name}` - Values from incoming request
   - `${mock.uuid}` - Random UUID
   - `${mock.int}` - Random integer
   - `${mock.int[1-100]}` - Random integer in range
   - `${mock.float[1.00-999.99]}` - Random float in range
   - `${mock.string[6-10]}` - Random string with length 6-10
   - `${mock.email}` - Random email
   - `${mock.name}` - Random name
   - `${mock.date.now}` - Current date
   - `${mock.date}` - Random past date
   - `${mock.time}` - Random time
   - `${mock.timestamp}` - Current timestamp
   - `${mock.phone}` - Random phone number
   - `${mock.url}` - Random URL
   - `${mock.currency}` - Random currency amount
   - `${mock.id}` - Random ID number
   - `${mock.bool}` - Random boolean
   - `${mock.enum[val1,val2,val3]}` - Random choice from list

### 4. Import from OpenAPI Specification

You can quickly create multiple endpoints by importing an OpenAPI specification file:

1. In the web dashboard, click "Import OpenAPI"
2. Upload a YAML or JSON OpenAPI specification file
3. Review the detected endpoints and their configurations
4. Click "Import Endpoints" to create them automatically

The importer will:

- Create endpoints for each path/method combination
- Generate request schemas from parameter and request body definitions
- Create response templates with appropriate mock data placeholders
- Handle various OpenAPI features like enums, format specifications, and validation rules

#### Supported OpenAPI Features

The OpenAPI importer supports:

- **HTTP Methods**: GET, POST, PUT, DELETE, PATCH
- **Path Parameters**: Automatically creates request schema fields
- **Request Bodies**: JSON schema converted to validation rules
- **Response Schemas**: Auto-generates response templates with appropriate mock data
- **Data Types**: string, integer, number, boolean, array, object
- **Format Specifications**: email, date, date-time, uri, uuid
- **Validation Rules**: minLength, maxLength, minimum, maximum, enum values
- **Nested Objects**: Flattens complex schemas into manageable templates

#### OpenAPI File Requirements

- **Format**: YAML (.yml, .yaml) or JSON (.json) files
- **Version**: OpenAPI 3.0.x specifications
- **Structure**: Must include `paths` section with operation definitions
- **Content-Type**: Request/response content types should be `application/json`

### 5. Test Your Endpoint

Once configured, your endpoint will be available at: `http://localhost:8000/your/endpoint/path`

Example request:

```bash
curl -X POST http://localhost:8000/webhook/candidate \\
  -H "Content-Type: application/json" \\
  -d '{"email": "john@example.com", "name": "John Doe"}'
```

### 6. Force Specific Response Templates

You can override the default response template by using the `X-Force-Response` header. This is useful for testing different scenarios and error conditions.

#### Force by Template Name

```bash
curl -X POST http://localhost:8000/webhook/candidate \\
  -H "Content-Type: application/json" \\
  -H "X-Force-Response: error_template" \\
  -d '{"email": "john@example.com", "name": "John Doe"}'
```

#### Force by Status Code

```bash
curl -X POST http://localhost:8000/webhook/candidate \\
  -H "Content-Type: application/json" \\
  -H "X-Force-Response: 400" \\
  -d '{"email": "john@example.com", "name": "John Doe"}'
```

#### How Force Response Works

1. **Template Name Match**: First tries to find a template with the exact name specified
2. **Status Code Match**: If no template name matches and the value is numeric, matches against status codes
3. **Fallback**: If no forced template is found, uses the default template
4. **Debug Header**: When a forced response is used, the response includes an `X-Template-Used` header showing which template was selected

## Template Examples

### Success Response

```json
{
  "success": true,
  "message": "Request processed successfully",
  "data": {
    "id": "${mock.uuid}",
    "timestamp": "${mock.timestamp}",
    "email": "${request.email}",
    "name": "${request.name}",
    "status": "${mock.enum[active,inactive,pending]}"
  }
}
```

### Error Response

```json
{
  "error": true,
  "message": "Validation failed",
  "code": "VALIDATION_ERROR",
  "timestamp": "${mock.timestamp}"
}
```

### Webhook Response

```json
{
  "event": "candidate.created",
  "data": {
    "candidate_id": "${mock.uuid}",
    "email": "${request.email}",
    "name": "${request.name}",
    "phone": "${mock.phone}",
    "created_at": "${mock.date.now}",
    "source": "${request.source}"
  },
  "metadata": {
    "request_id": "${mock.uuid}",
    "timestamp": "${mock.timestamp}"
  }
}
```

### Force Response Example

Create multiple templates for testing different scenarios:

**Error Template (name: "validation_error")**:

```json
{
  "error": true,
  "message": "Validation failed",
  "code": "VALIDATION_ERROR",
  "timestamp": "${mock.timestamp}",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

**Server Error Template (status code: 500)**:

```json
{
  "error": true,
  "message": "Internal server error",
  "code": "INTERNAL_ERROR",
  "timestamp": "${mock.timestamp}",
  "request_id": "${mock.uuid}"
}
```

**Testing Commands**:

```bash
# Force specific template by name
curl -H "X-Force-Response: validation_error" http://localhost:8000/api/users

# Force template by status code
curl -H "X-Force-Response: 500" http://localhost:8000/api/users

# Check which template was used (look for X-Template-Used header in response)
curl -v -H "X-Force-Response: validation_error" http://localhost:8000/api/users
```

## API Documentation

### Admin Endpoints

#### Endpoint Management

- `GET /admin/endpoints` - List all endpoints
- `POST /admin/endpoints` - Create new endpoint
- `GET /admin/endpoints/{id}` - Get endpoint details
- `PUT /admin/endpoints/{id}` - Update endpoint
- `DELETE /admin/endpoints/{id}` - Delete endpoint

#### Schema & Template Management

- `POST /admin/endpoints/{id}/schemas` - Create request schema
- `POST /admin/endpoints/{id}/templates` - Create response template
- `POST /admin/templates/validate` - Validate template

#### OpenAPI Import

- `POST /admin/import/openapi/validate` - Validate OpenAPI specification file
- `POST /admin/import/openapi` - Import endpoints from OpenAPI specification

### Dynamic Endpoints

All configured endpoints are automatically available at their specified paths with the configured HTTP methods.

## 📊 Mock Data Generators

| Syntax | Description | Example |
|--------|-------------|---------|
| `${mock.int}` | Random positive integer | `42` |
| `${mock.int[1-100]}` | Random integer in range | `75` |
| `${mock.float[1.00-999.99]}` | Random float in range | `123.45` |
| `${mock.string}` | Random string | `"AbCdEf12"` |
| `${mock.string[6-10]}` | Random string with length 6-10 | `"AbCdEf12"` |
| `${mock.date.now}` | Current date (ISO format) | `"2024-01-15T10:30:00Z"` |
| `${mock.date}` | Random past date | `"2023-08-22T14:30:00Z"` |
| `${mock.time}` | Random time | `"14:30:00"` |
| `${mock.email}` | Random email address | `"john.doe@example.com"` |
| `${mock.name}` | Random full name | `"Jane Smith"` |
| `${mock.uuid}` | Random UUID | `"123e4567-e89b-12d3-a456-426614174000"` |
| `${mock.id}` | Random ID number | `12345` |
| `${mock.bool}` | Random boolean | `true` |
| `${mock.enum[a,b,c]}` | Random choice from list | `"b"` |
| `${mock.timestamp}` | Current timestamp | `1642248600` |
| `${mock.phone}` | Random phone number | `"+1-555-0123"` |
| `${mock.url}` | Random URL | `"https://example.com/path"` |
| `${mock.currency}` | Random currency amount | `"$123.45"` |

## 🐛 Troubleshooting

### Common Issues

1. **Database not found**: The SQLite database is created automatically on first run
2. **CORS errors**: The backend is configured to allow all origins for development
3. **Template validation errors**: Check that your JSON is valid and placeholders are properly formatted
4. **Port conflicts**: Change ports in the configuration if 8000 or 3000 are already in use
5. **OpenAPI import fails**: Ensure your file is valid OpenAPI 3.0.x format and includes required sections
6. **Missing mock data generators**: Some generators referenced in imported specs may not be implemented yet
7. **Complex nested schemas**: Very deep object nesting may be simplified during import
8. **X-Force-Response not working**: Ensure template names are exact matches and status codes exist as templates
9. **Force response fallback**: If forced template doesn't exist, system falls back to default template automatically

### Development

- Backend logs are available in the terminal running uvicorn
- Frontend development server provides hot reload
- Database file is created as `ats_mock_api.db` in the backend directory

## 📝 License

MIT License - feel free to use this for your projects!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Happy Mocking!**
