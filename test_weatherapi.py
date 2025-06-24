#!/usr/bin/env python3
"""
Test script for WeatherAPI.com implementation
"""
import os
from dotenv import load_dotenv
from weather_api.utils import (
    get_location_key,
    get_current_weather,
    get_forecast,
    get_historical_weather
)

# Load environment variables
load_dotenv()

def test_weatherapi_implementation():
    """Test the WeatherAPI.com implementation"""
    print("Testing WeatherAPI.com implementation...")
    
    # Check if API key is set
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        print("❌ WEATHERAPI_KEY not found in environment variables")
        print("Please set your WeatherAPI.com API key in the .env file")
        return False
    
    print(f"✅ API key found: {api_key[:8]}...")
    
    # Test location validation
    print("\n1. Testing location validation...")
    location_result = get_location_key("New York")
    if "error" in location_result:
        print(f"❌ Location validation failed: {location_result['error']}")
        return False
    else:
        print(f"✅ Location validated: {location_result['name']}, {location_result['region']}, {location_result['country']}")
    
    # Test current weather
    print("\n2. Testing current weather...")
    current_weather = get_current_weather("New York")
    if "error" in current_weather:
        print(f"❌ Current weather failed: {current_weather['error']}")
        return False
    else:
        current = current_weather.get("current", {})
        location = current_weather.get("location", {})
        print(f"✅ Current weather for {location.get('name', 'Unknown')}:")
        print(f"   Temperature: {current.get('temp_f', 'N/A')}°F ({current.get('temp_c', 'N/A')}°C)")
        print(f"   Condition: {current.get('condition', {}).get('text', 'N/A')}")
        print(f"   Humidity: {current.get('humidity', 'N/A')}%")
    
    # Test forecast
    print("\n3. Testing forecast...")
    forecast = get_forecast("New York")
    if "error" in forecast:
        print(f"❌ Forecast failed: {forecast['error']}")
        return False
    else:
        forecast_days = forecast.get("forecast", {}).get("forecastday", [])
        print(f"✅ Forecast retrieved: {len(forecast_days)} days")
        if forecast_days:
            first_day = forecast_days[0]
            day_info = first_day.get("day", {})
            print(f"   First day: {first_day.get('date', 'N/A')}")
            print(f"   High: {day_info.get('maxtemp_f', 'N/A')}°F")
            print(f"   Low: {day_info.get('mintemp_f', 'N/A')}°F")
    
    # Test historical weather
    print("\n4. Testing historical weather...")
    historical = get_historical_weather("New York")
    if "error" in historical:
        print(f"❌ Historical weather failed: {historical['error']}")
        return False
    else:
        forecast_day = historical.get("forecast", {}).get("forecastday", [])
        if forecast_day:
            day_data = forecast_day[0]
            day_info = day_data.get("day", {})
            print(f"✅ Historical weather for {day_data.get('date', 'N/A')}:")
            print(f"   High: {day_info.get('maxtemp_f', 'N/A')}°F")
            print(f"   Low: {day_info.get('mintemp_f', 'N/A')}°F")
            print(f"   Condition: {day_info.get('condition', {}).get('text', 'N/A')}")
        else:
            print("⚠️  No historical data available")
    
    print("\n🎉 All tests passed! WeatherAPI.com implementation is working correctly.")
    return True

if __name__ == "__main__":
    test_weatherapi_implementation() 