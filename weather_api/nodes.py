"""
PocketFlow nodes for the Weather API POC
"""
from pocketflow import BaseNode
from typing import Dict, Any
from .utils import (
    extract_weather_parameters,
    get_location_key,
    get_current_weather,
    get_forecast,
    get_historical_weather,
    format_current_weather_for_user,
    format_forecast_for_user,
    format_historical_for_user
)

class InputNode(BaseNode):
    """Node to handle user input and initialize the flow"""
    def prep(self, shared):
        # Get user query from shared context
        user_query = shared.get("user_query", "")
        return {"user_query": user_query}
    
    def exec(self, prep_res):
        # Just pass through the user query
        return prep_res
    
    def post(self, shared, prep_res, exec_res):
        # Store user query in shared context
        shared["user_query"] = exec_res["user_query"]
        return "default"  # Return a string action instead of a dict

class ParameterExtractionNode(BaseNode):
    """Node to extract parameters from user query"""
    def prep(self, shared):
        # Get user query from shared context
        user_query = shared.get("user_query", "")
        return {"user_query": user_query}
    
    def exec(self, prep_res):
        # Extract parameters from user query
        user_query = prep_res["user_query"]
        parameters = extract_weather_parameters(user_query)
        return {"parameters": parameters}
    
    def post(self, shared, prep_res, exec_res):
        # Store extracted parameters in shared context
        shared["parameters"] = exec_res["parameters"]
        return "default"  # Return a string action instead of a dict

class LocationResolverNode(BaseNode):
    """Node to resolve location using WeatherAPI.com"""
    def prep(self, shared):
        # Get parameters from shared context
        parameters = shared.get("parameters", {})
        location = parameters.get("location", "")
        provider = shared.get("provider", "api")  # Default to API if not specified
        
        return {"location": location, "provider": provider}
    
    def exec(self, prep_res):
        # Get location information from WeatherAPI.com if using API provider
        location = prep_res["location"]
        provider = prep_res["provider"]
        
        # If using MCP, we don't need to resolve location here
        if provider == "mcp":
            return {"location_data": {"name": location}}
        
        # Otherwise, validate location with WeatherAPI.com
        location_data = get_location_key(location)
        
        return {"location_data": location_data}
    
    def post(self, shared, prep_res, exec_res):
        # Store location data in shared context
        location_data = exec_res["location_data"]
        provider = prep_res["provider"]
        
        # If using MCP, route to MCP weather node
        if provider == "mcp":
            shared["location_name"] = location_data["name"]
            return "mcp"
        
        # Otherwise, handle API provider
        if "error" in location_data:
            shared["error"] = location_data["error"]
            return "error"
        
        # Store location name for WeatherAPI.com (no location key needed)
        shared["location_name"] = location_data["name"]
        shared["location_region"] = location_data.get("region", "")
        shared["location_country"] = location_data.get("country", "")
        
        return "success"

class CurrentWeatherNode(BaseNode):
    """Node to get current weather conditions"""
    def prep(self, shared):
        # Get location name from shared context
        location_name = shared.get("location_name")
        return {"location_name": location_name}
    
    def exec(self, prep_res):
        # Get current weather from WeatherAPI.com
        location_name = prep_res["location_name"]
        weather_data = get_current_weather(location_name)
        return {"weather_data": weather_data}
    
    def post(self, shared, prep_res, exec_res):
        # Store weather data in shared context
        shared["current_weather"] = exec_res["weather_data"]
        
        # Format weather data for user
        formatted_response = format_current_weather_for_user(
            exec_res["weather_data"], 
            prep_res["location_name"]
        )
        
        shared["current_weather_response"] = formatted_response
        
        # Return a string action based on timeframe
        timeframe = shared.get("parameters", {}).get("timeframe", "current")
        if timeframe == "week" or timeframe == "tomorrow":
            return "forecast"
        elif timeframe == "historical":
            return "historical"
        else:
            return "done"

class ForecastNode(BaseNode):
    """Node to get weather forecast"""
    def prep(self, shared):
        # Get location name from shared context
        location_name = shared.get("location_name")
        return {"location_name": location_name}
    
    def exec(self, prep_res):
        # Get forecast from WeatherAPI.com
        location_name = prep_res["location_name"]
        forecast_data = get_forecast(location_name)
        return {"forecast_data": forecast_data}
    
    def post(self, shared, prep_res, exec_res):
        # Store forecast data in shared context
        shared["forecast"] = exec_res["forecast_data"]
        
        # Get timeframe from parameters
        timeframe = shared.get("parameters", {}).get("timeframe", "week")
        
        # Format forecast data for user
        formatted_response = format_forecast_for_user(
            exec_res["forecast_data"], 
            prep_res["location_name"],
            timeframe
        )
        
        shared["forecast_response"] = formatted_response
        return "default"  # Return a string action instead of a dict

class HistoricalWeatherNode(BaseNode):
    """Node to get historical weather data"""
    def prep(self, shared):
        # Get location name from shared context
        location_name = shared.get("location_name")
        return {"location_name": location_name}
    
    def exec(self, prep_res):
        # Get historical weather from WeatherAPI.com
        location_name = prep_res["location_name"]
        historical_data = get_historical_weather(location_name)
        return {"historical_data": historical_data}
    
    def post(self, shared, prep_res, exec_res):
        # Store historical data in shared context
        shared["historical_weather"] = exec_res["historical_data"]
        
        # Format historical data for user
        formatted_response = format_historical_for_user(
            exec_res["historical_data"], 
            prep_res["location_name"]
        )
        
        shared["historical_response"] = formatted_response
        return "default"  # Return a string action instead of a dict

class ResponseFormatterNode(BaseNode):
    """Node to format the final response to the user"""
    def prep(self, shared):
        # Get parameters and any available responses
        parameters = shared.get("parameters", {})
        timeframe = parameters.get("timeframe", "current")
        provider = shared.get("provider", "api")
        
        # Get API responses
        current_weather_response = shared.get("current_weather_response", "")
        forecast_response = shared.get("forecast_response", "")
        historical_response = shared.get("historical_response", "")
        
        # Get MCP weather data
        mcp_weather = shared.get("mcp_weather", {})
        
        return {
            "timeframe": timeframe,
            "provider": provider,
            "current_weather_response": current_weather_response,
            "forecast_response": forecast_response,
            "historical_response": historical_response,
            "mcp_weather": mcp_weather
        }
    
    def exec(self, prep_res):
        # Determine which response to use based on provider and timeframe
        timeframe = prep_res["timeframe"]
        provider = prep_res["provider"]
        current_weather_response = prep_res["current_weather_response"]
        forecast_response = prep_res["forecast_response"]
        historical_response = prep_res["historical_response"]
        mcp_weather = prep_res["mcp_weather"]
        
        if provider == "mcp":
            # Handle MCP weather responses
            if timeframe == "current":
                return {"final_response": self._format_mcp_current(mcp_weather)}
            elif timeframe == "tomorrow":
                return {"final_response": self._format_mcp_tomorrow(mcp_weather)}
            elif timeframe == "week":
                return {"final_response": self._format_mcp_week(mcp_weather)}
            elif timeframe == "historical":
                return {"final_response": self._format_mcp_historical(mcp_weather)}
            else:
                return {"final_response": "Sorry, I couldn't process your weather query."}
        else:
            # Handle API weather responses
            if timeframe == "current":
                return {"final_response": current_weather_response}
            elif timeframe == "tomorrow" or timeframe == "week":
                return {"final_response": forecast_response}
            elif timeframe == "historical":
                return {"final_response": historical_response}
            else:
                return {"final_response": current_weather_response}
    
    def _format_mcp_current(self, weather_data):
        """Format MCP current weather data"""
        if not weather_data or "current_conditions" not in weather_data:
            return "Sorry, I couldn't get the current weather information."
        
        current = weather_data["current_conditions"]
        location = weather_data.get("location", "Unknown location")
        region = weather_data.get("region", "")
        country = weather_data.get("country", "")
        
        temp = current.get("temperature", {})
        temp_value = temp.get("value", "N/A")
        temp_unit = temp.get("unit", "C")
        weather_text = current.get("weather_text", "Unknown conditions")
        humidity = current.get("relative_humidity", "N/A")
        wind = current.get("wind", {})
        wind_speed = wind.get("speed", "N/A")
        wind_dir = wind.get("direction", "N/A")
        precip = current.get("precipitation", "N/A")
        obs_time = current.get("observation_time", "N/A")
        
        response = f"Current weather for {location}, {region}, {country}:\n"
        response += f"• Condition: {weather_text}\n"
        response += f"• Temperature: {temp_value}°{temp_unit}\n"
        response += f"• Humidity: {humidity}%\n"
        response += f"• Wind: {wind_speed} km/h {wind_dir}\n"
        response += f"• Precipitation: {precip} mm\n"
        response += f"• Observation time: {obs_time}\n"
        
        return response
    
    def _format_mcp_tomorrow(self, weather_data):
        """Format MCP tomorrow's weather data"""
        forecast = weather_data.get("forecast", [])
        location = weather_data.get("location", "Unknown location")
        region = weather_data.get("region", "")
        country = weather_data.get("country", "")
        
        if not forecast or len(forecast) < 2:
            return f"Sorry, I couldn't get tomorrow's weather forecast."
        
        tomorrow = forecast[1]  # Second day is tomorrow
        date = tomorrow.get("date", "tomorrow")
        max_temp_c = tomorrow.get("max_temp_c", "N/A")
        min_temp_c = tomorrow.get("min_temp_c", "N/A")
        condition = tomorrow.get("condition", "Unknown conditions")
        chance_of_rain = tomorrow.get("chance_of_rain", "N/A")
        chance_of_snow = tomorrow.get("chance_of_snow", "N/A")
        
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%A, %B %d")
        except:
            formatted_date = date
        
        response = f"Tomorrow's forecast for {location}, {region}, {country} ({formatted_date}):\n"
        response += f"• Condition: {condition}\n"
        response += f"• High: {max_temp_c}°C\n"
        response += f"• Low: {min_temp_c}°C\n"
        response += f"• Chance of rain: {chance_of_rain}%\n"
        response += f"• Chance of snow: {chance_of_snow}%\n"
        return response
    
    def _format_mcp_week(self, weather_data):
        """Format MCP weekly weather data"""
        forecast = weather_data.get("forecast", [])
        location = weather_data.get("location", "Unknown location")
        region = weather_data.get("region", "")
        country = weather_data.get("country", "")
        
        if not forecast:
            return "Sorry, I couldn't get the weekly weather forecast."
        
        response = f"Weather forecast for {location}, {region}, {country} (up to {len(forecast)} days):\n\n"
        for day in forecast:
            date = day.get("date", "Unknown")
            condition = day.get("condition", "Unknown conditions")
            max_temp_c = day.get("max_temp_c", "N/A")
            min_temp_c = day.get("min_temp_c", "N/A")
            chance_of_rain = day.get("chance_of_rain", "N/A")
            chance_of_snow = day.get("chance_of_snow", "N/A")
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%A, %B %d")
            except:
                formatted_date = date
            response += f"📅 {formatted_date}:\n"
            response += f"   • Condition: {condition}\n"
            response += f"   • High: {max_temp_c}°C\n"
            response += f"   • Low: {min_temp_c}°C\n"
            response += f"   • Chance of rain: {chance_of_rain}%\n"
            response += f"   • Chance of snow: {chance_of_snow}%\n\n"
        return response.strip()
    
    def _format_mcp_historical(self, weather_data):
        """Format MCP historical weather data"""
        if not weather_data or "historical" not in weather_data:
            return "Sorry, I couldn't get the historical weather information."
        
        historical = weather_data["historical"]
        location = weather_data.get("location", "Unknown location")
        
        response = f"Historical weather for {location}:\n"
        response += f"• Date: {historical.get('date', 'N/A')}\n"
        response += f"• High: {historical.get('high', 'N/A')}°F\n"
        response += f"• Low: {historical.get('low', 'N/A')}°F\n"
        response += f"• Condition: {historical.get('condition', 'N/A')}\n"
        
        return response
    
    def post(self, shared, prep_res, exec_res):
        # Store final response in shared context
        shared["final_response"] = exec_res["final_response"]
        return "default"  # Return a string action instead of a dict

class ErrorHandlerNode(BaseNode):
    """Node to handle errors and format error messages"""
    def prep(self, shared):
        # Get error message if any
        error = shared.get("error", "Unknown error occurred")
        return {"error": error}
    
    def exec(self, prep_res):
        # Format error message
        error = prep_res["error"]
        error_response = f"Sorry, I encountered an error: {error}"
        return {"error_response": error_response}
    
    def post(self, shared, prep_res, exec_res):
        # Store error response in shared context
        shared["error_response"] = exec_res["error_response"]
        shared["final_response"] = exec_res["error_response"]
        return "default"  # Return a string action instead of a dict
