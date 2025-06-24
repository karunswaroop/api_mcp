#!/usr/bin/env python3
"""
Check environment variables loading
"""
import os
from dotenv import load_dotenv

print("Checking environment variables...")

# Try to load .env file
load_dotenv()

# Check for various possible API key names
api_keys = [
    "WEATHERAPI_API_KEY",
    "ACCUWEATHER_API_KEY",
    "WEATHER_API_KEY"
]

print("Environment variables found:")
for key in api_keys:
    value = os.getenv(key)
    if value:
        print(f"✅ {key}: {value[:8]}...")
    else:
        print(f"❌ {key}: Not found")

# List all environment variables that contain "API" or "KEY"
print("\nAll environment variables containing 'API' or 'KEY':")
for key, value in os.environ.items():
    if 'API' in key.upper() or 'KEY' in key.upper():
        print(f"  {key}: {value[:8]}..." if value else f"  {key}: (empty)")

print("\nCurrent working directory:", os.getcwd())
print("Files in current directory:")
for file in os.listdir('.'):
    if file.startswith('.') and file.endswith('env'):
        print(f"  {file}") 