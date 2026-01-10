"""
Test suite for simple (non-A2A) registration agent using httpx.

Run the server first with:
    python -m src.main

Then run these tests:
    pytest tests/test_simple_httpx.py -v

Or run directly:
    python tests/test_simple_httpx.py
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
    """Test simple search by name."""
    print("\n" + "=" * 60)
    print("TEST: Search by Name")
    print("=" * 60)

    # Simple JSON request
    request = {"name": "João"}

    print(f"Request: {json.dumps(request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

        assert response.status_code == 200
        assert data["status"] == "success"
        print(f"Count: {data['count']}")
        if data['count'] > 0:
            print(f"First Result: {data['results'][0]}")
        print("✓ Search by name passed")


async def test_search_by_city():
    """Test simple search by city."""
    print("\n" + "=" * 60)
    print("TEST: Search by City")
    print("=" * 60)

    request = {"city": "São Paulo"}

    print(f"Request: {json.dumps(request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "success"
        print(f"Count: {data['count']}")
        print(f"Message: {data['message']}")
        print("✓ Search by city passed")


async def test_search_by_cpf():
    """Test search by CPF (searchable but may not be exposed)."""
    print("\n" + "=" * 60)
    print("TEST: Search by CPF")
    print("=" * 60)

    request = {"cpf": "123.456.789"}

    print(f"Request: {json.dumps(request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "success"
        print(f"Message: {data['message']}")

        # Note: CPF may be searchable but not exposed in results
        if data['count'] > 0:
            print(f"Results found: {data['count']}")
            print(f"Sample result (note CPF may not be exposed): {data['results'][0]}")

        print("✓ Search by CPF passed")


async def test_multi_field_search():
    """Test multi-field search."""
    print("\n" + "=" * 60)
    print("TEST: Multi-field Search")
    print("=" * 60)

    request = {
        "surname": "Silva",
        "state": "SP"
    }

    print(f"Request: {json.dumps(request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "success"
        print(f"Count: {data['count']}")
        if data['count'] > 0:
            print(f"Results: {json.dumps(data['results'], indent=2, ensure_ascii=False)}")

        print("✓ Multi-field search passed")


async def test_search_no_results():
    """Test search with no matching results."""
    print("\n" + "=" * 60)
    print("TEST: Search with No Results")
    print("=" * 60)

    request = {"name": "NonExistentName123456"}

    print(f"Request: {json.dumps(request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "success"
        assert data["count"] == 0
        assert data["message"] == "No matching records found"
        print(f"Message: {data['message']}")
        print("✓ No results search passed")


async def test_search_by_phone():
    """Test search by phone number."""
    print("\n" + "=" * 60)
    print("TEST: Search by Phone")
    print("=" * 60)

    request = {"phone": "(11) 9"}

    print(f"Request: {json.dumps(request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "success"
        print(f"Count: {data['count']}")
        print("✓ Search by phone passed")


async def test_search_by_state():
    """Test search by state."""
    print("\n" + "=" * 60)
    print("TEST: Search by State")
    print("=" * 60)

    request = {"state": "RJ"}

    print(f"Request: {json.dumps(request, indent=2, ensure_ascii=False)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/send_message",
            json=request
        )

        print(f"\nStatus Code: {response.status_code}")
        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "success"
        print(f"Count: {data['count']}")
        print("✓ Search by state passed")


async def run_all_tests():
    """Run all tests sequentially."""
    print("\n" + "=" * 60)
    print("RUNNING SIMPLE SERVER TESTS (httpx)")
    print("=" * 60)

    tests = [
        ("Health Check", test_health_check),
        ("Get Metadata", test_get_metadata),
        ("Search by Name", test_search_by_name),
        ("Search by City", test_search_by_city),
        ("Search by CPF", test_search_by_cpf),
        ("Multi-field Search", test_multi_field_search),
        ("No Results Search", test_search_no_results),
        ("Search by Phone", test_search_by_phone),
        ("Search by State", test_search_by_state),
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
    print("\nMake sure the simple server is running on http://localhost:8000")
    print("Start it with: python -m src.main\n")

    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
