#!/usr/bin/env python3
"""ShowCode HTTP server - port 3000"""
import http.server, os, sys, json, re, random
import urllib.request, urllib.error
from urllib.parse import urlparse
from datetime import datetime

PORT = 3000
DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(DIR, 'projects')
PROJECTS_JSON = os.path.join(PROJECTS_DIR, 'projects.json')
UPSTREAM_LLM = 'http://127.0.0.1:8104'

def safe_name(s):
    s = re.sub(r'[\\/:*?"<>|\n\r\t]', '', s or '').strip()
    return s[:50] or 'untitled'

def load_projects():
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    try:
        with open(PROJECTS_JSON, 'r', encoding='utf-8') as f: return json.load(f)
    except Exception:
        return []

def save_projects(projects):
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    with open(PROJECTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def _qs(query):
    return {k: v for k, v in (p.split('=', 1) for p in query.split('&') if '=' in p)}

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)
    def log_message(self, *a): pass

    def _send_json(self, code, payload, extra=None):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        if extra:
            for k, v in extra.items(): self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _llm_call(self, prompt, temp=0.95):
        body = json.dumps({'model': 'DeepSeek-V4-Flash', 'messages': [{'role': 'user', 'content': prompt}],
            'temperature': temp, 'max_tokens': 500, 'stream': False}).encode('utf-8')
        req = urllib.request.Request(UPSTREAM_LLM + '/v1/chat/completions', data=body,
            headers={'Content-Type': 'application/json'}, method='POST')
        return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())['choices'][0]['message']['content']

    def _proxy_llm(self, method, upstream_path=None):
        parsed = urlparse(self.path)
        path = upstream_path or parsed.path
        target = UPSTREAM_LLM + path + ('?' + parsed.query if parsed.query else '')
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else None
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ('host', 'connection', 'transfer-encoding', 'content-length')}
        req = urllib.request.Request(target, data=body, headers=headers, method=method)
        try:
            resp = urllib.request.urlopen(req, timeout=120)
            self.send_response(resp.status)
            self.send_header('Transfer-Encoding', 'chunked')
            for k, v in resp.headers.items():
                if k.lower() not in ('transfer-encoding', 'content-length', 'connection'):
                    self.send_header(k, v)
            self.end_headers()
            while True:
                line = resp.readline()
                if not line:
                    self.wfile.write(b'0\r\n\r\n'); break
                self.wfile.write(format(len(line), 'x').encode() + b'\r\n' + line + b'\r\n')
                self.wfile.flush()
        except urllib.error.HTTPError as e:
            b = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        except Exception as e:
            self._send_json(502, {'error': 'Upstream unavailable: ' + str(e)})

    def do_OPTIONS(self):
        self._send_json(200, {}, {'Allow': 'GET, POST, DELETE, OPTIONS'}) if urlparse(self.path).path.startswith('/api/') else super().do_OPTIONS()

    def do_GET(self):
        p = urlparse(self.path).path
        if p.startswith('/v1/'): self._proxy_llm('GET')
        elif p == '/api/projects': self._send_json(200, load_projects())
        elif p == '/api/suggestions': self._send_suggestions()
        else: super().do_GET()

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/projects':
            try:
                pid = _qs(parsed.query).get('id', '')
                save_projects([p for p in load_projects() if p.get('id') != pid])
                self._send_json(200, {'ok': True})
            except Exception as e:
                self._send_json(500, {'ok': False, 'error': str(e)})
        else:
            self._send_json(404, {'ok': False, 'error': 'not found'})

    def do_POST(self):
        p = urlparse(self.path).path
        if p.startswith('/v1/'): self._proxy_llm('POST')
        elif p == '/api/chat': self._proxy_llm('POST', '/v1/chat/completions')
        elif p == '/api/save': self._save_project()
        else: self._send_json(404, {'ok': False, 'error': 'not found'})

    def _send_suggestions(self):
        lang = _qs(urlparse(self.path).query).get('lang', 'zh')
        is_zh = lang.startswith('zh')
        fb = ['做一个霓虹灯登录页面','生成一个瀑布流图片展示页','创建一个贪吃蛇游戏','画一个粒子动画背景'] if is_zh \
            else ['Make a neon glow login page','Create a waterfall image gallery','Build a Snake game','Make a particle animation background']
        try:
            prompt = ('Generate 4 short creative web project ideas for an online code playground (seed={}). '
                'Keep each under 60 chars. Use HTML+CSS+JS. Respond in {}. '
                'Return ONLY a JSON array of 4 strings: ["a","b","c","d"]. No markdown.'
            ).format(random.randint(1, 99999), 'Chinese' if is_zh else 'English')
            text = self._llm_call(prompt).strip()
            if text.startswith('```'): text = text.split('\n', 1)[1] if '\n' in text else text.replace('```', '').strip()
            if text.endswith('```'): text = text[:-3].strip()
            s = json.loads(text)
            if not isinstance(s, list) or len(s) < 4: raise ValueError
            self._send_json(200, s[:4], {'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0', 'Pragma': 'no-cache'})
        except Exception:
            self._send_json(200, fb)

    def _save_project(self):
        try:
            data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf-8'))
            html, css, js = (data.get('html') or '').strip(), (data.get('css') or '').strip(), (data.get('js') or '').strip()
            code, title = data.get('code') or '', safe_name(data.get('title') or 'untitled')

            os.makedirs(PROJECTS_DIR, exist_ok=True)
            num = max([int(m.group(1)) for name in os.listdir(PROJECTS_DIR) if name != 'projects.json'
                       and (m := re.match(r'^(\d+)_', name))] + [0]) + 1
            date_str = datetime.now().strftime('%Y-%m-%d')
            base_name = '{:03d}_{}_{}'.format(num, date_str, title)
            folder = os.path.join(PROJECTS_DIR, base_name)
            i = 1
            while os.path.exists(folder):
                folder = os.path.join(PROJECTS_DIR, '{}_{}'.format(base_name, i))
                base_name = os.path.basename(folder); i += 1
            os.makedirs(folder)

            saved = []
            for ext, content in [('html', html), ('css', css), ('js', js)]:
                if content:
                    with open(os.path.join(folder, base_name + '.' + ext), 'w', encoding='utf-8') as f: f.write(content)
                    saved.append(ext)

            projects = load_projects()
            project = {
                'id': data.get('id') or datetime.now().strftime('%y%m%d%H%M%S') + os.urandom(2).hex(),
                'code': code, 'title': title, 'views': int(data.get('views', 0)), 'runs': int(data.get('runs', 0)),
                'createdAt': data.get('createdAt') or int(datetime.now().timestamp() * 1000),
                'folder': base_name, 'saved': saved, 'num': num, 'date': date_str,
            }
            projects.insert(0, project)
            save_projects(projects)
            self._send_json(200, {'ok': True, 'projects': projects, 'project': project})
        except Exception as e:
            self._send_json(500, {'ok': False, 'error': str(e)})

if __name__ == '__main__':
    httpd = http.server.ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print("ShowCode server running on http://0.0.0.0:{}".format(PORT), flush=True)
    httpd.serve_forever()