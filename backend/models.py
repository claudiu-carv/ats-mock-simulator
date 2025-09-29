from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Any, List
from datetime import datetime
from pydantic import BaseModel


class EndpointBase(SQLModel):
    path: str = Field(
        index=True, description="API endpoint path (e.g., /webhook/candidate)"
    )
    method: str = Field(default="POST", description="HTTP method")
    name: str = Field(description="Human-readable endpoint name")
    description: Optional[str] = Field(default=None, description="Endpoint description")
    is_active: bool = Field(default=True, description="Whether endpoint is active")


class Endpoint(EndpointBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    schemas: List["RequestSchema"] = Relationship(back_populates="endpoint")
    templates: List["ResponseTemplate"] = Relationship(back_populates="endpoint")


class EndpointCreate(EndpointBase):
    pass


class EndpointUpdate(SQLModel):
    path: Optional[str] = None
    method: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class FieldValidation(BaseModel):
    field_name: str
    field_type: str  # "string", "int", "float", "bool", "email"
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None  # regex pattern
    choices: Optional[List[str]] = None  # enum values


class RequestSchemaBase(SQLModel):
    endpoint_id: int = Field(foreign_key="endpoint.id")
    name: str = Field(description="Schema name")
    validations: str = Field(
        description="JSON serialized list of FieldValidation objects"
    )
    is_default: bool = Field(
        default=False, description="Whether this is the default schema for the endpoint"
    )


class RequestSchema(RequestSchemaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    endpoint: Optional[Endpoint] = Relationship(back_populates="schemas")


class RequestSchemaCreate(SQLModel):
    name: str = Field(description="Schema name")
    validations: str = Field(
        description="JSON serialized list of FieldValidation objects"
    )
    is_default: bool = Field(
        default=False, description="Whether this is the default schema for the endpoint"
    )


class ResponseTemplateBase(SQLModel):
    endpoint_id: int = Field(foreign_key="endpoint.id")
    name: str = Field(description="Template name")
    template: str = Field(description="JSON template with ${} placeholders")
    status_code: int = Field(default=200, description="HTTP status code to return")
    content_type: str = Field(
        default="application/json", description="Response content type"
    )
    is_default: bool = Field(
        default=False,
        description="Whether this is the default template for the endpoint",
    )


class ResponseTemplate(ResponseTemplateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    endpoint: Optional[Endpoint] = Relationship(back_populates="templates")


class ResponseTemplateCreate(SQLModel):
    name: str = Field(description="Template name")
    template: str = Field(description="JSON template with ${} placeholders")
    status_code: int = Field(default=200, description="HTTP status code to return")
    content_type: str = Field(
        default="application/json", description="Response content type"
    )
    is_default: bool = Field(
        default=False,
        description="Whether this is the default template for the endpoint",
    )


# Response models for API
class EndpointRead(EndpointBase):
    id: int
    created_at: datetime
    updated_at: datetime


class RequestSchemaRead(RequestSchemaBase):
    id: int
    created_at: datetime


class ResponseTemplateRead(ResponseTemplateBase):
    id: int
    created_at: datetime


class EndpointWithDetails(EndpointRead):
    schemas: List[RequestSchemaRead] = []
    templates: List[ResponseTemplateRead] = []


# Validation response models
class ValidationError(BaseModel):
    field: str
    message: str
    value: Any


class ValidationResult(BaseModel):
    valid: bool
    errors: List[ValidationError] = []
