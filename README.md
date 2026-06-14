# 🤖 AI Chatbot Website

AI Chatbot interaktif untuk website dengan Flask backend dan integrasi OpenAI/Claude.

![Status](https://img.shields.io/badge/status-ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## ✨ Fitur

- 💬 Interface chat yang modern dan responsif
- 🤖 Dukungan untuk OpenAI GPT dan Anthropic Claude
- 📱 Mobile-friendly design
- ⚡ Real-time messaging dengan typing indicator
- 💾 Conversation history
- 🎨 Quick action buttons

## 🚀 Cara Instalasi

### 1. Clone atau Download Project

```bash
cd /workspace/project
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup API Key

Copy file `.env.example` menjadi `.env` dan isi dengan API key Anda:

```bash
cp .env.example .env
```

Edit file `.env`:
```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Dapatkan API key:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys

### 4. Jalankan Server

```bash
python app.py
```

### 5. Buka di Browser

Buka URL: http://localhost:5000

## 📁 Struktur Project

```
/workspace/project
├── index.html      # Frontend (HTML/CSS/JS)
├── app.py          # Flask Backend API
├── ai_engine.py    # AI Integration Module
├── requirements.txt # Python Dependencies
├── .env.example    # Template Environment Variables
└── README.md       # Dokumentasi
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/chat` | POST | Kirim pesan ke AI |
| `/api/history` | GET | Ambil history percakapan |
| `/api/clear` | POST | Hapus history percakapan |
| `/api/models` | GET | Lihat model AI yang tersedia |

### Contoh Request

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Halo, apa kabar?"}'
```

### Contoh Response

```json
{
  "response": "Halo! Saya baik, terima kasih! 👋",
  "status": "success"
}
```

## 🎨 Customization

### Ubah System Prompt

Edit file `ai_engine.py`, fungsi `__init__`:

```python
self.system_prompt = """Prompt baru Anda di sini..."""
```

### Ubah Theme Warna

Edit CSS di `index.html`:

```css
/* Gradient warna */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Ubah Quick Actions

Edit bagian quick-actions di `index.html`:

```html
<button class="quick-action" onclick="sendQuickMessage('Pesanan Anda')">
    Aksi Baru
</button>
```

## 🛠️ Development

### Run dengan Debug Mode

```bash
python app.py
```

### Test API

```bash
# Test health check
curl http://localhost:5000/

# Test chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## 📝 Catatan

- Tanpa API key, chatbot berjalan dalam **mode demo** dengan response sederhana
- API key disimpan di file `.env` (pastikan di-gitignore!)
- Untuk production, gunakan HTTPS dan environment variables yang aman

## 📜 License

MIT License - Bebas digunakan untuk project pribadi maupun komersial.

---

Dibuat dengan ❤️ untuk membantu Anda membuat AI Chatbot yang interaktif!