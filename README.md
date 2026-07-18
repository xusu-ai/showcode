# ShowCode — Online Code Showcase & Playground

A lightweight online code editor, preview, and sharing platform with AI-powered coding assistance.

## ✨ Features

- **Live Code Editor** — Edit HTML, CSS, and JavaScript with syntax highlighting
- **Real-time Preview** — See your changes instantly as you type
- **Device Simulation** — Preview on desktop, tablet (Xiaomi), and mobile (Apple) layouts
- **One-click Share** — Publish your code snippets and share via URL
- **AI Coding Assistant** — Built-in chatbot powered by LLMs to generate code from natural language descriptions
- **Works Gallery** — Browse and discover community-created projects
- **Zero Dependencies** — Pure frontend, no build tools or frameworks required

## 🚀 Quick Start

### Option 1: Direct Run

```bash
python3 server.py
```

The server starts on `http://0.0.0.0:3000` by default.

### Option 2: systemd Service

```bash
# Copy service file
sudo cp showcode.service /etc/systemd/system/

# Update the WorkingDirectory path if needed
sudo sed -i 's|/home/userroot/showcode|/your/actual/path|' /etc/systemd/system/showcode.service

# Enable and start
sudo systemctl enable --now showcode.service
```

## 🗂️ Project Structure

```
showcode/
├── index.html          # Main application — code editor & gallery UI
├── server.py           # Python HTTP server (stdlib only)
├── showcode.service    # systemd service unit file
├── README.md           # Project documentation (English)
└── README.zh.md        # Project documentation (Chinese)
```

## 🧰 Tech Stack

- **Frontend** — Vanilla HTML/CSS/JavaScript (no frameworks)
- **Backend** — Python 3 `http.server` (stdlib, zero dependencies)
- **AI API** — OpenAI-compatible endpoints (configurable)
- **Deployment** — systemd, supports reverse proxy (Nginx)

## 🤖 AI Coding Assistant

The built-in AI assistant connects to OpenAI-compatible API endpoints:

| Model | Endpoint | Status |
|-------|----------|--------|
| Qwen3.6-27B | `:8099/v1` | Ready |
| DeepSeek V4 Flash | `:8104/v1` | Ready |

The assistant maintains conversation context, generates complete HTML pages, and supports code extraction and execution directly in the editor.

## 🌐 Deployment

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Port Configuration

Edit `server.py` and change `PORT = 3000` to your desired port.

## 📄 License

MIT License

---

*Built with ❤️ for developers who love to show and share their code.*
