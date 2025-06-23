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
    """Node to resolve location to AccuWeather location key"""
    def prep(self, shared):
        # Get location from parameters
        parameters = shared.get("parameters", {})
        location = parameters.get("location", "New York")
        return {"location": location}
    
    def exec(self, prep_res):
        # Get location key from AccuWeather API
        location = prep_res["location"]
        location_key = get_location_key(location)
        return {"location_key": location_key, "location_name": location}
    
    def post(self, shared, prep_res, exec_res):
        # Store location key in shared context
        shared["location_key"] = exec_res["location_key"]
        shared["location_name"] = exec_res["location_name"]
        
        # Determine next action based on whether location was found
        if exec_res["location_key"] is None:
            shared["error_message"] = f"Could not find location: {prep_res['location']}"
            return "error"
        return "success"

class CurrentWeatherNode(BaseNode):
    """Node to get current weather conditions"""
    def prep(self, shared):
        # Get location key from shared context
        location_key = shared.get("location_key")
        location_name = shared.get("location_name")
        return {"location_key": location_key, "location_name": location_name}
    
    def exec(self, prep_res):
        # Get current weather from AccuWeather API
        location_key = prep_res["location_key"]
        weather_data = get_current_weather(location_key)
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
        # Get location key from shared context
        location_key = shared.get("location_key")
        location_name = shared.get("location_name")
        return {"location_key": location_key, "location_name": location_name}
    
    def exec(self, prep_res):
        # Get forecast from AccuWeather API
        location_key = prep_res["location_key"]
        forecast_data = get_forecast(location_key)
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
        # Get location key from shared context
        location_key = shared.get("location_key")
        location_name = shared.get("location_name")
        return {"location_key": location_key, "location_name": location_name}
    
    def exec(self, prep_res):
        # Get historical weather from AccuWeather API
        location_key = prep_res["location_key"]
        historical_data = get_historical_weather(location_key)
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
        
        current_weather_response = shared.get("current_weather_response", "")
        forecast_response = shared.get("forecast_response", "")
        historical_response = shared.get("historical_response", "")
        
        return {
            "timeframe": timeframe,
            "current_weather_response": current_weather_response,
            "forecast_response": forecast_response,
            "historical_response": historical_response
        }
    
    def exec(self, prep_res):
        # Determine which response to use based on timeframe
        timeframe = prep_res["timeframe"]
        
        if timeframe == "week" or timeframe == "tomorrow":
            response = prep_res["forecast_response"]
        elif timeframe == "historical":
            response = prep_res["historical_response"]
        else:  # current
            response = prep_res["current_weather_response"]
        
        return {"final_response": response}
    
    def post(self, shared, prep_res, exec_res):
        # Store final response in shared context
        shared["final_response"] = exec_res["final_response"]
        return "default"  # Return a string action instead of a dict

class ErrorHandlerNode(BaseNode):
    """Node to handle errors in the flow"""
    def prep(self, shared):
        # Get error message if any
        error_message = shared.get("error_message", "")
        return {"error_message": error_message}
    
    def exec(self, prep_res):
        # Format error message
        error_message = prep_res["error_message"]
        if not error_message:
            error_message = "An unknown error occurred while processing your request."
        
        return {"error_response": f"Sorry, I encountered an issue: {error_message}"}
    
    def post(self, shared, prep_res, exec_res):
        # Store error response in shared context
        shared["final_response"] = exec_res["error_response"]
        return "default"  # Return a string action instead of a dict
