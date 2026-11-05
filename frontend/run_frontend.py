"""
Sakshi ALPR India - Frontend Server Runner
Reads frontend/.env and serves the premium web dashboard on http://localhost:3000
Run with: python run_frontend.py
"""
import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from dotenv import load_dotenv

FRONTEND_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = FRONTEND_DIR / "public"

# Load frontend/.env
load_dotenv(FRONTEND_DIR / ".env")

PORT = int(os.getenv("PORT", "3000"))
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
APP_TITLE = os.getenv("APP_TITLE", "Sakshi ALPR India")

class CustomFrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_GET(self):
        # Serve index.html with injected BACKEND_API_URL script tag
        if self.path in ("/", "/index.html"):
            index_path = PUBLIC_DIR / "index.html"
            if index_path.exists():
                with open(index_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Inject backend URL configuration into frontend
                injection = f"<script>window.BACKEND_API_URL = '{BACKEND_URL}';</script>\n</head>"
                modified = content.replace("</head>", injection)

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(modified.encode("utf-8"))))
                self.end_headers()
                self.wfile.write(modified.encode("utf-8"))
                return

        return super().do_GET()

def run():
    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, CustomFrontendHandler)
    print("==================================================")
    print(f"  {APP_TITLE} - Frontend Server")
    print(f"  Web Dashboard: http://localhost:{PORT}")
    print(f"  Connected Backend: {BACKEND_URL}")
    print("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping frontend server.")
        httpd.server_close()

if __name__ == "__main__":
    run()

