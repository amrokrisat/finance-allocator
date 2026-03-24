"""Minimal local HTTP server for the planner API.

This keeps the MVP lightweight while still giving the Next.js frontend a real
backend endpoint during local development.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple
from urllib.parse import urlparse

from app.api.planner import build_financial_plan


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000


class PlannerRequestHandler(BaseHTTPRequestHandler):
    server_version = "FinanceAllocatorHTTP/0.1"

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json(204, {})

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/planner":
            self._send_json(404, {"error": "Not found"})
            return

        try:
            payload = self._read_json_body()
            response = build_financial_plan(payload)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body."})
            return
        except Exception as exc:  # pragma: no cover
            self._send_json(500, {"error": f"Unexpected server error: {exc}"})
            return

        self._send_json(200, response)

    def log_message(self, format: str, *args: object) -> None:
        # Keep local development output concise.
        return

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        parsed = json.loads(raw_body.decode("utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError("Planner request body must be a JSON object.")
        return parsed

    def _send_json(self, status_code: int, payload: dict) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        if self.command != "HEAD" and status_code != 204:
            self.wfile.write(encoded)


def _server_address() -> Tuple[str, int]:
    host = os.environ.get("PLANNER_API_HOST", DEFAULT_HOST)
    # Render exposes the runtime port through PORT. We still support the
    # explicit local override for consistency during local development.
    port = int(os.environ.get("PLANNER_API_PORT", os.environ.get("PORT", DEFAULT_PORT)))
    return host, port


def main() -> None:
    host, port = _server_address()
    httpd = ThreadingHTTPServer((host, port), PlannerRequestHandler)
    print(f"Planner API listening on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
