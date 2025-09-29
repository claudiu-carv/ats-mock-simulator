#!/usr/bin/env python3

import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from openapi_importer import OpenAPIImporter

def test_openapi_import():
    """Test the improved OpenAPI importer with the sample spec."""

    # Read the test OpenAPI spec
    with open('test_openapi.yaml', 'r') as f:
        spec_content = f.read()

    # Initialize importer and import spec
    importer = OpenAPIImporter()

    try:
        result = importer.import_spec(spec_content, 'yaml')

        print(f"✅ Successfully imported OpenAPI spec")
        print(f"📊 Total endpoints: {result['total_endpoints']}")
        print(f"❌ Errors: {len(result['errors'])}")
        print(f"⚠️  Warnings: {len(result['warnings'])}")

        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")

        # Test each endpoint
        for i, endpoint_data in enumerate(result['endpoints'], 1):
            endpoint = endpoint_data['endpoint']
            templates = endpoint_data['templates']

            print(f"\n🔗 Endpoint {i}: {endpoint.method} {endpoint.path}")
            print(f"   Name: {endpoint.name}")

            # Test templates - should be different for each endpoint
            print(f"   📄 Templates ({len(templates)}):")
            for template in templates:
                template_json = json.loads(template.template)
                print(f"      - {template.name} (Status: {template.status_code})")
                print(f"        Preview: {json.dumps(template_json, indent=8)[:200]}...")

        # Verify that templates are different for different endpoints
        template_contents = []
        for endpoint_data in result['endpoints']:
            for template in endpoint_data['templates']:
                template_contents.append(template.template)

        unique_templates = set(template_contents)
        print(f"\n🧪 Template diversity test:")
        print(f"   Total templates: {len(template_contents)}")
        print(f"   Unique templates: {len(unique_templates)}")

        if len(unique_templates) > 1:
            print("   ✅ Templates are properly differentiated")
        else:
            print("   ❌ Templates are still identical (issue not fixed)")

        return result

    except Exception as e:
        print(f"❌ Failed to import OpenAPI spec: {e}")
        raise

if __name__ == "__main__":
    test_openapi_import()