# WeatherAPI.com Integration Setup

This document explains how to set up and use the WeatherAPI.com integration that has replaced the AccuWeather API in this project.

## Changes Made

### 1. API Integration
- **Replaced**: AccuWeather API with WeatherAPI.com
- **Updated**: All API endpoints and authentication methods
- **Improved**: Data formatting and error handling

### 2. Key Files Modified
- `weather_api/utils.py` - Complete rewrite of API functions
- `weather_api/nodes.py` - Updated to work with new API structure
- `app.py` - Fixed missing imports and error handling

### 3. New Features
- Better location validation
- Enhanced weather data formatting
- Improved error messages
- Support for both imperial and metric units
- More detailed weather information (UV index, visibility, etc.)

## Setup Instructions

### 1. Get WeatherAPI.com API Key
1. Visit [WeatherAPI.com](https://www.weatherapi.com/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. The free tier includes:
   - 1,000,000 calls per month
   - Current weather
   - 3-day forecast
   - Historical weather (last 7 days)

### 2. Configure Environment Variables
Create or update your `.env` file:

```bash
# Replace ACCUWEATHER_API_KEY with WEATHERAPI_API_KEY
WEATHERAPI_API_KEY=your_weatherapi_api_key_here

# Keep other environment variables as needed
PORT=5001
```

### 3. Install Dependencies
The existing dependencies should work fine, but make sure you have:

```bash
pip install -r requirements.txt
```

### 4. Test the Implementation
Run the test script to verify everything works:

```bash
python test_weatherapi.py
```

## API Endpoints Used

### Current Weather
- **Endpoint**: `http://api.weatherapi.com/v1/current.json`
- **Parameters**: `key`, `q` (location), `aqi` (air quality)

### Forecast
- **Endpoint**: `http://api.weatherapi.com/v1/forecast.json`
- **Parameters**: `key`, `q` (location), `days` (3), `aqi`, `alerts`

### Historical Weather
- **Endpoint**: `http://api.weatherapi.com/v1/history.json`
- **Parameters**: `key`, `q` (location), `dt` (date)

## Data Structure Changes

### Current Weather Response
```json
{
  "location": {
    "name": "New York",
    "region": "New York",
    "country": "United States of America"
  },
  "current": {
    "temp_f": 72.0,
    "temp_c": 22.2,
    "condition": {
      "text": "Partly cloudy"
    },
    "humidity": 65,
    "wind_mph": 8.1,
    "wind_kph": 13.0,
    "wind_dir": "NW",
    "feelslike_f": 72.0,
    "feelslike_c": 22.2,
    "uv": 5.0,
    "vis_miles": 6.0
  }
}
```

### Forecast Response
```json
{
  "forecast": {
    "forecastday": [
      {
        "date": "2024-01-15",
        "day": {
          "maxtemp_f": 75.0,
          "mintemp_f": 60.0,
          "avghumidity": 70,
          "totalprecip_in": 0.1,
          "maxwind_mph": 12.0,
          "condition": {
            "text": "Partly cloudy"
          }
        },
        "astro": {
          "sunrise": "07:15 AM",
          "sunset": "04:45 PM"
        }
      }
    ]
  }
}
```

## Usage Examples

### Current Weather
```python
from weather_api.utils import get_current_weather

weather = get_current_weather("New York")
print(weather["current"]["temp_f"])  # Temperature in Fahrenheit
```

### Forecast
```python
from weather_api.utils import get_forecast

forecast = get_forecast("New York")
for day in forecast["forecast"]["forecastday"]:
    print(f"{day['date']}: {day['day']['maxtemp_f']}°F")
```

### Historical Weather
```python
from weather_api.utils import get_historical_weather

historical = get_historical_weather("New York")
# Returns yesterday's weather data
```

## Error Handling

The implementation includes comprehensive error handling:

- **Invalid API Key**: Returns clear error message
- **Location Not Found**: Validates location before making weather calls
- **API Rate Limits**: Handles rate limiting gracefully
- **Network Errors**: Provides meaningful error messages

## Migration Notes

### From AccuWeather
- No more location key lookup required
- Direct location name support
- Better data structure
- More detailed weather information

### Environment Variables
- Replace `ACCUWEATHER_API_KEY` with `WEATHERAPI_API_KEY`
- No other environment variables needed for basic functionality

## Testing

Run the test script to verify your setup:

```bash
python test_weatherapi.py
```

This will test:
1. API key configuration
2. Location validation
3. Current weather retrieval
4. Forecast retrieval
5. Historical weather retrieval

## Support

If you encounter issues:
1. Check your API key is correct
2. Verify your `.env` file is properly configured
3. Run the test script to identify specific issues
4. Check the WeatherAPI.com documentation for API limits and requirements 