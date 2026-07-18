#!/usr/bin/env python3
"""Simple HTTP server for ShowCode - port 3000"""
import http.server
import os
import sys

PORT = 3000
DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def log_message(self, format, *args):
        pass  # quiet

if __name__ == '__main__':
    httpd = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"ShowCode server running on http://0.0.0.0:{PORT}", flush=True)
    sys.stdout.flush()
    httpd.serve_forever()
