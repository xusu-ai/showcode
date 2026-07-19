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
├── index.html               # Main application — code editor & gallery UI
├── server.py                # Python backend (stdlib only, handles /api/save)
├── projects/                # Saved projects land here (auto-created)
├── nginx.showcode.conf      # nginx site config (drop-in for new servers)
├── deploy.sh                # all-in-one deploy/ops script (see below)
├── README.md                # Project documentation (English)
└── README.zh.md             # Project documentation (Chinese)
```

## 🔁 迁移到新服务器（标准流程）

业务代码与 nginx 解耦：nginx 只做反向代理和静态服务，所有业务逻辑在 `server.py` 里。
新机器上只需 nginx 标准安装 + 拷贝本文件夹即可运行：

```bash
# 1) 目标服务器：安装标准 nginx
sudo apt update && sudo apt install -y nginx python3

# 2) 把整个 showcode/ 目录拷到目标服务器（任意路径，例如 /opt/showcode）
sudo mkdir -p /opt && sudo cp -r showcode /opt/

# 3) 进入目录跑一键部署脚本
cd /opt/showcode && sudo ./deploy.sh
```

`deploy.sh` 子命令（合并 systemd 单元、启停脚本于一体）：

| 命令 | 用途 |
|------|------|
| `sudo ./deploy.sh` | 完整部署：链 nginx 配置 + reload + 启动后端 |
| `sudo ./deploy.sh start` / `stop` / `restart` / `status` | 后端运维 |
| `sudo ./deploy.sh service` | 安装为 systemd 开机自启服务（无需单独 .service 文件）|

### 端口与目录调整

只在 `nginx.showcode.conf` 里改两处即可：

- `root /showcode;` → 改成实际目录路径
- `proxy_pass http://127.0.0.1:8104/v1/;` → 改成你的 LLM API 上游（如不需要 AI 可整段删除）

后端端口（默认 3000）想改的话，改 `server.py` 里的 `PORT =` 即可；同时同步 `nginx.showcode.conf` 里的 `proxy_pass` 端口。

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
