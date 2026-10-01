"""Exercise discussion rendering through the self-contained report artifact."""
import json
import shutil
import socket
import subprocess
import threading
import time
import unittest
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parents[2]
CHROME = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
DRIVER = shutil.which("chromedriver")


@unittest.skipUnless(CHROME and DRIVER, "Chromium and chromedriver are required")
class ReportArtifactTests(unittest.TestCase):
    def test_discussion_order_partial_retry_and_show_all(self):
        template = (ROOT / "pr-review/templates/report.html").read_text()
        marker = '{"schema_version":"1.1","review":{"mode":"pull_request","repository":"owner/repo","pull_request":0,"base_sha":"base000","head_sha":"head000"},"summary":{"critical":0,"high":0,"medium":0,"low":0},"overview":{"summary":"Review summary goes here."},"flow":[],"changes":[],"findings":[],"pr_context":null}'
        payload = {"schema_version":"1.1", "review":{"mode":"pull_request","repository":"acme/app","pull_request":3,"base_sha":"base000","head_sha":"head000"}, "summary":{"critical":0,"high":0,"medium":0,"low":0}, "overview":{"summary":"Fixture"}, "flow":[],"changes":[],"findings":[],"pr_context":None}
        page = template.replace(marker, json.dumps(payload))
        reviews = [
            {"user":{"login":"a"},"submitted_at":"2026-09-28T12:00:00Z","state":"APPROVED","body":"old decision"},
            {"user":{"login":"b"},"submitted_at":"2026-09-29T12:00:00Z","state":"COMMENTED","body":"middle decision"},
            {"user":{"login":"c"},"submitted_at":"2026-09-30T12:00:00Z","state":"CHANGES_REQUESTED","body":"new decision"},
        ]
        comments = [{"user":{"login":f"user{i}"},"created_at":f"2026-09-{i:02d}T10:00:00Z","body":f"comment {i}"} for i in range(1, 12)]
        calls = {"reviews":0}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def reply(self, status, value, content_type="application/json"):
                body = value if isinstance(value, bytes) else json.dumps(value).encode()
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path == "/":
                    return self.reply(200, page.encode(), "text/html")
                if self.path.startswith("/__pr_review_context"):
                    context = {"lifecycle":"open","created_at":"2026-09-01T10:00:00Z","updated_at":"2026-10-01T10:00:00Z","closed_at":None,"merged_at":None,"review_decision":"no_decision","fetched_at":"2026-10-01T10:00:00Z"}
                    return self.reply(200, {"context":context})
                if self.path.startswith("/__pr_review_discussion"):
                    source = self.path.split("source=")[1]
                    if source == "reviews":
                        calls["reviews"] += 1
                        if calls["reviews"] > 1:
                            return self.reply(502, {"error":"rate limited"})
                        state = {"items":reviews,"complete":False,"error":"rate limited after first page"}
                        result = {"reviews":reviews,"sources":{"reviews":state}}
                    else:
                        state = {"items":comments,"complete":True,"error":""}
                        result = {"comments":comments,"sources":{"comments":state}}
                    result["fetched_at"] = "2026-10-01T10:00:00Z"
                    return self.reply(200, {"discussion":result})
                return self.reply(404, {"error":"not found"})

        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            driver_port = sock.getsockname()[1]
        driver = subprocess.Popen([DRIVER, f"--port={driver_port}", "--allowed-ips=127.0.0.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        session = None

        def request(path, value=None, method=None):
            body = json.dumps(value).encode() if value is not None else None
            req = urllib.request.Request(f"http://127.0.0.1:{driver_port}{path}", data=body, headers={"Content-Type":"application/json"}, method=method)
            with urllib.request.urlopen(req, timeout=8) as response:
                return json.load(response)

        try:
            for _ in range(60):
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{driver_port}/status", timeout=.2)
                    break
                except Exception:
                    time.sleep(.1)
            caps = {"capabilities":{"alwaysMatch":{"browserName":"chrome","goog:chromeOptions":{"binary":CHROME,"args":["--headless=new","--no-sandbox","--disable-dev-shm-usage"]}}}}
            session = request("/session", caps)["value"]["sessionId"]
            request(f"/session/{session}/url", {"url":f"http://127.0.0.1:{server.server_port}/"}, "POST")

            def evaluate(script):
                return request(f"/session/{session}/execute/sync", {"script":script,"args":[]}, "POST")["value"]

            for _ in range(60):
                if evaluate("return document.querySelectorAll('.discussion-card')[1].querySelectorAll('.discussion-item').length") == 10:
                    break
                time.sleep(.1)
            self.assertEqual(evaluate("return [...document.querySelectorAll('.discussion-group')].map(x=>x.textContent).join('|')"), "changes requested|commented|approved")
            self.assertEqual(evaluate("return [...document.querySelectorAll('.discussion-card')[0].querySelectorAll('.discussion-item p')].map(x=>x.textContent).join('|')"), "new decision|middle decision|old decision")
            self.assertEqual(evaluate("return document.querySelector('.discussion-card .discussion-item strong').textContent"), "c")
            self.assertEqual(evaluate("return document.querySelector('.discussion-card').querySelector('time').getAttribute('datetime')"), "2026-09-30T12:00:00Z")
            self.assertIn("Partial", evaluate("return document.querySelector('.discussion-card').textContent"))
            fetched_before = evaluate("var s=document.querySelector('.discussion-card .discussion-head .status').textContent; return s.match(/fetched (.*)$/)[1]")
            self.assertEqual(evaluate("return document.querySelectorAll('.show-all')[0].textContent"), "Show all 11 comments")
            evaluate("document.querySelector('.show-all').click(); return true")
            self.assertEqual(evaluate("return document.querySelectorAll('.discussion-card')[1].querySelectorAll('.discussion-item').length"), 11)
            evaluate("document.querySelector('[data-discussion-refresh=reviews]').click(); return true")
            time.sleep(.2)
            self.assertEqual(evaluate("return [...document.querySelectorAll('.discussion-card')[0].querySelectorAll('.discussion-item p')].map(x=>x.textContent).join('|')"), "new decision|middle decision|old decision")
            self.assertIn("Refresh failed: rate limited", evaluate("return document.querySelector('.discussion-card').textContent"))
            fetched_after = evaluate("var s=document.querySelector('.discussion-card .discussion-head .status').textContent; return s.match(/fetched (.*)$/)[1]")
            self.assertEqual(fetched_after, fetched_before)
        finally:
            if session:
                try:
                    request(f"/session/{session}", {}, "DELETE")
                except Exception:
                    pass
            driver.terminate()
            driver.wait(timeout=5)
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
