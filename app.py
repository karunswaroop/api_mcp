"""
Flask web application for the Weather API POC
"""
import os
import json
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
    """API endpoint to process weather queries"""
    try:
        # Get query from request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing query parameter'
            }), 400
        
        query = data['query']
        
        # Process query using PocketFlow
        response = process_weather_query(query)
        
        # Return response
        return jsonify({
            'query': query,
            'response': response
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR DETAILS: {error_details}")
        return jsonify({
            'error': str(e),
            'details': error_details
        }), 500

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
    app.run(host='0.0.0.0', port=port, debug=True)
