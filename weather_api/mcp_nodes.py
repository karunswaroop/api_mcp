"""
MCP-based weather nodes for the Weather API POC
Custom implementation without external mcp-weather dependency
"""
import os
import json
import requests
from typing import Dict, Any
from datetime import datetime, timedelta
from pocketflow import BaseNode
from dotenv import load_dotenv
from .utils import extract_weather_parameters

# Load environment variables
load_dotenv()

# WeatherAPI.com API key
WEATHERAPI_KEY = os.getenv('WEATHERAPI_KEY')
WEATHERAPI_BASE_URL = 'http://api.weatherapi.com/v1'

class MCPWeatherNode(BaseNode):
    """Node to get weather data from MCP (custom implementation)"""
    def prep(self, shared):
        # Get parameters from shared context
        parameters = shared.get("parameters", {})
        location = parameters.get("location", "")
        timeframe = parameters.get("timeframe", "current")
        
        return {
            "location": location,
            "timeframe": timeframe
        }
    
    def _get_location_info(self, location):
        """Get location information from WeatherAPI.com"""
        params = {
            "key": WEATHERAPI_KEY,
            "q": location
        }
        
        try:
            response = requests.get(f"{WEATHERAPI_BASE_URL}/search.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                return {
                    "name": data[0]["name"],
                    "region": data[0]["region"],
                    "country": data[0]["country"],
                    "lat": data[0]["lat"],
                    "lon": data[0]["lon"]
                }
            return {"error": f"Location '{location}' not found"}
        except Exception as e:
            error_msg = f"Error getting location info: {e}"
            print(error_msg)
            return {"error": error_msg}
    
    def _get_current_conditions(self, location):
        """Get current weather conditions from WeatherAPI.com"""
        params = {
            "key": WEATHERAPI_KEY,
            "q": location,
            "aqi": "yes"  # Include air quality data
        }
        
        try:
            response = requests.get(f"{WEATHERAPI_BASE_URL}/current.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and "current" in data:
                current = data["current"]
                location_data = data["location"]
                
                return {
                    "temperature": {
                        "value": current["temp_c"],
                        "unit": "C"
                    },
                    "weather_text": current["condition"]["text"],
                    "relative_humidity": current.get("humidity"),
                    "precipitation": current.get("precip_mm"),
                    "wind": {
                        "speed": current.get("wind_kph"),
                        "direction": current.get("wind_dir")
                    },
                    "observation_time": current["last_updated"],
                    "location": {
                        "name": location_data["name"],
                        "region": location_data["region"],
                        "country": location_data["country"]
                    }
                }
            return {"error": "No current conditions available"}
        except Exception as e:
            error_msg = f"Error getting current conditions: {e}"
            print(error_msg)
            return {"error": error_msg}
    
    def _get_forecast(self, location, days=3):
        """Get weather forecast from WeatherAPI.com"""
        params = {
            "key": WEATHERAPI_KEY,
            "q": location,
            "days": days,
            "aqi": "yes",
            "alerts": "yes"
        }
        
        try:
            response = requests.get(f"{WEATHERAPI_BASE_URL}/forecast.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and "forecast" in data and "forecastday" in data["forecast"]:
                forecast_days = []
                
                for day in data["forecast"]["forecastday"]:
                    day_data = {
                        "date": day["date"],
                        "max_temp_c": day["day"]["maxtemp_c"],
                        "min_temp_c": day["day"]["mintemp_c"],
                        "avg_temp_c": day["day"]["avgtemp_c"],
                        "condition": day["day"]["condition"]["text"],
                        "chance_of_rain": day["day"]["daily_chance_of_rain"],
                        "chance_of_snow": day["day"]["daily_chance_of_snow"],
                        "hourly": []
                    }
                    
                    # Add hourly forecast data
                    for hour in day["hour"]:
                        hour_data = {
                            "time": hour["time"],
                            "temp_c": hour["temp_c"],
                            "condition": hour["condition"]["text"],
                            "wind_kph": hour["wind_kph"],
                            "wind_dir": hour["wind_dir"],
                            "precip_mm": hour["precip_mm"],
                            "humidity": hour["humidity"],
                            "chance_of_rain": hour["chance_of_rain"],
                            "chance_of_snow": hour["chance_of_snow"]
                        }
                        day_data["hourly"].append(hour_data)
                    
                    forecast_days.append(day_data)
                
                return forecast_days
            return {"error": "No forecast data available"}
        except Exception as e:
            error_msg = f"Error getting forecast: {e}"
            print(error_msg)
            return {"error": error_msg}
    
    def _get_mcp_weather(self, location):
        """Get weather data using MCP approach with WeatherAPI.com"""
        try:
            # Get current conditions (includes location info)
            current_data = self._get_current_conditions(location)
            if "error" in current_data:
                return {"error": current_data["error"]}
            
            # Get forecast data
            forecast_data = self._get_forecast(location)
            if isinstance(forecast_data, dict) and "error" in forecast_data:
                # If forecast fails, we can still return current conditions
                forecast_data = []
            
            # Format response for MCP
            return {
                "location": current_data["location"]["name"],
                "region": current_data["location"]["region"],
                "country": current_data["location"]["country"],
                "current_conditions": {
                    "temperature": current_data["temperature"],
                    "weather_text": current_data["weather_text"],
                    "relative_humidity": current_data["relative_humidity"],
                    "precipitation": current_data["precipitation"],
                    "wind": current_data["wind"],
                    "observation_time": current_data["observation_time"]
                },
                "forecast": forecast_data
            }
        except Exception as e:
            return {"error": f"Error getting weather data from MCP: {str(e)}"}
            
    def _get_historical_weather(self, location, days=1):
        """Get historical weather data from WeatherAPI.com"""
        params = {
            "key": WEATHERAPI_KEY,
            "q": location,
            "dt": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        }
        
        try:
            response = requests.get(f"{WEATHERAPI_BASE_URL}/history.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and "forecast" in data and "forecastday" in data["forecast"]:
                return data["forecast"]["forecastday"]
            return {"error": "No historical data available"}
        except Exception as e:
            error_msg = f"Error getting historical weather: {e}"
            print(error_msg)
            return {"error": error_msg}
    
    def exec(self, prep_res):
        # Get weather using our custom MCP approach
        location = prep_res["location"]
        weather_data = self._get_mcp_weather(location)
        return {"weather_data": weather_data}
    
    def post(self, shared, prep_res, exec_res):
        """Post-execution processing"""
        # Store the weather data in the shared context
        weather_data = exec_res.get("weather_data", {})
        shared["mcp_weather"] = weather_data
        
        # Return action based on timeframe
        timeframe = prep_res.get("timeframe", "current")
        
        if "error" in weather_data:
            shared["error_message"] = weather_data["error"]
            return "error"
        elif timeframe == "current":
            return "current"
        elif timeframe == "tomorrow":
            return "tomorrow"
        elif timeframe == "week":
            return "week"
        elif timeframe == "historical":
            return "historical"
        else:
            return "success"
    
    def _convert_c_to_f(self, celsius):
        """Convert Celsius to Fahrenheit"""
        return round((celsius * 9/5) + 32, 1)
