"""Tiny static file server for the frontend - no bundler, no Node required.

Usage: python serve.py [port]  (defaults to 5500)
"""
import http.server
import sys

port = int(sys.argv[1]) if len(sys.argv) > 1 else 5500

handler = http.server.SimpleHTTPRequestHandler
with http.server.ThreadingHTTPServer(("", port), handler) as httpd:
    print(f"Serving frontend at http://localhost:{port}")
    httpd.serve_forever()
