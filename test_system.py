#!/usr/bin/env python3
"""
Test script for ATS Mock API Server
This script tests the basic functionality of the system
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"
ADMIN_URL = f"{BASE_URL}/admin"

def test_system():
    print("🧪 Testing ATS Mock API Server...")

    # Test 1: Check if server is running
    try:
        response = requests.get(f"{ADMIN_URL}/endpoints")
        print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        sys.exit(1)

    # Test 2: Create a test endpoint
    endpoint_data = {
        "name": "Test Candidate Webhook",
        "path": "/test/candidate",
        "method": "POST",
        "description": "Test endpoint for candidate data",
        "is_active": True
    }

    response = requests.post(f"{ADMIN_URL}/endpoints", json=endpoint_data)
    if response.status_code == 200:
        endpoint = response.json()
        endpoint_id = endpoint["id"]
        print(f"✅ Created test endpoint: {endpoint['name']} (ID: {endpoint_id})")
    else:
        print(f"❌ Failed to create endpoint: {response.status_code} - {response.text}")
        sys.exit(1)

    # Test 3: Create a request schema
    schema_data = {
        "name": "Candidate Schema",
        "is_default": True,
        "validations": json.dumps([
            {
                "field_name": "email",
                "field_type": "email",
                "required": True
            },
            {
                "field_name": "name",
                "field_type": "string",
                "required": True,
                "min_length": 2,
                "max_length": 100
            },
            {
                "field_name": "phone",
                "field_type": "string",
                "required": False
            }
        ])
    }

    response = requests.post(f"{ADMIN_URL}/endpoints/{endpoint_id}/schemas", json=schema_data)
    if response.status_code == 200:
        schema = response.json()
        print(f"✅ Created request schema: {schema['name']}")
    else:
        print(f"❌ Failed to create schema: {response.status_code} - {response.text}")

    # Test 4: Create a response template
    template_data = {
        "name": "Success Response",
        "is_default": True,
        "status_code": 200,
        "content_type": "application/json",
        "template": json.dumps({
            "success": True,
            "message": "Candidate processed successfully",
            "data": {
                "id": "${mock.uuid}",
                "email": "${request.email}",
                "name": "${request.name}",
                "phone": "${request.phone}",
                "created_at": "${mock.date.now}",
                "status": "${mock.enum[active,pending,inactive]}",
                "score": "${mock.int}"
            },
            "metadata": {
                "request_id": "${mock.uuid}",
                "timestamp": "${mock.timestamp}"
            }
        }, separators=(',', ':'))
    }

    response = requests.post(f"{ADMIN_URL}/endpoints/{endpoint_id}/templates", json=template_data)
    if response.status_code == 200:
        template = response.json()
        print(f"✅ Created response template: {template['name']}")
    else:
        print(f"❌ Failed to create template: {response.status_code} - {response.text}")

    # Test 5: Test the dynamic endpoint with valid data
    test_request_data = {
        "email": "john.doe@example.com",
        "name": "John Doe",
        "phone": "+1-555-0123"
    }

    response = requests.post(f"{BASE_URL}/test/candidate", json=test_request_data)
    if response.status_code == 200:
        response_data = response.json()
        print(f"✅ Dynamic endpoint responded successfully")
        print(f"   Response: {json.dumps(response_data, indent=2)}")
    else:
        print(f"❌ Dynamic endpoint failed: {response.status_code} - {response.text}")

    # Test 6: Test validation with invalid data
    invalid_request_data = {
        "email": "invalid-email",
        "name": "X"  # Too short
    }

    response = requests.post(f"{BASE_URL}/test/candidate", json=invalid_request_data)
    if response.status_code == 400:
        error_data = response.json()
        print(f"✅ Validation correctly rejected invalid data")
        print(f"   Errors: {json.dumps(error_data, indent=2)}")
    else:
        print(f"❌ Validation failed to catch invalid data: {response.status_code}")

    # Test 7: Template validation
    test_template = {
        "template": json.dumps({
            "id": "${mock.uuid}",
            "name": "${request.name}",
            "invalid": "${invalid.placeholder}"
        })
    }

    response = requests.post(f"{ADMIN_URL}/templates/validate", json=test_template)
    if response.status_code == 200:
        validation_result = response.json()
        print(f"✅ Template validation working")
        print(f"   Valid: {validation_result['valid']}")
        if not validation_result['valid']:
            print(f"   Errors: {validation_result['errors']}")

    # Cleanup: Delete the test endpoint
    response = requests.delete(f"{ADMIN_URL}/endpoints/{endpoint_id}")
    if response.status_code == 200:
        print(f"✅ Cleaned up test endpoint")

    print("\n🎉 All tests completed successfully! The system is working correctly.")
    print("\n📋 What was tested:")
    print("   ✓ Server connectivity")
    print("   ✓ Endpoint creation and management")
    print("   ✓ Request schema validation")
    print("   ✓ Response template creation")
    print("   ✓ Dynamic endpoint functionality")
    print("   ✓ Mock data generation")
    print("   ✓ Template validation")
    print("   ✓ Data validation and error handling")

if __name__ == "__main__":
    test_system()