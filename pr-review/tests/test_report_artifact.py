"""Exercise discussion and inline-thread rendering through the report artifact."""
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
        payload = {"schema_version":"1.1", "review":{"mode":"pull_request","repository":"acme/app","pull_request":3,"base_sha":"base000","head_sha":"head000"}, "summary":{"critical":0,"high":0,"medium":0,"low":1}, "overview":{"summary":"Fixture"},"flow":[],"changes":[{"path":"src/a.py","status":"modified","additions":1,"deletions":1,"patch":"@@ -7 +7 @@\n-old\n+new"}],"findings":[{"id":"F-001","severity":"LOW","title":"Related finding","summary":"Fixture finding","locations":[{"file":"src/a.py","start_line":6,"end_line":6}]}],"pr_context":None}
        page = template.replace(marker, json.dumps(payload))
        reviews = [
            {"user":{"login":"a"},"submitted_at":"2026-09-28T12:00:00Z","state":"APPROVED","body":"old decision"},
            {"user":{"login":"b"},"submitted_at":"2026-09-29T12:00:00Z","state":"COMMENTED","body":"middle decision"},
            {"user":{"login":"c"},"submitted_at":"2026-09-30T12:00:00Z","state":"CHANGES_REQUESTED","body":"new decision"},
        ]
        comments = [{"user":{"login":f"user{i}"},"created_at":f"2026-09-{i:02d}T10:00:00Z","body":f"comment {i}"} for i in range(1, 12)]
        def thread(thread_id, path, line, resolved, outdated, reply=False):
            root_id = thread_id + "-root"
            items = [{"id":root_id,"reply_to_id":None,"author":"root-author","created_at":"2026-09-30T10:00:00Z","body":"root comment","url":"https://example.test/root"}]
            if reply:
                items.append({"id":thread_id+"-reply","reply_to_id":root_id,"author":"reply-author","created_at":"2026-09-30T11:00:00Z","body":"nested reply","url":"https://example.test/reply"})
            return {"id":thread_id,"path":path,"line":line,"original_line":line,"start_line":line-2 if line==7 else line,"original_start_line":None,"side":"RIGHT","resolved":resolved,"outdated":outdated,"comments":items,"comments_complete":True}
        threads = [thread("t-unresolved","src/a.py",7,False,False,True),thread("t-resolved","src/a.py",8,True,False),thread("t-outdated","src/b.py",9,False,True)]
        calls = {"reviews":0,"threads":0}

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
                if self.path.startswith("/__pr_review_threads"):
                    calls["threads"] += 1
                    if calls["threads"] > 1:
                        return self.reply(502, {"error":"thread refresh failed"})
                    thread_data = {"threads":threads,"complete":False,"error":"connection interrupted after page one","fetched_at":"2026-10-01T10:00:00Z"}
                    return self.reply(200, {"thread_data":thread_data})
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
            evaluate("document.querySelector('#tab-changes').click(); return true")
            for _ in range(60):
                if evaluate("return document.querySelectorAll('.thread-item').length") == 3:
                    break
                time.sleep(.1)
            self.assertIn("Partial", evaluate("return document.querySelector('.thread-workspace').textContent"))
            thread_timestamp = evaluate("var s=document.querySelector('.thread-workspace-head .status').textContent; return s.match(/fetched (.*)$/)[1]")
            self.assertTrue(evaluate("return document.querySelector('#thread-t-unresolved').open"))
            self.assertFalse(evaluate("return document.querySelector('#thread-t-resolved').open"))
            self.assertFalse(evaluate("return document.querySelector('#thread-t-outdated').open"))
            self.assertTrue(evaluate("return document.querySelector('#thread-t-unresolved .thread-comment').querySelector('.thread-comment')!==null"))
            self.assertEqual(evaluate("return document.querySelectorAll('.thread-findings [data-id=F-001]').length"), 1)
            self.assertEqual(evaluate("return document.querySelector('.thread-anchor').textContent"), "1 thread")
            self.assertEqual(evaluate("return document.querySelector('.thread-anchor').dataset.threadJump"), "t-unresolved")
            evaluate("document.querySelector('.thread-anchor').click(); return true")
            self.assertFalse(evaluate("return document.querySelector('#thread-t-resolved').open"))
            self.assertTrue(evaluate("return document.querySelector('#thread-t-unresolved').open"))
            evaluate("document.querySelector('[data-thread-status=resolved]').click(); return true")
            self.assertEqual(evaluate("return document.querySelector('.thread-filters > span').textContent.trim()"), "2 of 3 threads")
            evaluate("var s=document.querySelector('[data-thread-file]');s.value='src/a.py';s.dispatchEvent(new Event('change'));return true")
            self.assertEqual(evaluate("return document.querySelector('.thread-filters > span').textContent.trim()"), "1 of 3 threads")
            evaluate("document.querySelector('[data-thread-clear]').click(); return true")
            self.assertEqual(evaluate("return document.querySelector('.thread-filters > span').textContent.trim()"), "3 of 3 threads")
            evaluate("document.querySelector('[data-thread-retry]').click(); return true")
            time.sleep(.2)
            self.assertEqual(evaluate("return document.querySelectorAll('.thread-item').length"), 3)
            self.assertIn("Refresh failed: thread refresh failed", evaluate("return document.querySelector('.thread-workspace').textContent"))
            after_thread_retry = evaluate("var s=document.querySelector('.thread-workspace-head .status').textContent; return s.match(/fetched (.*)$/)[1]")
            self.assertEqual(after_thread_retry, thread_timestamp)
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
