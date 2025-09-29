#!/usr/bin/env python3

import sys
sys.path.append('.')

# Test with a small section of the OpenAPI spec to verify the fixes
test_spec = '''
openapi: 3.0.0
info:
  title: Test ATS API
  version: 1.0.0
components:
  responses:
    GetJobsResponse:
      description: Jobs
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/GetJobsResponse'
  schemas:
    GetJobsResponse:
      type: object
      required:
        - status_code
        - status
        - service
        - resource
        - operation
        - data
      properties:
        status_code:
          type: integer
          description: HTTP Response Status Code
          example: 200
        status:
          type: string
          description: HTTP Response Status
          example: OK
        service:
          type: string
          description: Apideck service name
          example: lever
        resource:
          type: string
          description: Apideck resource name
          example: jobs
        operation:
          type: string
          description: Apideck operation name
          example: all
        data:
          type: array
          items:
            $ref: '#/components/schemas/Job'
    Job:
      type: object
      properties:
        id:
          type: string
          description: A unique identifier for an object.
          example: '12345'
        title:
          type: string
          description: The job title
          example: CEO
        description:
          type: string
          description: The job description
        salary:
          type: object
          properties:
            min:
              type: number
            max:
              type: number
            currency:
              type: string
paths:
  /ats/jobs:
    get:
      operationId: jobsAll
      summary: List Jobs
      responses:
        '200':
          $ref: '#/components/responses/GetJobsResponse'
        '400':
          description: Bad Request
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
    post:
      operationId: jobsAdd
      summary: Create Job
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                title:
                  type: string
                description:
                  type: string
                salary:
                  type: number
              required: [title]
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Job'
'''

# Import the OpenAPIImporter class
from openapi_importer import OpenAPIImporter

def main():
    # Test the importer
    importer = OpenAPIImporter()
    try:
        result = importer.import_spec(test_spec, 'yaml')
        print(f'Total endpoints: {result["total_endpoints"]}')
        print(f'Errors: {len(result["errors"])}')

        if result['errors']:
            for error in result['errors']:
                print(f'Error: {error}')

        for i, endpoint_data in enumerate(result['endpoints']):
            endpoint = endpoint_data['endpoint']
            templates = endpoint_data['templates']
            schema = endpoint_data['schema']

            print(f'\n=== Endpoint {i+1}: {endpoint.method} {endpoint.path} ===')
            print(f'Name: {endpoint.name}')
            print(f'Templates: {len(templates)}')

            for j, template in enumerate(templates):
                print(f'\n  Template {j+1}: {template.name}')
                print(f'  Status: {template.status_code}')
                print(f'  Default: {template.is_default}')
                template_preview = template.template[:300] + ('...' if len(template.template) > 300 else '')
                print(f'  Content: {template_preview}')

            if schema:
                print(f'\n  Schema: {schema.name}')
                import json
                validations = json.loads(schema.validations)
                print(f'  Validations: {len(validations)}')
                for validation in validations:
                    print(f'    - {validation["field_name"]}: {validation["field_type"]} (required: {validation["required"]})')

    except Exception as e:
        import traceback
        print(f'Import failed: {e}')
        traceback.print_exc()

if __name__ == "__main__":
    main()