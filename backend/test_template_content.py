#!/usr/bin/env python3

import sys
sys.path.append('.')
import json

# Import the OpenAPIImporter class
from openapi_importer import OpenAPIImporter

def main():
    print("Testing template content with real ATS OpenAPI spec...")

    # Load the real OpenAPI spec
    with open('../ats-openapi-spec.yml', 'r') as f:
        content = f.read()

    # Test the importer
    importer = OpenAPIImporter()
    try:
        result = importer.import_spec(content, 'yaml')

        # Look at the first endpoint's template
        if result['endpoints']:
            endpoint_data = result['endpoints'][0]
            endpoint = endpoint_data['endpoint']
            templates = endpoint_data['templates']

            print(f"Endpoint: {endpoint.method} {endpoint.path}")
            print(f"Operation: {endpoint.name}")
            print(f"Templates: {len(templates)}")

            if templates:
                template = templates[0]  # First template (200 response)
                print(f"\nTemplate: {template.name}")
                print(f"Status: {template.status_code}")
                print(f"Content:")
                print("=" * 50)
                print(template.template)
                print("=" * 50)

                # Check if it's still the old generic template
                is_generic = '"success": true' in template.template and '"message": "Request processed successfully"' in template.template
                print(f"\nIs Generic Template: {is_generic}")

    except Exception as e:
        import traceback
        print(f'Import failed: {e}')
        traceback.print_exc()

if __name__ == "__main__":
    main()