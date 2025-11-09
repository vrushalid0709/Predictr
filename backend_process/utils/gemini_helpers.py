import os
import requests
from typing import Dict, Any, Optional

class GeminiAI:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1"
        self.model = "gemini-2.5-flash"
        
    def generate_response(self, prompt: str, context: str = None) -> Dict[str, Any]:
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 512}
        }
        
        # Single timeout attempt with optimized settings
        try:
            response = requests.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                headers={"Content-Type": "application/json"},
                json=payload,
                params={"key": self.api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and data["candidates"]:
                    content = data["candidates"][0].get("content", {})
                    if "parts" in content and content["parts"]:
                        return {
                            "success": True,
                            "response": content["parts"][0].get("text", "").strip(),
                            "model": self.model
                        }
        except Exception as e:
            pass
        
        return {"success": False, "error": "API request failed"}
    
    def get_market_insights(self, user_question: str, portfolio_data: Optional[Dict] = None) -> Dict[str, Any]:
        context = "You are a helpful financial AI assistant. Provide educational insights and general guidance about investing, portfolio analysis, and market trends. Keep responses concise and helpful."
        
        if portfolio_data:
            context += f"\n\nUser's Portfolio: Invested {portfolio_data.get('total_investment', 'N/A')}, Current value {portfolio_data.get('current_value', 'N/A')}, P/L {portfolio_data.get('profit_loss', 'N/A')} ({portfolio_data.get('currency', 'USD')})\nHoldings: {', '.join(portfolio_data.get('stocks', []))}"
        
        return self.generate_response(user_question, context)


def get_direct_ai_response(user_question: str) -> Dict[str, Any]:
    """Get direct response from Gemini AI without any context filtering"""
    gemini = GeminiAI()
    simple_context = "You are a helpful financial AI assistant. Answer the user's question directly and clearly."
    return gemini.generate_response(user_question, simple_context)

def get_market_insights_ai(user_question: str, portfolio_data: Optional[Dict] = None) -> Dict[str, Any]:
    gemini = GeminiAI()
    result = gemini.get_market_insights(user_question, portfolio_data)
    
    # If the main response fails, try a direct response
    if not result.get('success'):
        return get_direct_ai_response(user_question)
    
    return result