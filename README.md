# AI Weather Intelligence Platform

A modern, professional weather application that combines traditional weather APIs with AI-powered intelligent summaries. Built with Flask, OpenAI GPT-4o-mini, and a sleek responsive UI.

![Weather Intelligence Demo](https://img.shields.io/badge/Demo-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 🤖 AI-Powered Intelligence
- **Smart Weather Summaries** - GPT-4o-mini generates contextual, conversational weather insights
- **Direct Answer Format** - Answers specific questions directly, then provides additional context
- **Natural Language Processing** - Ask questions like "Will it be cloudy tomorrow?" or "What's the humidity in Seattle?"

### 🌤️ Dual Data Providers
- **Weather API** - Traditional weather data from WeatherAPI.com
- **MCP Protocol** - Modern Model Context Protocol implementation
- **Real-time Data** - Current conditions, forecasts, and historical weather

### 🎨 Professional UI/UX
- **Modern Design** - Clean, gradient-based interface with glass morphism effects
- **Interactive Examples** - Click-to-try example queries for instant demos
- **Responsive Layout** - Works seamlessly on desktop, tablet, and mobile
- **Professional Typography** - Optimized readability with Inter font

### ⚡ Advanced Features
- **Error Handling** - Graceful fallbacks when AI or weather services are unavailable
- **Loading States** - Professional loading animations and user feedback
- **Secure Configuration** - Environment-based API key management

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- WeatherAPI.com API key ([Get free key](https://www.weatherapi.com/))
- OpenAI API key ([Get key](https://platform.openai.com/api-keys))

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/karunswaroop/api_mcp.git
   cd api_mcp
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv env_api_mcp
   source env_api_mcp/bin/activate  # On Windows: env_api_mcp\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # WEATHERAPI_KEY=your_weatherapi_key_here
   # OPENAI_API_KEY=your_openai_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5001
   ```

## 🌐 Deployment

### Render.com (Recommended)

1. **Fork this repository** on GitHub

2. **Create new Web Service** on [Render.com](https://render.com)
   - Connect your GitHub repository
   - Use the included `render.yaml` configuration

3. **Set environment variables** in Render dashboard:
   - `WEATHERAPI_KEY`: Your WeatherAPI.com key
   - `OPENAI_API_KEY`: Your OpenAI API key

4. **Deploy** - Render will automatically build and deploy your app

### Manual Deployment

The app includes a `render.yaml` file with optimized settings:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Environment**: Python 3.10+

## 📖 API Reference

### Weather Endpoint

```http
POST /api/weather
Content-Type: application/json

{
  "query": "What's the weather like in New York?",
  "provider": "api"  // or "mcp"
}
```

**Response:**
```json
{
  "response": {
    "weather_data": "Current weather for New York: Sunny, 72°F...",
    "ai_summary": "It's sunny and pleasant in New York today..."
  }
}
```

### Health Check

```http
GET /health
```

## 🏗️ Architecture

### Backend Components
- **Flask App** (`app.py`) - Main web server and API endpoints
- **PocketFlow** (`weather_api/flow.py`) - Workflow orchestration
- **Weather Nodes** (`weather_api/nodes.py`) - Traditional API integrations
- **MCP Nodes** (`weather_api/mcp_nodes.py`) - Model Context Protocol implementation
- **AI Summary** (`weather_api/ai_summary_node.py`) - OpenAI integration

### Frontend
- **Modern HTML5/CSS3** with responsive design
- **Vanilla JavaScript** for interactions
- **Progressive Enhancement** - works without JavaScript

### Data Flow
```
User Query → Parameter Extraction → Location Resolution → Weather Data → AI Summary → Response
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `WEATHERAPI_KEY` | WeatherAPI.com API key | Yes |
| `OPENAI_API_KEY` | OpenAI API key for summaries | Yes |
| `PORT` | Server port (default: 5001) | No |

### Supported Weather Queries

- **Current conditions**: "What's the weather in [city]?"
- **Forecasts**: "Will it rain tomorrow in [city]?"
- **Specific metrics**: "What's the humidity in [city]?"
- **Multi-day**: "What's the 3-day forecast for [city]?"

## 🛠️ Development

### Project Structure
```
api_mcp/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── render.yaml              # Render.com deployment config
├── templates/
│   └── index.html           # Web interface
├── weather_api/
│   ├── __init__.py
│   ├── flow.py              # PocketFlow workflow
│   ├── nodes.py             # Weather API nodes
│   ├── mcp_nodes.py         # MCP protocol nodes
│   ├── ai_summary_node.py   # OpenAI integration
│   └── utils.py             # Utility functions
└── README.md
```

### Adding New Features

1. **New Weather Provider**: Add to `weather_api/nodes.py`
2. **AI Enhancements**: Modify `weather_api/ai_summary_node.py`
3. **UI Changes**: Update `templates/index.html`
4. **Workflow Changes**: Edit `weather_api/flow.py`

## 🧪 Testing

Run the test suite:
```bash
# Test OpenAI connection
python test_openai_key.py

# Manual testing
python app.py
# Visit http://localhost:5001
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **WeatherAPI.com** for reliable weather data
- **OpenAI** for powerful AI summaries
- **PocketFlow** for workflow orchestration
- **Render.com** for seamless deployment

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/karunswaroop/api_mcp/issues)
- **Documentation**: This README and code comments
- **Examples**: Interactive examples in the web interface

---

Built with ❤️ using Flask, OpenAI, and modern web technologies.