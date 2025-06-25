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
from .mcp_nodes import MCPWeatherNode
from .ai_summary_node import AISummaryNode

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
    mcp_weather = MCPWeatherNode()
    response_formatter = ResponseFormatterNode()
    ai_summary = AISummaryNode()
    error_handler = ErrorHandlerNode()
    
    # Connect nodes
    flow.start(input_node)
    
    # Main flow
    input_node.next(param_extraction)
    param_extraction.next(location_resolver)
    
    # Handle location resolution success or error
    location_resolver - "success" >> current_weather
    location_resolver - "error" >> error_handler
    
    # Connect API weather nodes based on timeframe
    current_weather.next(response_formatter)
    forecast.next(response_formatter)
    historical.next(response_formatter)
    
    # Connect response formatter to AI summary
    response_formatter.next(ai_summary)
    
    # Connect MCP weather node with specific actions
    mcp_weather - "current" >> response_formatter
    mcp_weather - "tomorrow" >> response_formatter
    mcp_weather - "week" >> response_formatter
    mcp_weather - "historical" >> response_formatter
    mcp_weather - "success" >> response_formatter
    mcp_weather - "error" >> error_handler
    
    # Add conditional transitions from current weather node
    current_weather - "forecast" >> forecast
    current_weather - "historical" >> historical
    current_weather - "done" >> response_formatter
    
    # Add conditional transitions from location resolver to MCP weather
    # This will be used when provider is set to "mcp"
    location_resolver - "mcp" >> mcp_weather
    
    return flow

def process_weather_query(query: str, provider: str = "api") -> str:
    """
    Process a weather query using the PocketFlow
    
    Args:
        query: User's natural language query about weather
        provider: Weather data provider to use ("api" or "mcp")
        
    Returns:
        Formatted response to the user's query
    """
    # Create shared context
    shared = {
        "user_query": query,
        "provider": provider
    }
    
    # Create flow
    flow = create_weather_flow()
    
    # Run flow
    print(f"DEBUG: Processing query: {query} with provider: {provider}")
    flow.run(shared)
    
    # Print debug info
    print(f"DEBUG: Parameters: {shared.get('parameters', {})}")
    print(f"DEBUG: Provider: {shared.get('provider', 'api')}")
    print(f"DEBUG: Current weather response: {shared.get('current_weather_response', 'None')}")
    print(f"DEBUG: Forecast response: {shared.get('forecast_response', 'None')}")
    print(f"DEBUG: MCP weather data: {shared.get('mcp_weather', {})}")
    print(f"DEBUG: Final response: {shared.get('final_response', 'None')}")
    print(f"DEBUG: AI summary: {shared.get('ai_summary', 'None')}")
    print(f"DEBUG: Error message: {shared.get('error_message', 'None')}")
    print(f"DEBUG: Error response: {shared.get('error_response', 'None')}")
    
    
    # Return final response
    return shared.get("final_response", "Sorry, I couldn't process your weather query.")
