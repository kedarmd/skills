#!/usr/bin/env python3
"""Serve one PR report locally and execute explicitly confirmed reviews with gh."""
import http.server
import json
import re
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path


MAX_BODY = 1_000_000
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA = re.compile(r"^[0-9a-fA-F]{7,64}$")


class Handler(http.server.BaseHTTPRequestHandler):
    report = None

    def log_message(self, fmt, *args):
        print("[pr-review] " + fmt % args)

    def send_json(self, status, value):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path not in ("/", "/review.html"):
            return self.send_json(404, {"error": "not found"})
        data = self.report.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/__pr_review_action":
            return self.send_json(404, {"error": "not found"})
        origin = self.headers.get("Origin", "")
        if origin != "http://127.0.0.1:" + str(self.server.server_port):
            return self.send_json(403, {"error": "request must come from this local report"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > MAX_BODY:
                raise ValueError("invalid request size")
            p = json.loads(self.rfile.read(size))
            repo, pr, sha, action = p["repo"], int(p["pr"]), p["commit_sha"], p["action"]
            if not REPO.fullmatch(repo) or pr < 1 or not SHA.fullmatch(sha):
                raise ValueError("invalid repository, PR number, or head SHA")
            if action not in ("COMMENT", "APPROVE", "REQUEST_CHANGES"):
                raise ValueError("unsupported review action")
            body = str(p.get("body", ""))
            if action != "COMMENT" and not body.strip():
                raise ValueError("approve and request changes require a review summary")
            comments = p.get("comments", [])
            if not isinstance(comments, list) or len(comments) > 100:
                raise ValueError("invalid comment list")
            safe_comments = []
            for c in comments:
                file, line, side, text = str(c["file"]), int(c["line"]), c["side"], str(c["body"])
                if not file or file.startswith("/") or ".." in Path(file).parts or line < 1 or side not in ("LEFT", "RIGHT") or not text.strip():
                    raise ValueError("invalid inline comment location or body")
                safe_comments.append({"path": file, "line": line, "side": side, "body": text})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            return self.send_json(400, {"error": str(e)})

        try:
            current = subprocess.run(
                ["gh", "pr", "view", str(pr), "--repo", repo, "--json", "headRefOid", "--jq", ".headRefOid"],
                capture_output=True, text=True, timeout=30, check=True,
            ).stdout.strip()
            if current.lower() != sha.lower():
                return self.send_json(409, {"error": "PR head changed since this report was generated. Refresh the review and re-check comment lines before posting."})
            payload = {"event": action, "commit_id": sha, "body": body, "comments": safe_comments}
            result = subprocess.run(
                ["gh", "api", f"repos/{repo}/pulls/{pr}/reviews", "--method", "POST", "--input", "-"],
                input=json.dumps(payload), capture_output=True, text=True, timeout=90,
            )
            if result.returncode:
                return self.send_json(502, {"error": result.stderr.strip() or result.stdout.strip() or "gh api failed"})
            response = json.loads(result.stdout or "{}")
            return self.send_json(200, {"url": response.get("html_url", ""), "id": response.get("id")})
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError) as e:
            detail = getattr(e, "stderr", "") or str(e)
            return self.send_json(502, {"error": detail.strip() or "gh request failed"})


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: actions-server.py <report.html>")
    report = Path(sys.argv[1]).resolve(strict=True)
    if not report.is_file():
        raise SystemExit("report must be a file")
    Handler.report = report
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    url = f"http://127.0.0.1:{server.server_port}/review.html"
    print(f"Serving {report} at {url}")
    print("Keep this terminal open while using the report; press Ctrl-C to stop.")
    threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[pr-review] stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
