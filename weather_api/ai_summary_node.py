"""
AI Summary Node for generating intelligent weather summaries using OpenAI
"""
import os
import json
from typing import Dict, Any, Optional
from pocketflow import BaseNode
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AISummaryNode(BaseNode):
    """Node to generate AI-powered summaries of weather responses"""
    
    def __init__(self):
        super().__init__()
        try:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.model = "gpt-4o-mini"  # Cost-effective small model
            self.client_initialized = True
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")
            self.client = None
            self.client_initialized = False
            self.model = "gpt-4o-mini"
    
    def prep(self, shared):
        """Prepare data for AI summary generation"""
        return {
            "user_query": shared.get("user_query", ""),
            "final_response": shared.get("final_response", ""),
            "parameters": shared.get("parameters", {}),
            "provider": shared.get("provider", "api"),
            "weather_data": {
                "current_weather": shared.get("current_weather", {}),
                "forecast": shared.get("forecast", {}),
                "mcp_weather": shared.get("mcp_weather", {}),
                "current_weather_response": shared.get("current_weather_response", ""),
                "forecast_response": shared.get("forecast_response", "")
            }
        }
    
    def _create_summary_prompt(self, user_query: str, weather_response: str, weather_data: Dict[str, Any]) -> str:
        """Create a focused prompt for weather summary generation"""
        
        prompt = f"""You are a helpful weather assistant. Analyze the user's specific question and provide a direct, focused answer followed by a brief summary.

User asked: "{user_query}"

Weather Data Response:
{weather_response}

Instructions:
- FIRST, answer their EXACT question directly and concisely in 1-2 sentences
- THEN, provide a brief additional summary with 2-3 practical insights or context
- Structure your response as: Direct Answer + Additional Summary
- Keep the total response under 100 words
- Use a friendly, conversational tone

Format:
[Direct answer to their question]

[2-3 sentences of additional weather summary/context]

Examples:
- If asked "humidity tomorrow in Seattle?" → "Humidity will be 77% tomorrow in Seattle.

It'll feel quite damp with overcast conditions and temperatures around 64°F. Consider bringing a light jacket as the high humidity combined with cooler temps might make it feel chilly."

Generate the response in this two-part format."""

        return prompt
    
    def _generate_ai_summary(self, user_query: str, weather_response: str, weather_data: Dict[str, Any]) -> str:
        """Generate AI summary using OpenAI with error handling"""
        try:
            # Check if OpenAI client was initialized successfully
            if not self.client_initialized or not self.client:
                return "AI summary unavailable - OpenAI client initialization failed."
            
            # Check if OpenAI API key is available
            if not os.getenv('OPENAI_API_KEY'):
                return "AI summary unavailable - OpenAI API key not configured."
            
            if not weather_response or weather_response.strip() == "":
                return "No weather data available to summarize."
            
            prompt = self._create_summary_prompt(user_query, weather_response, weather_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful weather assistant that provides concise, friendly weather summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7,
                timeout=10  # 10 second timeout
            )
            
            summary = response.choices[0].message.content.strip()
            return summary if summary else "Unable to generate weather summary."
            
        except Exception as e:
            error_msg = str(e)
            print(f"AI Summary Error: {error_msg}")
            
            # Provide more specific error messages for common issues
            if "API key" in error_msg.lower():
                return "AI summary unavailable - please check OpenAI API key."
            elif "timeout" in error_msg.lower():
                return "AI summary unavailable - service timeout."
            elif "rate limit" in error_msg.lower():
                return "AI summary unavailable - rate limit exceeded."
            else:
                return "AI summary unavailable - service temporarily down."
    
    def exec(self, prep_res):
        """Execute AI summary generation"""
        user_query = prep_res["user_query"]
        weather_response = prep_res["final_response"]
        weather_data = prep_res["weather_data"]
        
        # Generate AI summary
        ai_summary = self._generate_ai_summary(user_query, weather_response, weather_data)
        
        return {
            "ai_summary": ai_summary,
            "original_response": weather_response
        }
    
    def post(self, shared, prep_res, exec_res):
        """Post-process and store AI summary with fallback handling"""
        ai_summary = exec_res["ai_summary"]
        original_response = exec_res["original_response"]
        
        # Store AI summary in shared context
        shared["ai_summary"] = ai_summary
        
        # Check if AI summary generation failed
        if ai_summary.startswith("AI summary unavailable"):
            # Fallback: return original response if AI summary fails
            print(f"AI Summary failed, falling back to original response: {ai_summary}")
            shared["final_response"] = original_response
        else:
            # Create enhanced response with both original data and AI summary
            enhanced_response = {
                "weather_data": original_response,
                "ai_summary": ai_summary
            }
            
            # Update final response to include AI summary
            shared["final_response"] = json.dumps(enhanced_response, indent=2)
        
        return "success"