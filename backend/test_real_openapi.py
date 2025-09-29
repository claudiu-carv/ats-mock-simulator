#!/usr/bin/env python3

import sys
sys.path.append('.')

# Import the OpenAPIImporter class
from openapi_importer import OpenAPIImporter

def main():
    print("Testing with real ATS OpenAPI spec...")

    # Load the real OpenAPI spec
    with open('../ats-openapi-spec.yml', 'r') as f:
        content = f.read()

    # Test the importer
    importer = OpenAPIImporter()
    try:
        result = importer.import_spec(content, 'yaml')
        print(f'Total endpoints: {result["total_endpoints"]}')
        print(f'Errors: {len(result["errors"])}')

        if result['errors']:
            print("\nErrors encountered:")
            for i, error in enumerate(result['errors'][:5]):  # Show first 5 errors
                print(f'{i+1}. {error}')
            if len(result['errors']) > 5:
                print(f'... and {len(result["errors"]) - 5} more errors')

        # Show details for first few endpoints
        print(f"\n=== Sample Endpoints (showing first 3 out of {len(result['endpoints'])}) ===")
        for i, endpoint_data in enumerate(result['endpoints'][:3]):
            endpoint = endpoint_data['endpoint']
            templates = endpoint_data['templates']
            schema = endpoint_data['schema']

            print(f'\n--- Endpoint {i+1}: {endpoint.method} {endpoint.path} ---')
            print(f'Operation: {endpoint.name}')
            print(f'Templates: {len(templates)}')

            # Show template names and whether they're actually different now
            template_previews = []
            for template in templates:
                preview = template.template[:100].replace('\n', ' ').strip()
                is_generic = 'success": true, "message": "Request processed successfully"' in template.template
                template_previews.append(f'{template.name} (Status: {template.status_code}, Generic: {is_generic})')

            for preview in template_previews:
                print(f'  - {preview}')

            if schema:
                print(f'Request Schema: {schema.name}')
                import json
                try:
                    validations = json.loads(schema.validations)
                    print(f'  Fields: {len(validations)} ({[v["field_name"] for v in validations[:3]]}{"..." if len(validations) > 3 else ""})')
                except:
                    print(f'  Schema validation parsing failed')
            else:
                print('Request Schema: None')

    except Exception as e:
        import traceback
        print(f'Import failed: {e}')
        traceback.print_exc()

if __name__ == "__main__":
    main()