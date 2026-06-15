"""
Flask Backend untuk AI Chatbot
Menangani request dari frontend dan berkomunikasi dengan AI API
"""

import os
import requests
import time
from io import BytesIO
from flask import Flask, request, jsonify, send_file, Response
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

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """
    Endpoint untuk membuat gambar menggunakan Pollinations API
    Server-side proxy untuk mengatasi CORS
    """
    import sys
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        prompt = data['prompt']
        style = data.get('style', 'none')
        
        # Style modifiers
        style_modifiers = {
            'none': '',
            'realistic': 'photorealistic, high quality',
            'anime': 'anime style, Studio Ghibli inspired',
            'digital': 'digital art, trending on artstation'
        }
        
        style_text = style_modifiers.get(style, '')
        full_prompt = f"{prompt}, {style_text}" if style_text else prompt
        
        # Encode prompt - keep it short to avoid rate limiting
        encoded_prompt = requests.utils.quote(full_prompt[:200])
        # Use default size without extra parameters
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        app.logger.info(f"Generating image for prompt: {full_prompt}")
        sys.stdout.flush()
        
        # Download image with longer retry delays
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Add delay for generation
                if attempt == 0:
                    time.sleep(2)
                
                response = requests.get(image_url, timeout=60, stream=True)
                
                app.logger.info(f"Attempt {attempt + 1}: Status {response.status_code}, Content-Type: {response.headers.get('content-type')}")
                sys.stdout.flush()
                
                if response.status_code == 200:
                    # Check if it's actually an image
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        return Response(
                            response.iter_content(chunk_size=8192),
                            mimetype=content_type,
                            headers={
                                'Content-Disposition': 'inline',
                                'Cache-Control': 'no-cache'
                            }
                        )
                    elif 'json' in content_type:
                        # Rate limited, wait and retry
                        app.logger.info("Rate limited, waiting longer...")
                        sys.stdout.flush()
                        time.sleep(10)
                        continue
                elif response.status_code == 402:
                    # Payment required / rate limited
                    app.logger.info("Payment required (402), waiting longer...")
                    sys.stdout.flush()
                    time.sleep(10)
                    continue
                else:
                    time.sleep(3)
                    
            except requests.exceptions.RequestException as e:
                app.logger.error(f"Request error: {e}")
                sys.stdout.flush()
                time.sleep(3)
                continue
        
        # All retries failed
        return jsonify({
            'error': 'Gagal membuat gambar. Layanan sedang sibuk, coba lagi dalam beberapa menit.',
            'status': 'error'
        }), 503
        
    except Exception as e:
        app.logger.error(f"Image generation error: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
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
    print("📍 Image Endpoint: http://localhost:5000/api/generate-image")
    print("📍 Frontend: Buka http://localhost:5000 di browser")
    print("=" * 50)
    
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)