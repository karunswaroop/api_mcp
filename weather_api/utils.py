"""
Utility functions for the Weather API POC
"""
import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Get API key from environment variables
ACCUWEATHER_API_KEY = os.getenv("ACCUWEATHER_API_KEY")

# AccuWeather API base URLs
ACCUWEATHER_BASE_URL = "http://dataservice.accuweather.com"
LOCATION_ENDPOINT = "/locations/v1/cities/search"
CURRENT_CONDITIONS_ENDPOINT = "/currentconditions/v1/"
FORECAST_ENDPOINT = "/forecasts/v1/daily/5day/"
HISTORICAL_ENDPOINT = "/currentconditions/v1/historical/24"

def extract_weather_parameters(user_query: str) -> Dict[str, Any]:
    """
    Extract weather parameters from user query using simple keyword matching.
    In a production environment, this would use an LLM for better extraction.
    
    Args:
        user_query: The user's natural language query
        
    Returns:
        Dictionary containing extracted parameters
    """
    query = user_query.lower()
    params = {}
    
    # Extract location
    location_keywords = ["in", "at", "for", "of"]
    for keyword in location_keywords:
        if f" {keyword} " in query:
            parts = query.split(f" {keyword} ")
            if len(parts) > 1:
                location_part = parts[1].split("?")[0].split(".")[0].strip()
                params["location"] = location_part
                break
    
    # Extract time frame
    if "tomorrow" in query:
        params["timeframe"] = "tomorrow"
    elif "week" in query or "5 day" in query or "5-day" in query:
        params["timeframe"] = "week"
    elif "yesterday" in query or "past" in query or "historical" in query:
        params["timeframe"] = "historical"
    else:
        params["timeframe"] = "current"
    
    # Extract specific weather parameters of interest
    weather_aspects = ["temperature", "rain", "precipitation", "humidity", 
                      "wind", "pressure", "uv", "visibility"]
    
    for aspect in weather_aspects:
        if aspect in query:
            if "specific_info" not in params:
                params["specific_info"] = []
            params["specific_info"].append(aspect)
    
    # Default location if none found
    if "location" not in params:
        params["location"] = "New York"
        
    return params

def get_location_key(location: str) -> Optional[str]:
    """
    Get the location key for a given location name from AccuWeather API
    
    Args:
        location: Name of the location (city, etc.)
        
    Returns:
        Location key if found, None otherwise
    """
    params = {
        "apikey": ACCUWEATHER_API_KEY,
        "q": location
    }
    
    try:
        response = requests.get(f"{ACCUWEATHER_BASE_URL}{LOCATION_ENDPOINT}", params=params)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            return data[0]["Key"]
        return None
    except Exception as e:
        print(f"Error getting location key: {e}")
        return None

def get_current_weather(location_key: str) -> Dict[str, Any]:
    """
    Get current weather conditions for a location
    
    Args:
        location_key: AccuWeather location key
        
    Returns:
        Dictionary with current weather data
    """
    params = {
        "apikey": ACCUWEATHER_API_KEY,
        "details": "true"
    }
    
    try:
        response = requests.get(f"{ACCUWEATHER_BASE_URL}{CURRENT_CONDITIONS_ENDPOINT}{location_key}", params=params)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            return data[0]
        return {"error": "No weather data available"}
    except Exception as e:
        return {"error": f"Error getting current weather: {e}"}

def get_forecast(location_key: str) -> Dict[str, Any]:
    """
    Get 5-day forecast for a location
    
    Args:
        location_key: AccuWeather location key
        
    Returns:
        Dictionary with forecast data
    """
    params = {
        "apikey": ACCUWEATHER_API_KEY,
        "details": "true",
        "metric": "false"
    }
    
    try:
        response = requests.get(f"{ACCUWEATHER_BASE_URL}{FORECAST_ENDPOINT}{location_key}", params=params)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        return {"error": f"Error getting forecast: {e}"}

def get_historical_weather(location_key: str) -> Dict[str, Any]:
    """
    Get historical weather data for a location (past 24 hours)
    
    Args:
        location_key: AccuWeather location key
        
    Returns:
        Dictionary with historical weather data
    """
    params = {
        "apikey": ACCUWEATHER_API_KEY,
        "details": "true"
    }
    
    try:
        response = requests.get(f"{ACCUWEATHER_BASE_URL}{HISTORICAL_ENDPOINT}/{location_key}", params=params)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        return {"error": f"Error getting historical weather: {e}"}

def format_current_weather_for_user(weather_data: Dict[str, Any], location_name: str) -> str:
    """
    Format current weather data into a user-friendly response
    
    Args:
        weather_data: Current weather data from AccuWeather
        location_name: Name of the location
        
    Returns:
        Formatted string with weather information
    """
    if "error" in weather_data:
        return f"Sorry, I couldn't get the weather information: {weather_data['error']}"
    
    try:
        weather_text = weather_data.get("WeatherText", "Unknown conditions")
        temp_f = weather_data.get("Temperature", {}).get("Imperial", {}).get("Value", "N/A")
        temp_c = weather_data.get("Temperature", {}).get("Metric", {}).get("Value", "N/A")
        humidity = weather_data.get("RelativeHumidity", "N/A")
        wind_speed = weather_data.get("Wind", {}).get("Speed", {}).get("Imperial", {}).get("Value", "N/A")
        wind_direction = weather_data.get("Wind", {}).get("Direction", {}).get("Localized", "N/A")
        
        response = f"Current weather for {location_name}:\n"
        response += f"• Condition: {weather_text}\n"
        response += f"• Temperature: {temp_f}°F ({temp_c}°C)\n"
        response += f"• Humidity: {humidity}%\n"
        response += f"• Wind: {wind_speed} mph from {wind_direction}\n"
        
        return response
    except Exception as e:
        return f"Error formatting weather data: {e}"

def format_forecast_for_user(forecast_data: Dict[str, Any], location_name: str, timeframe: str = "week") -> str:
    """
    Format forecast data into a user-friendly response
    
    Args:
        forecast_data: Forecast data from AccuWeather
        location_name: Name of the location
        timeframe: The timeframe requested ("tomorrow" or "week")
        
    Returns:
        Formatted string with forecast information
    """
    if "error" in forecast_data:
        return f"Sorry, I couldn't get the forecast information: {forecast_data['error']}"
    
    try:
        headline = forecast_data.get("Headline", {}).get("Text", "No headline available")
        daily_forecasts = forecast_data.get("DailyForecasts", [])
        
        # Handle tomorrow's forecast specifically
        if timeframe == "tomorrow" and len(daily_forecasts) > 0:
            tomorrow = daily_forecasts[0]  # First day in forecast is tomorrow
            date = tomorrow.get("Date", "").split("T")[0]
            min_temp = tomorrow.get("Temperature", {}).get("Minimum", {}).get("Value", "N/A")
            max_temp = tomorrow.get("Temperature", {}).get("Maximum", {}).get("Value", "N/A")
            day_condition = tomorrow.get("Day", {}).get("IconPhrase", "N/A")
            night_condition = tomorrow.get("Night", {}).get("IconPhrase", "N/A")
            rain_prob = tomorrow.get("Day", {}).get("RainProbability", "N/A")
            
            response = f"Tomorrow's forecast for {location_name} ({date}):\n"
            response += f"• Temperature: {min_temp}°F to {max_temp}°F\n"
            response += f"• Conditions: {day_condition}\n"
            response += f"• Chance of rain: {rain_prob}%\n"
            response += f"• Night: {night_condition}\n"
            
            return response
        
        # Regular 5-day forecast
        response = f"5-Day Forecast for {location_name}:\n"
        response += f"Summary: {headline}\n\n"
        
        for day in daily_forecasts:
            date = day.get("Date", "").split("T")[0]
            min_temp = day.get("Temperature", {}).get("Minimum", {}).get("Value", "N/A")
            max_temp = day.get("Temperature", {}).get("Maximum", {}).get("Value", "N/A")
            day_condition = day.get("Day", {}).get("IconPhrase", "N/A")
            night_condition = day.get("Night", {}).get("IconPhrase", "N/A")
            
            response += f"Date: {date}\n"
            response += f"• Temperature: {min_temp}°F to {max_temp}°F\n"
            response += f"• Day: {day_condition}\n"
            response += f"• Night: {night_condition}\n\n"
        
        return response
    except Exception as e:
        return f"Error formatting forecast data: {e}"

def format_historical_for_user(historical_data: Dict[str, Any], location_name: str) -> str:
    """
    Format historical weather data into a user-friendly response
    
    Args:
        historical_data: Historical weather data from AccuWeather
        location_name: Name of the location
        
    Returns:
        Formatted string with historical weather information
    """
    if "error" in historical_data:
        return f"Sorry, I couldn't get the historical weather information: {historical_data['error']}"
    
    try:
        if not isinstance(historical_data, list) or len(historical_data) == 0:
            return f"No historical weather data available for {location_name}"
        
        response = f"Historical weather for {location_name} (past 24 hours):\n\n"
        
        for i, record in enumerate(historical_data[:5]):  # Limit to 5 records for readability
            time = record.get("LocalObservationDateTime", "").split("T")[1].split("+")[0]
            weather_text = record.get("WeatherText", "Unknown conditions")
            temp_f = record.get("Temperature", {}).get("Imperial", {}).get("Value", "N/A")
            temp_c = record.get("Temperature", {}).get("Metric", {}).get("Value", "N/A")
            
            response += f"Time: {time}\n"
            response += f"• Condition: {weather_text}\n"
            response += f"• Temperature: {temp_f}°F ({temp_c}°C)\n\n"
        
        return response
    except Exception as e:
        return f"Error formatting historical data: {e}"
