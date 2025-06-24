"""
Utility functions for the Weather API POC
"""
import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Get API key from environment variables
WEATHERAPI_API_KEY = os.getenv("WEATHERAPI_KEY")

# WeatherAPI.com API base URL
WEATHERAPI_BASE_URL = "http://api.weatherapi.com/v1"

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
    elif (
        "week" in query or
        "5 day" in query or "5-day" in query or
        "3 day" in query or "3-day" in query or
        "three day" in query or "three-day" in query or
        "forecast" in query
    ):
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

def get_location_key(location: str) -> Dict[str, Any]:
    """
    Get location information for a given location name from WeatherAPI.com
    Note: WeatherAPI.com doesn't require a separate location key lookup,
    but we'll validate the location exists by making a current weather call
    
    Args:
        location: Name of the location (city, etc.)
        
    Returns:
        Dictionary with location name if found, error otherwise
    """
    try:
        # Make a test call to validate location
        params = {
            "key": WEATHERAPI_API_KEY,
            "q": location,
            "aqi": "no"
        }
        
        response = requests.get(f"{WEATHERAPI_BASE_URL}/current.json", params=params)
        response.raise_for_status()
        
        data = response.json()
        if "error" in data:
            return {"error": f"Location '{location}' not found: {data['error']['message']}"}
        
        return {
            "name": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"]
        }
    except Exception as e:
        error_msg = f"Error validating location: {e}"
        print(error_msg)
        return {"error": error_msg}

def get_current_weather(location: str) -> Dict[str, Any]:
    """
    Get current weather conditions for a location
    
    Args:
        location: Location name or coordinates
        
    Returns:
        Dictionary with current weather data
    """
    params = {
        "key": WEATHERAPI_API_KEY,
        "q": location,
        "aqi": "no"
    }
    
    try:
        response = requests.get(f"{WEATHERAPI_BASE_URL}/current.json", params=params)
        response.raise_for_status()
        
        data = response.json()
        if "error" in data:
            return {"error": f"Error getting current weather: {data['error']['message']}"}
        
        return data
    except Exception as e:
        return {"error": f"Error getting current weather: {e}"}

def get_forecast(location: str) -> Dict[str, Any]:
    """
    Get 3-day forecast for a location
    
    Args:
        location: Location name or coordinates
        
    Returns:
        Dictionary with forecast data
    """
    params = {
        "key": WEATHERAPI_API_KEY,
        "q": location,
        "days": 3,
        "aqi": "no",
        "alerts": "no"
    }
    
    try:
        response = requests.get(f"{WEATHERAPI_BASE_URL}/forecast.json", params=params)
        response.raise_for_status()
        
        data = response.json()
        if "error" in data:
            return {"error": f"Error getting forecast: {data['error']['message']}"}
        
        return data
    except Exception as e:
        return {"error": f"Error getting forecast: {e}"}

def get_historical_weather(location: str) -> Dict[str, Any]:
    """
    Get historical weather data for a location (yesterday)
    
    Args:
        location: Location name or coordinates
        
    Returns:
        Dictionary with historical weather data
    """
    # Get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    
    params = {
        "key": WEATHERAPI_API_KEY,
        "q": location,
        "dt": date_str
    }
    
    try:
        response = requests.get(f"{WEATHERAPI_BASE_URL}/history.json", params=params)
        response.raise_for_status()
        
        data = response.json()
        if "error" in data:
            return {"error": f"Error getting historical weather: {data['error']['message']}"}
        
        return data
    except Exception as e:
        return {"error": f"Error getting historical weather: {e}"}

def format_current_weather_for_user(weather_data: Dict[str, Any], location_name: str) -> str:
    """
    Format current weather data into a user-friendly response
    
    Args:
        weather_data: Current weather data from WeatherAPI.com
        location_name: Name of the location
        
    Returns:
        Formatted string with weather information
    """
    if "error" in weather_data:
        return f"Sorry, I couldn't get the weather information: {weather_data['error']}"
    
    try:
        current = weather_data.get("current", {})
        location = weather_data.get("location", {})
        
        condition = current.get("condition", {}).get("text", "Unknown conditions")
        temp_f = current.get("temp_f", "N/A")
        temp_c = current.get("temp_c", "N/A")
        humidity = current.get("humidity", "N/A")
        wind_mph = current.get("wind_mph", "N/A")
        wind_kph = current.get("wind_kph", "N/A")
        wind_dir = current.get("wind_dir", "N/A")
        feels_like_f = current.get("feelslike_f", "N/A")
        feels_like_c = current.get("feelslike_c", "N/A")
        uv = current.get("uv", "N/A")
        visibility_miles = current.get("vis_miles", "N/A")
        
        response = f"Current weather for {location_name}:\n"
        response += f"• Condition: {condition}\n"
        response += f"• Temperature: {temp_f}°F ({temp_c}°C)\n"
        response += f"• Feels like: {feels_like_f}°F ({feels_like_c}°C)\n"
        response += f"• Humidity: {humidity}%\n"
        response += f"• Wind: {wind_mph} mph ({wind_kph} km/h) {wind_dir}\n"
        response += f"• UV Index: {uv}\n"
        response += f"• Visibility: {visibility_miles} miles\n"
        
        return response
    except Exception as e:
        return f"Error formatting weather data: {e}"

def format_forecast_for_user(forecast_data: Dict[str, Any], location_name: str, timeframe: str = "week") -> str:
    """
    Format forecast data into a user-friendly response
    
    Args:
        forecast_data: Forecast data from WeatherAPI.com
        location_name: Name of the location
        timeframe: Time frame for the forecast
        
    Returns:
        Formatted string with forecast information
    """
    if "error" in forecast_data:
        return f"Sorry, I couldn't get the forecast: {forecast_data['error']}"
    
    try:
        forecast_days = forecast_data.get("forecast", {}).get("forecastday", [])
        
        if not forecast_days:
            return f"No forecast data available for {location_name}"
        
        # If the user asked for tomorrow, only show the second day
        if timeframe == "tomorrow" and len(forecast_days) > 1:
            day = forecast_days[1]
            date = day.get("date", "Unknown")
            day_info = day.get("day", {})
            astro = day.get("astro", {})
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%A, %B %d")
            except:
                formatted_date = date
            condition = day_info.get("condition", {}).get("text", "Unknown")
            max_temp_f = day_info.get("maxtemp_f", "N/A")
            min_temp_f = day_info.get("mintemp_f", "N/A")
            max_temp_c = day_info.get("maxtemp_c", "N/A")
            min_temp_c = day_info.get("mintemp_c", "N/A")
            avg_humidity = day_info.get("avghumidity", "N/A")
            total_precip_mm = day_info.get("totalprecip_mm", "N/A")
            total_precip_in = day_info.get("totalprecip_in", "N/A")
            max_wind_mph = day_info.get("maxwind_mph", "N/A")
            max_wind_kph = day_info.get("maxwind_kph", "N/A")
            response = f"Tomorrow's forecast for {location_name} ({formatted_date}):\n"
            response += f"• Condition: {condition}\n"
            response += f"• High: {max_temp_f}°F ({max_temp_c}°C)\n"
            response += f"• Low: {min_temp_f}°F ({min_temp_c}°C)\n"
            response += f"• Humidity: {avg_humidity}%\n"
            response += f"• Precipitation: {total_precip_in} in ({total_precip_mm} mm)\n"
            response += f"• Max Wind: {max_wind_mph} mph ({max_wind_kph} km/h)\n"
            response += f"• Sunrise: {astro.get('sunrise', 'N/A')}\n"
            response += f"• Sunset: {astro.get('sunset', 'N/A')}\n"
            return response.strip()
        
        # Otherwise, show all days
        response = f"Weather forecast for {location_name}:\n\n"
        for day in forecast_days:
            date = day.get("date", "Unknown")
            day_info = day.get("day", {})
            astro = day.get("astro", {})
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%A, %B %d")
            except:
                formatted_date = date
            condition = day_info.get("condition", {}).get("text", "Unknown")
            max_temp_f = day_info.get("maxtemp_f", "N/A")
            min_temp_f = day_info.get("mintemp_f", "N/A")
            max_temp_c = day_info.get("maxtemp_c", "N/A")
            min_temp_c = day_info.get("mintemp_c", "N/A")
            avg_humidity = day_info.get("avghumidity", "N/A")
            total_precip_mm = day_info.get("totalprecip_mm", "N/A")
            total_precip_in = day_info.get("totalprecip_in", "N/A")
            max_wind_mph = day_info.get("maxwind_mph", "N/A")
            max_wind_kph = day_info.get("maxwind_kph", "N/A")
            response += f"📅 {formatted_date}:\n"
            response += f"   • {condition}\n"
            response += f"   • High: {max_temp_f}°F ({max_temp_c}°C)\n"
            response += f"   • Low: {min_temp_f}°F ({min_temp_c}°C)\n"
            response += f"   • Humidity: {avg_humidity}%\n"
            response += f"   • Precipitation: {total_precip_in} in ({total_precip_mm} mm)\n"
            response += f"   • Max Wind: {max_wind_mph} mph ({max_wind_kph} km/h)\n"
            response += f"   • Sunrise: {astro.get('sunrise', 'N/A')}\n"
            response += f"   • Sunset: {astro.get('sunset', 'N/A')}\n\n"
        return response.strip()
    except Exception as e:
        return f"Error formatting forecast data: {e}"

def format_historical_for_user(historical_data: Dict[str, Any], location_name: str) -> str:
    """
    Format historical weather data into a user-friendly response
    
    Args:
        historical_data: Historical weather data from WeatherAPI.com
        location_name: Name of the location
        
    Returns:
        Formatted string with historical weather information
    """
    if "error" in historical_data:
        return f"Sorry, I couldn't get the historical weather: {historical_data['error']}"
    
    try:
        forecast_day = historical_data.get("forecast", {}).get("forecastday", [])
        
        if not forecast_day:
            return f"No historical data available for {location_name}"
        
        day_data = forecast_day[0]
        day_info = day_data.get("day", {})
        date = day_data.get("date", "Unknown")
        
        # Parse date for better formatting
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%A, %B %d, %Y")
        except:
            formatted_date = date
        
        condition = day_info.get("condition", {}).get("text", "Unknown")
        max_temp_f = day_info.get("maxtemp_f", "N/A")
        min_temp_f = day_info.get("mintemp_f", "N/A")
        max_temp_c = day_info.get("maxtemp_c", "N/A")
        min_temp_c = day_info.get("mintemp_c", "N/A")
        avg_humidity = day_info.get("avghumidity", "N/A")
        total_precip_mm = day_info.get("totalprecip_mm", "N/A")
        total_precip_in = day_info.get("totalprecip_in", "N/A")
        max_wind_mph = day_info.get("maxwind_mph", "N/A")
        max_wind_kph = day_info.get("maxwind_kph", "N/A")
        
        response = f"Historical weather for {location_name} on {formatted_date}:\n\n"
        response += f"• Condition: {condition}\n"
        response += f"• High: {max_temp_f}°F ({max_temp_c}°C)\n"
        response += f"• Low: {min_temp_f}°F ({min_temp_c}°C)\n"
        response += f"• Average Humidity: {avg_humidity}%\n"
        response += f"• Total Precipitation: {total_precip_in} in ({total_precip_mm} mm)\n"
        response += f"• Max Wind: {max_wind_mph} mph ({max_wind_kph} km/h)\n"
        
        return response
    except Exception as e:
        return f"Error formatting historical data: {e}"
