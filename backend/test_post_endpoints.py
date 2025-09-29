#!/usr/bin/env python3

import sys
sys.path.append('.')
import json

# Import the OpenAPIImporter class
from openapi_importer import OpenAPIImporter

def main():
    print("Testing POST endpoints with request schemas...")

    # Load the real OpenAPI spec
    with open('../ats-openapi-spec.yml', 'r') as f:
        content = f.read()

    # Test the importer
    importer = OpenAPIImporter()
    try:
        result = importer.import_spec(content, 'yaml')

        # Look for POST endpoints
        post_endpoints = [ep for ep in result['endpoints'] if ep['endpoint'].method == 'POST']
        print(f"Found {len(post_endpoints)} POST endpoints:")

        for i, endpoint_data in enumerate(post_endpoints):
            endpoint = endpoint_data['endpoint']
            templates = endpoint_data['templates']
            schema = endpoint_data['schema']

            print(f"\n--- POST Endpoint {i+1}: {endpoint.path} ---")
            print(f"Operation: {endpoint.name}")
            print(f"Templates: {len(templates)}")

            if schema:
                print(f"Request Schema: {schema.name}")
                try:
                    validations = json.loads(schema.validations)
                    print(f"Fields ({len(validations)}):")
                    for validation in validations:
                        print(f"  - {validation['field_name']}: {validation['field_type']} (required: {validation['required']})")
                except Exception as e:
                    print(f"  Schema parsing error: {e}")
            else:
                print("Request Schema: None")

            # Show one template as example
            if templates:
                template = templates[0]
                print(f"\nSample Template ({template.name}):")
                preview = template.template[:200].replace('\n', ' ')
                print(f"  {preview}...")

    except Exception as e:
        import traceback
        print(f'Import failed: {e}')
        traceback.print_exc()

if __name__ == "__main__":
    main()