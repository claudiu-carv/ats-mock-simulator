import json
from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from backend.database import create_db_and_tables, get_session
from backend.models import (
    Endpoint,
    EndpointCreate,
    EndpointUpdate,
    EndpointRead,
    EndpointWithDetails,
    RequestSchema,
    RequestSchemaCreate,
    RequestSchemaRead,
    ResponseTemplate,
    ResponseTemplateCreate,
    ResponseTemplateRead,
)
from backend.template_engine import TemplateEngine
from backend.validation import RequestValidator
from backend.openapi_importer import OpenAPIImporter


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="ATS Mock API Server",
    description="Dynamic ATS API simulation with configurable endpoints, validation, and responses",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
template_engine = TemplateEngine()
request_validator = RequestValidator()


# Admin API Routes for managing endpoints
@app.get("/admin/endpoints", response_model=List[EndpointRead])
async def list_endpoints(session: Session = Depends(get_session)):
    """Get all endpoints."""
    endpoints = session.exec(select(Endpoint)).all()
    return endpoints


@app.get("/admin/endpoints/{endpoint_id}", response_model=EndpointWithDetails)
async def get_endpoint(endpoint_id: int, session: Session = Depends(get_session)):
    """Get endpoint with its schemas and templates."""
    endpoint = session.get(Endpoint, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    # Get schemas and templates
    schemas = session.exec(
        select(RequestSchema).where(RequestSchema.endpoint_id == endpoint_id)
    ).all()
    templates = session.exec(
        select(ResponseTemplate).where(ResponseTemplate.endpoint_id == endpoint_id)
    ).all()

    return EndpointWithDetails(
        **endpoint.dict(),
        schemas=[RequestSchemaRead(**schema.dict()) for schema in schemas],
        templates=[ResponseTemplateRead(**template.dict()) for template in templates],
    )


@app.post("/admin/endpoints", response_model=EndpointRead)
async def create_endpoint(
    endpoint: EndpointCreate, session: Session = Depends(get_session)
):
    """Create a new endpoint."""
    db_endpoint = Endpoint(**endpoint.dict())
    session.add(db_endpoint)
    session.commit()
    session.refresh(db_endpoint)
    return db_endpoint


@app.put("/admin/endpoints/{endpoint_id}", response_model=EndpointRead)
async def update_endpoint(
    endpoint_id: int,
    endpoint_update: EndpointUpdate,
    session: Session = Depends(get_session),
):
    """Update an endpoint."""
    db_endpoint = session.get(Endpoint, endpoint_id)
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    update_data = endpoint_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_endpoint, key, value)

    session.add(db_endpoint)
    session.commit()
    session.refresh(db_endpoint)
    return db_endpoint


@app.delete("/admin/endpoints/{endpoint_id}")
async def delete_endpoint(endpoint_id: int, session: Session = Depends(get_session)):
    """Delete an endpoint and its associated schemas and templates."""
    db_endpoint = session.get(Endpoint, endpoint_id)
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    # Delete associated schemas and templates
    session.exec(
        select(RequestSchema).where(RequestSchema.endpoint_id == endpoint_id)
    ).all()
    for schema in session.exec(
        select(RequestSchema).where(RequestSchema.endpoint_id == endpoint_id)
    ).all():
        session.delete(schema)

    for template in session.exec(
        select(ResponseTemplate).where(ResponseTemplate.endpoint_id == endpoint_id)
    ).all():
        session.delete(template)

    session.delete(db_endpoint)
    session.commit()
    return {"message": "Endpoint deleted successfully"}


# Request Schema management
@app.post("/admin/endpoints/{endpoint_id}/schemas", response_model=RequestSchemaRead)
async def create_request_schema(
    endpoint_id: int,
    schema: RequestSchemaCreate,
    session: Session = Depends(get_session),
):
    """Create a request schema for an endpoint."""
    # Verify endpoint exists
    endpoint = session.get(Endpoint, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    # Validate the validations JSON
    try:
        validations = RequestValidator.parse_validations(schema.validations)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # If this is marked as default, unset other defaults
    if schema.is_default:
        existing_schemas = session.exec(
            select(RequestSchema).where(
                RequestSchema.endpoint_id == endpoint_id,
                RequestSchema.is_default == True,
            )
        ).all()
        for existing_schema in existing_schemas:
            existing_schema.is_default = False
            session.add(existing_schema)

    db_schema = RequestSchema(endpoint_id=endpoint_id, **schema.dict())
    session.add(db_schema)
    session.commit()
    session.refresh(db_schema)
    return db_schema


@app.get("/admin/schemas/{schema_id}", response_model=RequestSchemaRead)
async def get_request_schema(schema_id: int, session: Session = Depends(get_session)):
    """Get a specific request schema."""
    schema = session.get(RequestSchema, schema_id)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema


@app.delete("/admin/schemas/{schema_id}")
async def delete_request_schema(
    schema_id: int, session: Session = Depends(get_session)
):
    """Delete a request schema."""
    schema = session.get(RequestSchema, schema_id)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")

    session.delete(schema)
    session.commit()
    return {"message": "Schema deleted successfully"}


# Response Template management
@app.post(
    "/admin/endpoints/{endpoint_id}/templates", response_model=ResponseTemplateRead
)
async def create_response_template(
    endpoint_id: int,
    template: ResponseTemplateCreate,
    session: Session = Depends(get_session),
):
    """Create a response template for an endpoint."""
    # Verify endpoint exists
    endpoint = session.get(Endpoint, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    # Validate template
    validation_result = template_engine.validate_template(template.template)
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid template: {', '.join(validation_result['errors'])}",
        )

    # If this is marked as default, unset other defaults
    if template.is_default:
        existing_templates = session.exec(
            select(ResponseTemplate).where(
                ResponseTemplate.endpoint_id == endpoint_id,
                ResponseTemplate.is_default == True,
            )
        ).all()
        for existing_template in existing_templates:
            existing_template.is_default = False
            session.add(existing_template)

    db_template = ResponseTemplate(endpoint_id=endpoint_id, **template.dict())
    session.add(db_template)
    session.commit()
    session.refresh(db_template)
    return db_template


@app.get("/admin/templates/{template_id}", response_model=ResponseTemplateRead)
async def get_response_template(
    template_id: int, session: Session = Depends(get_session)
):
    """Get a specific response template."""
    template = session.get(ResponseTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@app.delete("/admin/templates/{template_id}")
async def delete_response_template(
    template_id: int, session: Session = Depends(get_session)
):
    """Delete a response template."""
    template = session.get(ResponseTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    session.delete(template)
    session.commit()
    return {"message": "Template deleted successfully"}


# Template validation endpoint
@app.post("/admin/templates/validate")
async def validate_template(template_data: Dict[str, str]):
    """Validate a template without saving it."""
    template = template_data.get("template", "")
    if not template:
        raise HTTPException(status_code=400, detail="Template is required")

    validation_result = template_engine.validate_template(template)
    return validation_result


# OpenAPI import endpoints
@app.post("/admin/import/openapi")
async def import_openapi_spec(
    file: UploadFile = File(...), session: Session = Depends(get_session)
):
    """Import endpoints from OpenAPI specification file."""

    # Read file content
    content = await file.read()

    try:
        # Determine format and parse
        importer = OpenAPIImporter()
        results = importer.import_spec(content.decode("utf-8"))

        # Create endpoints, schemas, and templates
        created_endpoints = []

        for endpoint_data in results["endpoints"]:
            try:
                # Create endpoint
                db_endpoint = Endpoint(**endpoint_data["endpoint"].dict())
                session.add(db_endpoint)
                session.commit()
                session.refresh(db_endpoint)

                # Create schema if present
                if endpoint_data["schema"]:
                    db_schema = RequestSchema(
                        endpoint_id=db_endpoint.id, **endpoint_data["schema"].dict()
                    )
                    session.add(db_schema)

                # Create templates
                for template in endpoint_data["templates"]:
                    db_template = ResponseTemplate(
                        endpoint_id=db_endpoint.id, **template.dict()
                    )
                    session.add(db_template)

                session.commit()
                created_endpoints.append(
                    {
                        "endpoint": EndpointRead(**db_endpoint.dict()),
                        "schemas_count": 1 if endpoint_data["schema"] else 0,
                        "templates_count": len(endpoint_data["templates"]),
                    }
                )

            except Exception as e:
                session.rollback()
                results["errors"].append(
                    f"Failed to create {endpoint_data['endpoint'].name}: {str(e)}"
                )

        return {
            "success": True,
            "created_endpoints": created_endpoints,
            "total_created": len(created_endpoints),
            "errors": results["errors"],
            "warnings": results["warnings"],
        }

    except Exception as e:
        return JSONResponse(
            status_code=400, content={"success": False, "error": str(e)}
        )


@app.post("/admin/import/openapi/validate")
async def validate_openapi_spec(file: UploadFile = File(...)):
    """Validate OpenAPI specification without importing."""

    content = await file.read()

    try:
        importer = OpenAPIImporter()
        results = importer.import_spec(content.decode("utf-8"))

        return {
            "valid": True,
            "endpoints_found": results["total_endpoints"],
            "endpoints": [
                {
                    "path": ep["endpoint"].path,
                    "method": ep["endpoint"].method,
                    "name": ep["endpoint"].name,
                    "has_schema": ep["schema"] is not None,
                    "templates_count": len(ep["templates"]),
                }
                for ep in results["endpoints"]
            ],
            "errors": results["errors"],
            "warnings": results["warnings"],
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}


# Dynamic endpoint handler
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def handle_dynamic_endpoint(
    request: Request, path: str, session: Session = Depends(get_session)
):
    """Handle requests to dynamic endpoints."""
    method = request.method
    full_path = f"/{path}"

    # Find matching endpoint
    endpoint = session.exec(
        select(Endpoint).where(
            Endpoint.path == full_path,
            Endpoint.method == method,
            Endpoint.is_active == True,
        )
    ).first()

    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    # Get request data
    request_data = {}
    content_type = request.headers.get("content-type", "")

    if method in ["POST", "PUT", "PATCH"]:
        if "application/json" in content_type:
            try:
                request_data = await request.json()
            except Exception:
                request_data = {}
        elif "application/x-www-form-urlencoded" in content_type:
            form_data = await request.form()
            request_data = dict(form_data)
        else:
            # Try to parse as JSON anyway
            try:
                body = await request.body()
                if body:
                    request_data = json.loads(body.decode())
            except Exception:
                request_data = {}

    # Add query parameters to request data
    request_data.update(dict(request.query_params))

    # Validate request if schema exists
    default_schema = session.exec(
        select(RequestSchema).where(
            RequestSchema.endpoint_id == endpoint.id, RequestSchema.is_default == True
        )
    ).first()

    if default_schema:
        try:
            validations = RequestValidator.parse_validations(default_schema.validations)
            validation_result = request_validator.validate_request(
                request_data, validations
            )

            if not validation_result.valid:
                error_details = [
                    {
                        "field": error.field,
                        "message": error.message,
                        "value": error.value,
                    }
                    for error in validation_result.errors
                ]
                return JSONResponse(
                    status_code=400,
                    content={"error": "Validation failed", "details": error_details},
                )
        except Exception as e:
            # Log validation error but don't fail the request
            print(f"Validation error: {str(e)}")

    # Check for force response header
    force_response_header = request.headers.get("X-Force-Response")

    selected_template = None

    if force_response_header:
        # Try to find template by name first
        selected_template = session.exec(
            select(ResponseTemplate).where(
                ResponseTemplate.endpoint_id == endpoint.id,
                ResponseTemplate.name == force_response_header,
            )
        ).first()

        # If not found by name, try to find by status code (e.g., "400", "500")
        if not selected_template and force_response_header.isdigit():
            status_code = int(force_response_header)
            selected_template = session.exec(
                select(ResponseTemplate).where(
                    ResponseTemplate.endpoint_id == endpoint.id,
                    ResponseTemplate.status_code == status_code,
                )
            ).first()

    # Fall back to default template if no forced template or forced template not found
    if not selected_template:
        selected_template = session.exec(
            select(ResponseTemplate).where(
                ResponseTemplate.endpoint_id == endpoint.id,
                ResponseTemplate.is_default == True,
            )
        ).first()

    if not selected_template:
        # Return a basic success response if no template is configured
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Request processed successfully"},
        )

    # Render response template
    try:
        rendered_response = template_engine.render(
            selected_template.template, request_data
        )

        # Try to parse as JSON, fall back to plain text
        try:
            response_data = json.loads(rendered_response)
        except json.JSONDecodeError:
            response_data = rendered_response

        # Add header to indicate which template was used (helpful for debugging)
        response_headers = {"Content-Type": selected_template.content_type}
        if force_response_header:
            response_headers["X-Template-Used"] = selected_template.name

        return JSONResponse(
            status_code=selected_template.status_code,
            content=response_data,
            headers=response_headers,
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Template rendering failed", "details": str(e)},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
