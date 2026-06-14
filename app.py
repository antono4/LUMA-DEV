"""
Flask Backend untuk AI Chatbot
Menangani request dari frontend dan berkomunikasi dengan AI API
"""

import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ai_engine import AIEngine

app = Flask(__name__)
CORS(app)

# Inisialisasi AI Engine
ai_engine = AIEngine()

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint untuk menerima pesan dari frontend
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required'
            }), 400
        
        user_message = data['message']
        
        if not user_message.strip():
            return jsonify({
                'error': 'Message cannot be empty'
            }), 400
        
        # Dapatkan response dari AI
        response = ai_engine.get_response(user_message)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Endpoint untuk mendapatkan history percakapan
    """
    return jsonify({
        'history': ai_engine.get_conversation_history()
    })

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """
    Endpoint untuk清除 history percakapan
    """
    ai_engine.clear_history()
    return jsonify({
        'status': 'success',
        'message': 'Conversation history cleared'
    })

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """
    Endpoint untuk melihat model AI yang tersedia
    """
    return jsonify({
        'models': ai_engine.get_available_models()
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 AI Chatbot Server Starting...")
    print("=" * 50)
    print("📍 API Endpoint: http://localhost:5000/api/chat")
    print("📍 Frontend: Buka http://localhost:5000 di browser")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)