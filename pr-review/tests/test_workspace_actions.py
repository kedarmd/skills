"""Exercise Review workspace actions through the report and local helper seams."""
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parents[2]
CHROME = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
DRIVER = shutil.which("chromedriver")
SPEC = importlib.util.spec_from_file_location("pr_review_actions_server", ROOT / "pr-review/scripts/actions-server.py")
ACTIONS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ACTIONS)


@unittest.skipUnless(CHROME and DRIVER, "Chromium and chromedriver are required")
class ReviewWorkspaceActionTests(unittest.TestCase):
    def test_staged_comment_is_sent_after_confirmation_and_pr_controls_are_mode_gated(self):
        template = (ROOT / "pr-review/templates/report.html").read_text()
        marker = '{"schema_version":"1.1","review":{"mode":"pull_request","repository":"owner/repo","pull_request":0,"base_sha":"base000","head_sha":"head000"},"summary":{"critical":0,"high":0,"medium":0,"low":0},"overview":{"summary":"Review summary goes here."},"flow":[],"changes":[],"findings":[],"pr_context":null}'
        payload = {"schema_version":"1.1", "review":{"mode":"pull_request","repository":"acme/app","pull_request":3,"base_sha":"base000","head_sha":"abcdef1234567890"}, "summary":{"critical":0,"high":0,"medium":0,"low":0}, "overview":{"summary":"Fixture summary","stats":{"files":1}}, "flow":[], "changes":[{"path":"src/app.py","status":"modified","additions":1,"deletions":0,"patch":"@@ -7 +7 @@\n+new"}], "findings":[], "pr_context":None}
        temporary = tempfile.TemporaryDirectory()
        test_dir = Path(temporary.name)
        original_report = test_dir / "pull-request.html"
        local_report = test_dir / "local.html"
        original_report.write_text(template.replace(marker, json.dumps(payload)))
        local_payload = dict(payload)
        local_payload["review"] = dict(payload["review"], mode="local", pull_request=None)
        local_report.write_text(template.replace(marker, json.dumps(local_payload)))
        capture = test_dir / "submitted-review.json"
        fake_bin = test_dir / "bin"
        fake_bin.mkdir()
        fake_gh = fake_bin / "gh"
        fake_gh.write_text("""#!/bin/sh
if [ "$1" = pr ] && [ "$2" = view ]; then
  case "$*" in
    *--jq*) echo abcdef1234567890 ;;
    *) printf '{\"state\":\"OPEN\",\"createdAt\":\"2026-09-01T10:00:00Z\",\"updatedAt\":\"2026-10-01T10:00:00Z\",\"closedAt\":null,\"mergedAt\":null,\"reviewDecision\":null}' ;;
  esac
  exit 0
fi
if [ "$1" = api ] && [ "$2" = repos/acme/app ]; then
  printf '{\"merge\":true,\"squash\":true,\"rebase\":false}'
  exit 0
fi
if [ "$1" = api ] && [ "$2" = --paginate ]; then
  printf '[[]]'
  exit 0
fi
if [ "$1" = api ] && [ "$2" = graphql ]; then
  printf '{\"data\":{\"repository\":{\"pullRequest\":{\"reviewThreads\":{\"nodes\":[],\"pageInfo\":{\"hasNextPage\":false,\"endCursor\":null}}}}}}'
  exit 0
fi
if [ "$1" = api ] && [ "$2" = repos/acme/app/pulls/3/reviews ]; then
  cat > "$PR_REVIEW_CAPTURE"
  printf '{\"html_url\":\"https://github.com/acme/app/pull/3#review-777\",\"id\":777}'
  exit 0
fi
echo "unexpected fake gh call: $*" >&2
exit 2
""")
        fake_gh.chmod(0o755)
        old_path = os.environ.get("PATH", "")
        old_capture = os.environ.get("PR_REVIEW_CAPTURE")
        os.environ["PATH"] = str(fake_bin) + os.pathsep + old_path
        os.environ["PR_REVIEW_CAPTURE"] = str(capture)
        ACTIONS.Handler.report = original_report
        server = ThreadingHTTPServer(("127.0.0.1", 0), ACTIONS.Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            driver_port = sock.getsockname()[1]
        driver = subprocess.Popen([DRIVER, f"--port={driver_port}", "--allowed-ips=127.0.0.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            report_url = f"http://127.0.0.1:{server.server_port}/review.html"
            request(f"/session/{session}/url", {"url":report_url}, "POST")

            def evaluate(script):
                return request(f"/session/{session}/execute/sync", {"script":script,"args":[]}, "POST")["value"]

            evaluate("document.querySelector('#tab-changes').click();return true")
            self.assertEqual(evaluate("return [...document.querySelectorAll('[data-action]')].map(x=>x.dataset.action).join(',')"), "COMMENT,REQUEST_CHANGES,APPROVE,MERGE,CLOSE")
            evaluate("document.querySelector('[data-action=MERGE]').click();return true")
            for _ in range(60):
                if evaluate("return !!document.querySelector('[data-merge-method]')"):
                    break
                time.sleep(.1)
            evaluate("var m=document.querySelector('[data-merge-method]');m.value='squash';m.dispatchEvent(new Event('change'));return true")
            self.assertIn('"merge_method": "squash"', evaluate("return document.querySelector('[data-payload]').textContent"))
            evaluate("document.querySelector('[data-cancel]').click();return true")
            evaluate("document.querySelector('.diff-row.add [data-compose-comment]').click();var t=document.querySelector('[data-line-draft]');t.value='Please cover this case.';t.dispatchEvent(new Event('input'));document.querySelector('[data-stage-line]').click();return true")
            evaluate("var t=document.querySelector('#review-body');t.value='Review summary';t.dispatchEvent(new Event('input'));document.querySelector('[data-action=COMMENT]').click();return true")
            self.assertTrue(evaluate("return !!document.querySelector('[role=dialog] [data-confirm]')"))
            evaluate("document.querySelector('[role=dialog] [data-confirm]').click();return true")
            for _ in range(60):
                if capture.exists() and capture.stat().st_size:
                    break
                time.sleep(.1)
            self.assertTrue(capture.exists())
            submitted = json.loads(capture.read_text())
            self.assertEqual(submitted["event"], "COMMENT")
            self.assertEqual(submitted["commit_id"], "abcdef1234567890")
            self.assertEqual(submitted["body"], "Review summary")
            self.assertEqual(submitted["comments"], [{"path":"src/app.py","line":7,"side":"RIGHT","body":"Please cover this case."}])

            ACTIONS.Handler.report = local_report
            request(f"/session/{session}/url", {"url":report_url}, "POST")
            self.assertEqual(evaluate("return document.querySelectorAll('[data-action],.discussion-card,.thread-workspace').length"), 0)
            ACTIONS.Handler.report = original_report
            request(f"/session/{session}/url", {"url":original_report.as_uri()}, "POST")
            self.assertEqual(evaluate("return document.querySelectorAll('[data-action],.discussion-card,.thread-workspace').length"), 0)
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
            ACTIONS.Handler.report = None
            os.environ["PATH"] = old_path
            if old_capture is None:
                os.environ.pop("PR_REVIEW_CAPTURE", None)
            else:
                os.environ["PR_REVIEW_CAPTURE"] = old_capture
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
