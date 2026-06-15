"""
AI Engine - Modul untuk komunikasi dengan berbagai AI API
Mendukung: OpenAI GPT, Anthropic Claude, Google Gemini, dll.
Integrasi dengan OpenHands untuk kapabilitas AI Agent.
"""

import os
import json
import re
from typing import List, Dict, Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

class OpenHandsCapabilities:
    """Knowledge base for OpenHands capabilities and integration."""
    
    CAPABILITIES = {
        'fix_vulnerabilities': {
            'name': 'Fix Vulnerabilities',
            'description': 'Scans repositories, fixes vulnerabilities, and opens reviewable PRs',
            'use_case': 'Automated security patching',
            'icon': '🛡️'
        },
        'review_prs': {
            'name': 'Review PRs',
            'description': 'Reviews PRs for quality, security, and best practices',
            'use_case': 'Automated code review',
            'icon': '🔍'
        },
        'migrate_code': {
            'name': 'Migrate Code',
            'description': 'Migrates legacy systems (COBOL, etc.) to modern languages',
            'use_case': 'Legacy modernization',
            'icon': '🔄'
        },
        'triage_incidents': {
            'name': 'Triage Incidents',
            'description': 'Investigates errors, finds root causes, posts debugging insights',
            'use_case': 'Production issue resolution',
            'icon': '🚨'
        }
    }
    
    FEATURES = [
        ("SDK", "Build agents with Python SDK - https://docs.openhands.dev/sdk"),
        ("CLI", "Terminal-based agentic power - https://docs.openhands.dev/openhands/usage/run-openhands/cli-mode"),
        ("Local GUI", "Web-based agent interface - https://docs.openhands.dev/openhands/usage/run-openhands/local-setup"),
        ("Cloud", "Hosted solution with integrations - https://app.all-hands.dev"),
        ("Enterprise", "Self-hosted deployment - https://openhands.dev/enterprise")
    ]
    
    QUICK_ACTIONS = [
        ("fix bugs", "OpenHands can autonomously fix 87% of bug tickets same-day"),
        ("code review", "Speed up reviews with AI-powered analysis"),
        ("test coverage", "Generate and maintain tests automatically"),
        ("documentation", "Auto-generate docs and release notes"),
        ("refactor", "Decompose monoliths and modernize legacy code"),
        ("security", "Upgrade dependencies and fix vulnerabilities"),
        ("debugging", "Analyze logs and pinpoint root causes")
    ]

class AIEngine:
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 20
        
        # System prompt untuk personality AI
        self.system_prompt = """Kamu adalah LUMA yang helpful, friendly, dan informative.
Kamu bisa membantu dalam berbagai topik seperti:
- Programming dan coding
- Penjelasan konsep teknologi
- Penulisan dan editing teks
- Pertanyaan umum dan edukasi
- Brainstorming ide
- Kapabilitas OpenHands dan AI Agent

INTEGRASI OPENHANDS:
OpenHands adalah platform AI coding agent open-source yang bisa:
- Fix Vulnerabilities: Scan & fix vulnerability, buka PR
- Review PRs: Quality, security, dan best practices review
- Migrate Code: Migrate legacy code (COBOL → Java, dll)
- Triage Incidents: Investigate errors, find root causes

OpenHands Products:
- SDK: Build agents dengan Python (docs.openhands.dev/sdk)
- CLI: Agentic power dari terminal
- Local GUI: Web interface lokal
- Cloud: app.all-hands.dev (free tier available)
- Enterprise: Self-hosted deployment

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
        
        # OpenHands specific patterns (CHECK FIRST - higher priority)
        if self._handle_openhands_query(user_message_lower, user_message):
            return self._handle_openhands_query(user_message_lower, user_message) or ""
        
        # Greeting patterns
        greetings = ['halo', 'hai', 'hi', 'hello', 'pagi', 'siang', 'sore', 'malam']
        if any(greet in user_message_lower for greet in greetings):
            return "Halo! 👋 Selamat datang! Saya LUMA. Ada yang bisa saya bantu hari ini?\n\n💡 **Tips:** Tanyakan tentang OpenHands, programming, atau topik lainnya!"
        
        # Programming help
        if any(word in user_message_lower for word in ['code', 'coding', 'program', 'python', 'javascript', 'java', 'html', 'css']):
            return """Tentu! Saya bisa membantu dengan programming. Beberapa hal yang bisa saya bantu:

🐍 **Python** - Web development, data science, AI/ML
⚡ **JavaScript** - Frontend, backend (Node.js), React
☕ **Java** - OOP, Android development
🌐 **HTML/CSS** - Web design dan styling

💡 **Pro Tip:** Gunakan **OpenHands** untuk automate coding tasks seperti fix bugs, generate tests, dan code review!

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
• **AI Agents** - Autonomous AI yang bisa execute tasks (seperti OpenHands!)

🤖 **Contoh AI yang populer:**
• ChatGPT (OpenAI)
• Claude (Anthropic)
• Gemini (Google)
• Llama (Meta)
• **OpenHands** - AI coding agent open-source!

Apakah Anda ingin tahu lebih detail tentang topik tertentu?"""
        
        # Help request
        if any(word in user_message_lower for word in ['bantu', 'tolong', 'help', 'how', 'cara']):
            return """Tentu, saya dengan senang hati membantu! 😊

**Topik yang bisa saya bantu:**

🔧 **Programming**
   - Code review, debugging, refactoring
   - Generate tests, documentation

🤖 **OpenHands**
   - AI coding agent untuk automate tasks
   - Fix bugs, PR review, code migration

📚 **Edukasi**
   - Penjelasan konsep teknologi
   - Tutorial dan best practices

Silakan ceritakan lebih detail apa yang Anda butuhkan!"""
        
        # Thanks/Gratitude
        if any(word in user_message_lower for word in ['terima kasih', 'thanks', 'thank you', 'makasih']):
            return "Sama-sama! 😊 Senang bisa membantu. Jika ada pertanyaan lain, jangan ragu untuk bertanya!\n\n💡 **Coba tanyakan tentang OpenHands untuk automate coding tasks!**"
        
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

**💡 Atau coba OpenHands untuk AI coding agent:**
👉 https://app.all-hands.dev (free tier available)

Apakah ada hal lain yang bisa saya bantu?"""

    def _handle_openhands_query(self, msg_lower: str, original_msg: str) -> str:
        """Handle OpenHands-specific queries with detailed responses."""
        
        # Direct OpenHands questions
        if 'openhands' in msg_lower:
            if any(word in msg_lower for word in ['apa itu', 'what is', 'apa itu openhands', 'what is openhands']):
                return """**OpenHands** adalah platform AI coding agent open-source yang powerful!

🤖 **Apa itu OpenHands?**
OpenHands adalah AI agent yang bisa autonomously execute engineering tasks - bukan cuma suggest code, tapi benar-benar menyelesaikan pekerjaan!

**✨ Kapabilitas Utama:**
• 🛡️ **Fix Vulnerabilities** - Scan & fix security issues, auto-create PR
• 🔍 **Review PRs** - Quality, security, best practices review
• 🔄 **Migrate Code** - Legacy modernization (COBOL → Java, dll)
• 🚨 **Triage Incidents** - Debugging & root cause analysis

**📦 Products:**
| Product | Description | Link |
|---------|-------------|------|
| SDK | Build custom agents | docs.openhands.dev/sdk |
| CLI | Terminal agent | docs.openhands.dev |
| Local GUI | Web interface | Run locally |
| Cloud | Free tier available | app.all-hands.dev |
| Enterprise | Self-hosted | openhands.dev/enterprise |

**🎯 Hasil nyata:** "OpenHands autonomously fixes 87% of bug tickets same-day"

Klik 👉 https://app.all-hands.dev untuk coba gratis!"""
            
            if any(word in msg_lower for word in ['capabilities', 'fitur', 'features', 'bisa apa', ' kemampuan']):
                return """**🎯 OpenHands Capabilities:**

🛡️ **Fix Vulnerabilities**
Scan repositories, fix vulnerabilities, dan buka reviewable PRs

🔍 **Review PRs**  
Quality, security, dan best practices review untuk setiap pull request

🔄 **Migrate Code**
Migrate legacy systems seperti COBOL ke Java dengan testing & validation

🚨 **Triage Incidents**
Investigate errors, find root causes, post debugging insights

**🚀 Automate the Outer Loop:**
• Speed up code reviews ⏱️
• Expand test coverage ✅
• Automate docs & release notes 📝
• Refactor old code 🔧
• Eliminate security debt 🔒

**📚 Learn more:** https://docs.openhands.dev"""
            
            if 'sdk' in msg_lower or 'python' in msg_lower and 'build' in msg_lower:
                return """**🐍 OpenHands SDK - Build Agents with Python!**

OpenHands SDK adalah composable Python library untuk membangun AI agents.

```python
# Basic usage example
from openhands.agent import Agent

agent = Agent(
    model='claude-sonnet',
    max_steps=100
)
result = agent.run('Fix the login bug in auth.py')
```

**✨ SDK Features:**
• Model-agnostic (Claude, GPT, Gemini, dll)
• Tool calling system
• Conversation management
• Extensible architecture

**📖 Docs:** https://docs.openhands.dev/sdk
**💻 GitHub:** github.com/All-Hands-AI/OpenHands (77K+ stars!)"""
            
            if 'cli' in msg_lower or 'terminal' in msg_lower or 'command' in msg_lower:
                return """**💻 OpenHands CLI - Agentic Power from Terminal!**

OpenHands CLI memberikan agentic power langsung dari command line.

```bash
# Install
pip install openhands

# Start interactive session
openhands

# Run specific task
openhands --task "Fix bug in auth.py"
```

**✨ CLI Features:**
• Claude, GPT, or any LLM backend
• File editing & code execution
• Git operations
• Interactive & non-interactive modes

**📖 Docs:** https://docs.openhands.dev/openhands/usage/run-openhands/cli-mode"""
            
            if 'cloud' in msg_lower or 'app.all-hands' in msg_lower or 'hosted' in msg_lower:
                return """**☁️ OpenHands Cloud - Try it Free!**

OpenHands Cloud adalah hosted solution dengan free tier!

👉 **app.all-hands.dev**

**✨ Cloud Features:**
• Sign in with GitHub/GitLab
• Free tier with Minimax model
• Slack, Jira, Linear integrations
• Multi-user support
• RBAC & permissions
• Collaboration features

**💰 Pricing:** Mulai gratis, scale sesuai kebutuhan!

Klik 👉 https://app.all-hands.dev untuk mulai!"""
            
            if 'enterprise' in msg_lower or 'self-hosted' in msg_lower or 'on-premise' in msg_lower:
                return """**🏢 OpenHands Enterprise - Self-Hosted Solution!**

OpenHands Enterprise untuk organizations yang butuh self-hosted deployment.

**✨ Enterprise Features:**
• Deploy di VPC sendiri (Kubernetes)
• Full source-available code
• Extended support
• Access to research team
• Enterprise-grade security
• Custom integrations

**🔒 Security:**
• Isolated execution environments
• Full auditability
• Model-agnostic architecture
• Flexible access control

**📞 Contact:** openhands.dev/enterprise

Cocok untuk organisasi dengan strict data security & compliance requirements!"""
            
            if any(word in msg_lower for word in ['bug', 'fix', 'error', 'vulnerability', 'cve', 'security']):
                return """**🛡️ OpenHands for Bug Fixing & Security!**

OpenHands bisa autonomously fix bugs dan security vulnerabilities!

**🔧 Bug Fixing:**
• Analyzes error logs
• Identifies root cause
• Proposes & implements fix
• Creates PR for review

**🔒 Security Features:**
• Scan for vulnerabilities
• Auto-fix security issues
• Update dependencies
• Generate security reports

**📊 Quote:** "OpenHands autonomously fixes **87% of bug tickets same-day**"

**🚀 Start fixing bugs:**
👉 https://app.all-hands.dev

"At some companies, clients think they hired an army of engineers." 🤯"""
            
            if any(word in msg_lower for word in ['pr', 'pull request', 'review', 'code review']):
                return """**🔍 OpenHands for PR Review!**

Automate code reviews dengan AI-powered analysis!

**✨ PR Review Features:**
• Quality assessment
• Security scanning
• Best practices check
• Inline comments
• Suggestions for improvement

**⏱️ Speed Up Reviews:**
From hours to minutes - AI handles the analysis, humans focus on decisions!

**🔗 Integrations:**
• GitHub PR review automation
• GitLab MR reviews
• Custom workflows

**📖 Learn more:** https://docs.openhands.dev

Try it free 👉 https://app.all-hands.dev"""
            
            if any(word in msg_lower for word in ['github', 'gitlab', 'integration', 'slack', 'jira']):
                return """**🔗 OpenHands Integrations!**

OpenHands integrates seamlessly dengan tools favorit Anda!

**📌 Version Control:**
• GitHub - PR reviews, issue automation
• GitLab - MR reviews, CI/CD integration
• Bitbucket - Pull request automation

**💬 Collaboration:**
• Slack - Channel monitoring, notifications
• Jira - Issue creation, sprint management
• Linear - Project tracking automation

**☁️ Cloud Platforms:**
• Vercel, AWS, Azure deployment
• Docker & Kubernetes support

**🔧 API & SDK:**
• REST API for custom integrations
• Python SDK for building agents
• Webhooks for event-driven workflows

**📖 Docs:** https://docs.openhands.dev

OpenHands fits into your existing workflow! 🎯"""
            
            if any(word in msg_lower for word in ['77k', '77k+', 'stars', 'github stars', 'open source', 'oss', 'community']):
                return """**⭐ OpenHands Community!**

**77.1K+ GitHub Stars** - Join the fastest growing AI coding community!

**🏆 Why OpenHands?**
• Open source & transparent
• Model-agnostic (your choice of LLM)
• Enterprise-ready
• Trusted by engineers at TikTok, VMware, Roche, Amazon, Netflix, Mastercard, NVIDIA, Google, dll!

**👥 Community:**
• 65K+ GitHub stars
• Active Slack community (dub.sh/openhands)
• Regular contributions & improvements
• Documentation in 8+ languages!

**🤝 Contribute:**
• Star the repo ⭐
• Join Slack 💬
• Contribute code 💻
• Share feedback 💡

**🔗 Links:**
• GitHub: github.com/All-Hands-AI/OpenHands
• Slack: dub.sh/openhands
• Docs: docs.openhands.dev

Every contribution makes the platform faster, safer, and smarter! 🚀"""
            
            if any(word in msg_lower for word in ['tutorial', 'getting started', 'start', 'begin', 'cara mulai', 'how to start']):
                return """**🚀 Getting Started with OpenHands!**

**1️⃣ Try Cloud (Easiest):**
👉 https://app.all-hands.dev
- Free tier available
- Sign in with GitHub/GitLab
- Start coding immediately!

**2️⃣ CLI (For Developers):**
```bash
pip install openhands
openhands
```

**3️⃣ SDK (For Builders):**
```bash
pip install openhands-agent
```
Docs: docs.openhands.dev/sdk

**4️⃣ Local GUI:**
```bash
docker run -p:3000:3000 openhands/openhands
```
Docs: docs.openhands.dev/openhands/usage/run-openhands/local-setup

**💡 Recommended Path:**
1. Start with Cloud (free, no setup)
2. Try CLI for local development
3. Build custom agents with SDK

**📚 Resources:**
• Docs: docs.openhands.dev
• Examples: github.com/All-Hands-AI/OpenHands
• Community: dub.sh/openhands

Which path interests you most? 🎯"""
        
        return ""


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