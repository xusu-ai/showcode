# ShowCode - 在线代码展示与分享平台

一个轻量级的在线代码展示与分享工具，支持代码编辑、语法高亮、实时预览和一键分享。

## ✨ 功能特性

- **代码编辑器**：支持多语言语法高亮，内置 HTML/CSS/JS 编辑
- **实时预览**：编辑代码后自动渲染预览结果
- **一键分享**：生成分享链接，快速展示你的代码片段
- **简洁界面**：现代化 UI 设计，响应式布局，支持移动端
- **零依赖部署**：基于 Python 标准库，无需安装任何第三方依赖

## 🚀 快速部署

### 方式一：直接运行

```bash
python3 server.py
```

服务器默认监听 `0.0.0.0:3000`，浏览器访问 `http://你的IP:3000` 即可。

### 方式二：systemd 服务

```bash
# 复制服务文件
sudo cp showcode.service /etc/systemd/system/

# 修改 WorkingDirectory 路径（如果需要）
sudo sed -i 's|/home/userroot/showcode|/你的实际路径|' /etc/systemd/system/showcode.service

# 启动并设置开机自启
sudo systemctl enable --now showcode.service
```

## 📁 项目结构

```
showcode/
├── index.html          # 主页面 - 代码编辑器与展示界面
├── server.py           # Python HTTP 服务器（基于 http.server）
├── showcode.service    # systemd 服务配置文件
└── README.md           # 项目说明
```

## 🔧 技术栈

- **前端**: HTML + CSS + JavaScript（原生，无框架依赖）
- **后端**: Python 标准库 http.server
- **部署**: systemd（支持开机自启）

## 📝 配置说明

### 修改端口

编辑 `server.py`，修改 `PORT = 3000` 为你想要的端口号：

```python
PORT = 3000   # 改为你需要的端口
```

### Nginx 反向代理（可选）

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

## 📄 许可证

MIT License
