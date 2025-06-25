"""
Flask web application for the Weather API POC
"""
import os
import json
import traceback
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from weather_api.flow import process_weather_query

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page with the query form"""
    return render_template('index.html')

@app.route('/api/weather', methods=['POST'])
def weather_api():
    """API endpoint for weather queries"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        provider = data.get('provider', 'api')  # Default to API if not specified
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Validate provider
        if provider not in ['api', 'mcp']:
            return jsonify({"error": "Invalid provider. Must be 'api' or 'mcp'"}), 400
        
        response = process_weather_query(query, provider)
        
        return jsonify({"response": response})
    except Exception as e:
        traceback.print_exc()  # Print detailed error for debugging
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'weather-api-poc'
    })

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5001))
    
    # Run app
    app.run(host='0.0.0.0', port=port, debug=False)
