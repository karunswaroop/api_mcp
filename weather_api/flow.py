"""
PocketFlow flow definition for the Weather API POC
"""
from pocketflow import Flow
from .nodes import (
    InputNode,
    ParameterExtractionNode,
    LocationResolverNode,
    CurrentWeatherNode,
    ForecastNode,
    HistoricalWeatherNode,
    ResponseFormatterNode,
    ErrorHandlerNode
)

def create_weather_flow():
    """
    Create and configure the weather flow
    
    Returns:
        Configured PocketFlow flow
    """
    # Create flow
    flow = Flow()
    
    # Create nodes
    input_node = InputNode()
    param_extraction = ParameterExtractionNode()
    location_resolver = LocationResolverNode()
    current_weather = CurrentWeatherNode()
    forecast = ForecastNode()
    historical = HistoricalWeatherNode()
    response_formatter = ResponseFormatterNode()
    error_handler = ErrorHandlerNode()
    
    # Connect nodes
    flow.start(input_node)
    
    # Main flow
    input_node.next(param_extraction)
    param_extraction.next(location_resolver)
    
    # Handle location resolution success or error
    location_resolver - "success" >> current_weather
    location_resolver - "error" >> error_handler
    
    # Connect weather nodes based on timeframe
    current_weather.next(response_formatter)
    forecast.next(response_formatter)
    historical.next(response_formatter)
    
    # The CurrentWeatherNode now handles this logic directly in its post method
    
    # Add conditional transitions from current weather node
    current_weather - "forecast" >> forecast
    current_weather - "historical" >> historical
    current_weather - "done" >> response_formatter
    
    # ForecastNode and HistoricalWeatherNode now handle this logic directly in their post methods
    
    return flow

def process_weather_query(query: str) -> str:
    """
    Process a weather query using the PocketFlow
    
    Args:
        query: User's natural language query about weather
        
    Returns:
        Formatted response to the user's query
    """
    # Create shared context
    shared = {"user_query": query}
    
    # Create flow
    flow = create_weather_flow()
    
    # Run flow
    print(f"DEBUG: Processing query: {query}")
    flow.run(shared)
    
    # Print debug info
    print(f"DEBUG: Parameters: {shared.get('parameters', {})}")
    print(f"DEBUG: Current weather response: {shared.get('current_weather_response', 'None')}")
    print(f"DEBUG: Forecast response: {shared.get('forecast_response', 'None')}")
    print(f"DEBUG: Final response: {shared.get('final_response', 'None')}")
    
    # Return final response
    return shared.get("final_response", "Sorry, I couldn't process your weather query.")
