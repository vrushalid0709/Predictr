from flask import Blueprint, request, jsonify, session
from backend_process.utils.gemini_helpers import get_market_insights_ai, get_direct_ai_response
from backend_process.utils.stock_helpers import user_stocks_helper
import requests
import os

gemini_bp = Blueprint('gemini', __name__)

def get_exchange_rates():
    try:
        api_key = os.getenv('EXCHANGE_RATE_API_KEY')
        response = requests.get(f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD', timeout=5)
        if response.status_code == 200:
            return response.json().get('conversion_rates', {})
    except:
        pass
    return {'USD': 1, 'EUR': 0.92, 'GBP': 0.78, 'INR': 84}

def convert_currency(amount, from_currency='USD', to_currency='INR'):
    if from_currency == to_currency:
        return amount
    rates = get_exchange_rates()
    usd_amount = amount / rates.get(from_currency, 1)
    return usd_amount * rates.get(to_currency, 1)

@gemini_bp.route('/ai/chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Message is required'}), 400
    
    user_message = data['message'].strip()
    user_currency = data.get('currency', 'INR')
    user_id = session.get('user_id')
    portfolio_context = None
    
    if user_id:
        user_stocks = user_stocks_helper.get_user_stocks(user_id)
        if user_stocks.get('success'):
            stocks = user_stocks.get('stocks', [])
            total_investment_usd = sum(s.get('qty', 0) * s.get('buy_price', 0) for s in stocks)
            current_value_usd = sum(s.get('qty', 0) * s.get('current_price', 0) for s in stocks)
            
            total_investment = convert_currency(total_investment_usd, 'USD', user_currency)
            current_value = convert_currency(current_value_usd, 'USD', user_currency)
            profit_loss = current_value - total_investment
            
            symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}
            symbol = symbols.get(user_currency, user_currency + ' ')
            
            portfolio_context = {
                'stocks': [f"{s.get('symbol')}: {s.get('qty')} shares" for s in stocks],
                'total_investment': f"{symbol}{total_investment:,.0f}",
                'current_value': f"{symbol}{current_value:,.0f}",
                'profit_loss': f"{symbol}{profit_loss:,.0f}",
                'currency': user_currency
            }
    
    ai_response = get_market_insights_ai(user_message, portfolio_context)
    
    if ai_response['success']:
        return jsonify({
            'success': True,
            'response': ai_response['response'],
            'model': ai_response.get('model', 'gemini-2.5-flash'),
            'hasPortfolioContext': portfolio_context is not None
        })
    
    # Try direct AI response as fallback
    direct_response = get_direct_ai_response(user_message)
    if direct_response['success']:
        return jsonify({
            'success': True,
            'response': direct_response['response'],
            'model': 'gemini-direct',
            'hasPortfolioContext': portfolio_context is not None
        })
    
    # Final fallback message
    fallback = "I can help with portfolio analysis, market trends, investment strategies, and risk assessment. Please try rephrasing your question or ask about a specific investment topic."
    return jsonify({
        'success': True,
        'response': fallback,
        'model': 'fallback',
        'hasPortfolioContext': portfolio_context is not None
    })

@gemini_bp.route('/ai/direct', methods=['POST'])
def ai_direct():
    """Direct AI response endpoint without portfolio context"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Message is required'}), 400
    
    user_message = data['message'].strip()
    response = get_direct_ai_response(user_message)
    
    if response['success']:
        return jsonify({
            'success': True,
            'response': response['response'],
            'model': response.get('model', 'gemini-2.5-flash')
        })
    
    return jsonify({'success': False, 'error': 'Failed to generate response'}), 500


