#!/usr/bin/env python3
"""
Test script for Weather API providers
Tests both API and MCP providers for current, tomorrow, and week timeframes
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5001/api/weather"
TEST_LOCATION = "New York"

def test_provider(provider, timeframe):
    """Test a specific provider and timeframe"""
    if timeframe == "current":
        query = f"What's the weather like in {TEST_LOCATION}?"
    elif timeframe == "tomorrow":
        query = f"What's the weather going to be like tomorrow in {TEST_LOCATION}?"
    elif timeframe == "week":
        query = f"What's the weather forecast for this week in {TEST_LOCATION}?"
    else:
        print(f"Invalid timeframe: {timeframe}")
        return False
    
    print(f"\n=== Testing {provider.upper()} provider with {timeframe} timeframe ===")
    print(f"Query: {query}")
    
    try:
        response = requests.post(
            BASE_URL,
            json={"query": query, "provider": provider},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        print(f"Response: {data['response']}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    providers = ["api", "mcp"]
    timeframes = ["current", "tomorrow", "week"]
    
    success_count = 0
    total_tests = len(providers) * len(timeframes)
    
    for provider in providers:
        for timeframe in timeframes:
            if test_provider(provider, timeframe):
                success_count += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {success_count}/{total_tests} tests")
    
    if success_count == total_tests:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
