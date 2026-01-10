"""
Test suite for A2A-compliant registration agent using httpx.

Run the server first with:
    python -m src.main --mode compliant

Then run these tests:
    pytest tests/test_a2a_compliant.py -v

Or run directly:
    python tests/test_a2a_compliant.py
"""
import asyncio
import json
import httpx


BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test the health check endpoint."""
    print("\n" + "=" * 60)
    print("TEST: Health Check")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")


async def test_get_metadata():
    """Test retrieving agent metadata."""
    print("\n" + "=" * 60)
    print("TEST: Get Agent Metadata")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/metadata")

        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Agent Name: {data.get('name')}")
        print(f"Description: {data.get('description')}")
        print(f"Version: {data.get('version')}")

        assert response.status_code == 200
        assert "name" in data
        assert "capabilities" in data
        print("✓ Metadata retrieval passed")


async def test_search_by_name():
    """Test A2A search by name."""
    print("\n" + "=" * 60)
    print("TEST: A2A Search by Name")
    print("=" * 60)

    # A2A-compliant request format
    a2a_request = {
        "message": {
            "role": "user",
            "parts": [
                {
                    "text": json.dumps({"name": "João"})
                }
            ]
        }
    }

    print(f"Request: {json.dumps(a2a_request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=a2a_request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

        assert response.status_code == 200
        assert "message" in data
        assert "parts" in data["message"]

        # Parse the text from response parts
        result_text = data["message"]["parts"][0]["text"]
        result_data = json.loads(result_text)

        print(f"\nParsed Result:")
        print(f"Status: {result_data['status']}")
        print(f"Count: {result_data['count']}")
        if result_data['count'] > 0:
            print(f"First Result: {result_data['results'][0]}")

        assert result_data["status"] == "success"
        print("✓ Search by name passed")


async def test_search_by_city():
    """Test A2A search by city."""
    print("\n" + "=" * 60)
    print("TEST: A2A Search by City")
    print("=" * 60)

    a2a_request = {
        "message": {
            "role": "user",
            "parts": [
                {
                    "text": json.dumps({"city": "São Paulo"})
                }
            ]
        }
    }

    print(f"Request: {json.dumps(a2a_request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=a2a_request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        result_text = data["message"]["parts"][0]["text"]
        result_data = json.loads(result_text)

        print(f"Status: {result_data['status']}")
        print(f"Count: {result_data['count']}")
        print(f"Message: {result_data['message']}")

        assert result_data["status"] == "success"
        print("✓ Search by city passed")


async def test_search_by_cpf():
    """Test A2A search by CPF (searchable but may not be exposed)."""
    print("\n" + "=" * 60)
    print("TEST: A2A Search by CPF")
    print("=" * 60)

    a2a_request = {
        "message": {
            "role": "user",
            "parts": [
                {
                    "text": json.dumps({"cpf": "123.456.789-00"})
                }
            ]
        }
    }

    print(f"Request: {json.dumps(a2a_request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=a2a_request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        result_text = data["message"]["parts"][0]["text"]
        result_data = json.loads(result_text)

        print(f"Status: {result_data['status']}")
        print(f"Message: {result_data['message']}")

        # Note: CPF may be searchable but not exposed in results
        if result_data['count'] > 0:
            print(f"Results found: {result_data['count']}")
            print(f"Sample result (note CPF may not be exposed): {result_data['results'][0]}")

        assert result_data["status"] == "success"
        print("✓ Search by CPF passed")


async def test_multi_field_search():
    """Test A2A multi-field search."""
    print("\n" + "=" * 60)
    print("TEST: A2A Multi-field Search")
    print("=" * 60)

    a2a_request = {
        "message": {
            "role": "user",
            "parts": [
                {
                    "text": json.dumps({
                        "surname": "Silva",
                        "state": "SP"
                    })
                }
            ]
        }
    }

    print(f"Request: {json.dumps(a2a_request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=a2a_request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        result_text = data["message"]["parts"][0]["text"]
        result_data = json.loads(result_text)

        print(f"Status: {result_data['status']}")
        print(f"Count: {result_data['count']}")
        if result_data['count'] > 0:
            print(f"Results: {json.dumps(result_data['results'], indent=2, ensure_ascii=False)}")

        assert result_data["status"] == "success"
        print("✓ Multi-field search passed")


async def test_search_no_results():
    """Test A2A search with no matching results."""
    print("\n" + "=" * 60)
    print("TEST: A2A Search with No Results")
    print("=" * 60)

    a2a_request = {
        "message": {
            "role": "user",
            "parts": [
                {
                    "text": json.dumps({"name": "NonExistentName123456"})
                }
            ]
        }
    }

    print(f"Request: {json.dumps(a2a_request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=a2a_request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        result_text = data["message"]["parts"][0]["text"]
        result_data = json.loads(result_text)

        print(f"Status: {result_data['status']}")
        print(f"Message: {result_data['message']}")
        print(f"Count: {result_data['count']}")

        assert result_data["status"] == "success"
        assert result_data["count"] == 0
        assert result_data["message"] == "No matching records found"
        print("✓ No results search passed")


async def test_invalid_request_format():
    """Test handling of invalid A2A request format."""
    print("\n" + "=" * 60)
    print("TEST: Invalid A2A Request Format")
    print("=" * 60)

    # Missing 'message' field
    invalid_request = {
        "data": "invalid"
    }

    print(f"Request: {json.dumps(invalid_request, indent=2)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=invalid_request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

        assert response.status_code == 400
        result_text = data["message"]["parts"][0]["text"]
        result_data = json.loads(result_text)
        assert result_data["status"] == "error"
        print("✓ Invalid format handling passed")


async def test_invalid_json_in_parts():
    """Test handling of invalid JSON in message parts."""
    print("\n" + "=" * 60)
    print("TEST: Invalid JSON in Message Parts")
    print("=" * 60)

    a2a_request = {
        "message": {
            "role": "user",
            "parts": [
                {
                    "text": "This is not valid JSON"
                }
            ]
        }
    }

    print(f"Request: {json.dumps(a2a_request, indent=2)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=a2a_request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

        assert response.status_code == 400
        result_text = data["message"]["parts"][0]["text"]
        result_data = json.loads(result_text)
        assert result_data["status"] == "error"
        assert "Invalid JSON" in result_data["message"]
        print("✓ Invalid JSON handling passed")


async def run_all_tests():
    """Run all tests sequentially."""
    print("\n" + "=" * 60)
    print("RUNNING A2A-COMPLIANT SERVER TESTS")
    print("=" * 60)

    tests = [
        ("Health Check", test_health_check),
        ("Get Metadata", test_get_metadata),
        ("Search by Name", test_search_by_name),
        ("Search by City", test_search_by_city),
        ("Search by CPF", test_search_by_cpf),
        ("Multi-field Search", test_multi_field_search),
        ("No Results Search", test_search_no_results),
        ("Invalid Request Format", test_invalid_request_format),
        ("Invalid JSON in Parts", test_invalid_json_in_parts),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ {test_name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ {test_name} ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 60)


if __name__ == "__main__":
    print("\nMake sure the A2A-compliant server is running on http://localhost:8000")
    print("Start it with: python -m src.main --mode compliant\n")

    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
