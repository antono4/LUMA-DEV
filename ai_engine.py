"""
AI Engine - Modul untuk komunikasi dengan berbagai AI API
Mendukung: OpenAI GPT, Anthropic Claude, Google Gemini, dll.
"""

import os
import json
from typing import List, Dict, Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

class AIEngine:
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 20
        
        # System prompt untuk personality AI
        self.system_prompt = """Kamu adalah AI Assistant yang helpful, friendly, dan informative.
Kamu bisa membantu dalam berbagai topik seperti:
- Programming dan coding
- Penjelasan konsep teknologi
- Penulisan dan editing teks
- Pertanyaan umum dan edukasi
- Brainstorming ide

Selalu jawab dalam Bahasa Indonesia kecuali pengguna meminta dalam bahasa lain.
Jawab dengan ramah, jelas, dan informatif."""

    def get_response(self, user_message: str) -> str:
        """
        Mendapatkan response dari AI
        """
        # Tambahkan pesan user ke history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Cek apakah ada API key
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        response = None
        error_message = None
        
        # Coba gunakan OpenAI dulu
        if openai_key:
            try:
                response = self._get_openai_response(openai_key)
                if "Error dengan OpenAI API" in response:
                    error_message = response
                    response = None
            except Exception as e:
                error_message = str(e)
        
        # Jika OpenAI gagal, coba Claude
        if response is None and anthropic_key:
            try:
                response = self._get_anthropic_response(anthropic_key)
                if "Error dengan Anthropic API" in response:
                    response = None
            except Exception as e:
                error_message = str(e)
        
        # Jika tidak ada keduanya atau gagal, gunakan fallback
        if response is None:
            response = self._get_fallback_response(user_message)
        
        # Tambahkan response ke history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # Batasi ukuran history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        return response

    def _get_openai_response(self, api_key: str) -> str:
        """
        Mendapatkan response dari OpenAI GPT
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            
            # Buat messages dengan system prompt
            messages = [{'role': 'system', 'content': self.system_prompt}]
            messages.extend(self.conversation_history[:-1])  # Exclude last message (pending response)
            
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            return "Library OpenAI belum terinstall. Install dengan: pip install openai"
        except Exception as e:
            return f"Error dengan OpenAI API: {str(e)}"

    def _get_anthropic_response(self, api_key: str) -> str:
        """
        Mendapatkan response dari Anthropic Claude
        """
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Convert history format for Claude
            messages = []
            for msg in self.conversation_history[:-1]:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            
            response = client.messages.create(
                model='claude-3-sonnet-20240229',
                max_tokens=1000,
                system=self.system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except ImportError:
            return "Library Anthropic belum terinstall. Install dengan: pip install anthropic"
        except Exception as e:
            return f"Error dengan Anthropic API: {str(e)}"

    def _get_fallback_response(self, user_message: str) -> str:
        """
        Fallback response ketika tidak ada API key
        Menggunakan logika sederhana untuk demo
        """
        user_message_lower = user_message.lower()
        
        # Greeting patterns
        greetings = ['halo', 'hai', 'hi', 'hello', 'pagi', 'siang', 'sore', 'malam']
        if any(greet in user_message_lower for greet in greetings):
            return "Halo! 👋 Selamat datang! Saya AI Assistant. Ada yang bisa saya bantu hari ini?"
        
        # Programming help
        if any(word in user_message_lower for word in ['code', 'coding', 'program', 'python', 'javascript', 'java', 'html', 'css']):
            return """Tentu! Saya bisa membantu dengan programming. Beberapa hal yang bisa saya bantu:

🐍 **Python** - Web development, data science, AI/ML
⚡ **JavaScript** - Frontend, backend (Node.js), React
☕ **Java** - OOP, Android development
🌐 **HTML/CSS** - Web design dan styling

Silakan beritahu saya:
1. Bahasa pemrograman apa yang ingin Anda pelajari?
2. Project apa yang sedang Anda kerjakan?
3. Ada error atau masalah spesifik yang ingin ditanyakan?"""
        
        # AI questions
        if any(word in user_message_lower for word in ['apa itu ai', 'artificial intelligence', 'machine learning', 'deep learning']):
            return """**Artificial Intelligence (AI)** adalah cabang ilmu komputer yang fokus pada pembuatan mesin yang bisa belajar dan berpikir seperti manusia.

📊 **Jenis-jenis AI:**
• **Machine Learning** - AI yang belajar dari data
• **Deep Learning** - Menggunakan neural network berlapis
• **NLP (Natural Language Processing)** - AI untuk memahami bahasa manusia

🤖 **Contoh AI yang populer:**
• ChatGPT (OpenAI)
• Claude (Anthropic)
• Gemini (Google)
• Llama (Meta)

Apakah Anda ingin tahu lebih detail tentang topik tertentu?"""
        
        # Help request
        if any(word in user_message_lower for word in ['bantu', 'tolong', 'help', 'how', 'cara']):
            return """Tentu, saya dengan senang hati membantu! 😊

Silakan ceritakan lebih detail:
• Apa yang ingin Anda capai?
• Apakah ada konteks atau masalah spesifik?
• Sudah mencoba apa saja sebelumnya?

Dengan informasi lebih detail, saya bisa memberikan jawaban yang lebih tepat dan helpful."""
        
        # Thanks/Gratitude
        if any(word in user_message_lower for word in ['terima kasih', 'thanks', 'thank you', 'makasih']):
            return "Sama-sama! 😊 Senang bisa membantu. Jika ada pertanyaan lain, jangan ragu untuk bertanya!"
        
        # Default response
        return f"""Terima kasih atas pesan Anda! Saya menerima: "{user_message}"

Maaf, untuk saat ini saya berjalan dalam mode demo karena belum ada API key yang dikonfigurasi.

**Untuk mengaktifkan AI yang sebenarnya:**
1. Dapatkan API key dari OpenAI (openai.com/api) atau Anthropic
2. Buat file `.env` dengan isi:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Jalankan server: `python app.py`

Apakah ada hal lain yang bisa saya bantu?"""


    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Mengembalikan history percakapan"""
        return self.conversation_history

    def clear_history(self):
        """Menghapus history percakapan"""
        self.conversation_history = []

    def get_available_models(self) -> Dict[str, str]:
        """Mengembalikan daftar model AI yang tersedia"""
        models = {
            'openai': 'GPT-3.5 Turbo (Default)',
            'anthropic': 'Claude 3 Sonnet',
        }
        
        # Tambahkan info berdasarkan API key yang tersedia
        available = []
        if os.getenv('OPENAI_API_KEY'):
            available.append('openai')
        if os.getenv('ANTHROPIC_API_KEY'):
            available.append('anthropic')
        if not available:
            available.append('demo (no API key)')
        
        return {
            'available': available,
            'all_models': models
        }