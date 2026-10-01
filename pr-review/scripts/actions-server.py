#!/usr/bin/env python3
"""Serve one PR report locally and execute explicitly confirmed reviews with gh."""
import http.server
import json
import re
import subprocess
import sys
import threading
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit
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
        request = urlsplit(self.path)
        if request.path == "/__pr_review_discussion":
            query = parse_qs(request.query)
            repos, prs = query.get("repo", []), query.get("pr", [])
            repo = repos[0] if len(repos) == 1 else ""
            try:
                pr = int(prs[0]) if len(prs) == 1 else 0
            except ValueError:
                pr = 0
            if not REPO.fullmatch(repo) or pr < 1:
                return self.send_json(400, {"error": "invalid repository or pull request number"})
            source_values = query.get("source", [])
            source = source_values[0] if len(source_values) == 1 else ""
            if source not in ("reviews", "comments"):
                return self.send_json(400, {"error": "source must be reviews or comments"})
            return self.send_json(200, {"discussion": fetch_discussion(repo, pr, source)})
        if request.path == "/__pr_review_context":
            query = parse_qs(request.query)
            repos, prs = query.get("repo", []), query.get("pr", [])
            repo = repos[0] if len(repos) == 1 else ""
            try:
                pr = int(prs[0]) if len(prs) == 1 else 0
            except ValueError:
                pr = 0
            if not REPO.fullmatch(repo) or pr < 1:
                return self.send_json(400, {"error": "invalid repository or pull request number"})
            try:
                result = subprocess.run(
                    ["gh", "pr", "view", str(pr), "--repo", repo, "--json",
                     "state,createdAt,updatedAt,closedAt,mergedAt,reviewDecision"],
                    capture_output=True, text=True, timeout=30, check=True,
                )
                raw = json.loads(result.stdout)
                required = ("state", "createdAt", "updatedAt", "closedAt", "mergedAt", "reviewDecision")
                if not isinstance(raw, dict) or any(key not in raw for key in required):
                    raise ValueError("GitHub returned incomplete pull request context")
                if not isinstance(raw["state"], str):
                    raise ValueError("GitHub returned an invalid pull request lifecycle state")
                lifecycle = raw["state"].lower()
                if lifecycle not in ("open", "closed"):
                    raise ValueError("GitHub returned an unknown pull request lifecycle state")
                dates = (raw["createdAt"], raw["updatedAt"])
                if any(not isinstance(value, str) or not value for value in dates):
                    raise ValueError("GitHub returned incomplete pull request dates")
                lifecycle_dates = [raw["createdAt"], raw["updatedAt"]]
                for key in ("closedAt", "mergedAt"):
                    value = raw[key]
                    if value is not None and (not isinstance(value, str) or not value):
                        raise ValueError("GitHub returned an invalid pull request lifecycle date")
                    if value is not None:
                        lifecycle_dates.append(value)
                for value in lifecycle_dates:
                    try:
                        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    except ValueError as e:
                        raise ValueError("GitHub returned an invalid pull request lifecycle date") from e
                    if parsed.tzinfo is None:
                        raise ValueError("GitHub returned a pull request date without a timezone")
                if lifecycle == "closed" and not raw["closedAt"]:
                    raise ValueError("GitHub returned an incomplete closed pull request")
                if lifecycle == "open" and raw["mergedAt"]:
                    raise ValueError("GitHub returned inconsistent pull request lifecycle data")
                if raw["mergedAt"]:
                    lifecycle = "merged"
                decision = raw["reviewDecision"]
                decisions = {"APPROVED": "approved", "CHANGES_REQUESTED": "changes_requested", "REVIEW_REQUIRED": "review_required"}
                if decision is not None and (not isinstance(decision, str) or decision not in decisions):
                    raise ValueError("GitHub returned an unknown aggregate review decision")
                value = {
                    "lifecycle": lifecycle,
                    "created_at": raw["createdAt"],
                    "updated_at": raw["updatedAt"],
                    "closed_at": raw["closedAt"],
                    "merged_at": raw["mergedAt"],
                    "review_decision": decisions.get(decision, "no_decision"),
                    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
                return self.send_json(200, {"context": value})
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, ValueError) as e:
                detail = getattr(e, "stderr", "") or str(e)
            return self.send_json(502, {"error": detail.strip() or "could not read complete pull request context"})
        if request.path == "/__pr_review_merge_methods":
            repo_values = parse_qs(request.query).get("repo", [])
            repo = repo_values[0] if len(repo_values) == 1 else ""
            if not REPO.fullmatch(repo):
                return self.send_json(400, {"error": "invalid repository"})
            try:
                result = subprocess.run(
                    ["gh", "api", f"repos/{repo}", "--jq", "{merge: .allow_merge_commit, squash: .allow_squash_merge, rebase: .allow_rebase_merge}"],
                    capture_output=True, text=True, timeout=30, check=True,
                )
                settings = json.loads(result.stdout)
                methods = [method for method in ("merge", "squash", "rebase") if settings.get(method)]
                if not methods:
                    return self.send_json(409, {"error": "This repository has no enabled merge method."})
                return self.send_json(200, {"methods": methods})
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
                detail = getattr(e, "stderr", "") or str(e)
                return self.send_json(502, {"error": detail.strip() or "could not read repository merge settings"})
        if request.path not in ("/", "/review.html"):
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
            if action not in ("COMMENT", "APPROVE", "REQUEST_CHANGES", "MERGE", "CLOSE"):
                raise ValueError("unsupported review action")
            body = str(p.get("body", ""))
            if action in ("APPROVE", "REQUEST_CHANGES") and not body.strip():
                raise ValueError("approve and request changes require a review summary")
            comments = p.get("comments", [])
            if not isinstance(comments, list) or len(comments) > 100:
                raise ValueError("invalid comment list")
            if action in ("MERGE", "CLOSE") and (body.strip() or comments):
                raise ValueError("merge and close actions cannot include review content")
            merge_method = p.get("merge_method", "")
            if action == "MERGE" and merge_method not in ("merge", "squash", "rebase"):
                raise ValueError("choose a supported merge method")
            if action != "MERGE" and merge_method:
                raise ValueError("merge method is only valid for merge actions")
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
                return self.send_json(409, {"error": "PR head changed since this report was generated. Refresh the review before taking action."})
            if action == "MERGE":
                settings = subprocess.run(
                    ["gh", "api", f"repos/{repo}", "--jq", "{merge: .allow_merge_commit, squash: .allow_squash_merge, rebase: .allow_rebase_merge}"],
                    capture_output=True, text=True, timeout=30, check=True,
                )
                if not json.loads(settings.stdout).get(merge_method):
                    return self.send_json(409, {"error": f"The {merge_method} merge method is not enabled for this repository. Refresh the report and choose an available method."})
                flag = {"merge": "--merge", "squash": "--squash", "rebase": "--rebase"}[merge_method]
                result = subprocess.run(
                    ["gh", "pr", "merge", str(pr), "--repo", repo, "--match-head-commit", sha, flag],
                    capture_output=True, text=True, timeout=90, stdin=subprocess.DEVNULL,
                )
                if result.returncode:
                    return self.send_json(502, {"error": result.stderr.strip() or result.stdout.strip() or "gh pr merge failed"})
                return self.send_json(200, {"url": f"https://github.com/{repo}/pull/{pr}", "message": "Pull request merged or added to the merge queue."})
            if action == "CLOSE":
                result = subprocess.run(
                    ["gh", "pr", "close", str(pr), "--repo", repo],
                    capture_output=True, text=True, timeout=90, stdin=subprocess.DEVNULL,
                )
                if result.returncode:
                    return self.send_json(502, {"error": result.stderr.strip() or result.stdout.strip() or "gh pr close failed"})
                return self.send_json(200, {"url": f"https://github.com/{repo}/pull/{pr}", "message": "Pull request closed."})
            payload = {"event": action, "commit_id": sha, "body": body, "comments": safe_comments}
            result = subprocess.run(
                ["gh", "api", f"repos/{repo}/pulls/{pr}/reviews", "--method", "POST", "--input", "-"],
                input=json.dumps(payload), capture_output=True, text=True, timeout=90,
            )
            if result.returncode:
                return self.send_json(502, {"error": result.stderr.strip() or result.stdout.strip() or "gh api failed"})
            response = json.loads(result.stdout or "{}")
            return self.send_json(200, {"url": response.get("html_url", ""), "id": response.get("id")})
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
            detail = getattr(e, "stderr", "") or str(e)
            return self.send_json(502, {"error": detail.strip() or "gh request failed"})

def _paged_gh_json(endpoint):
    """Read every page, retaining any complete pages if a later page fails."""
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", endpoint],
        capture_output=True, text=True, timeout=60,
    )
    pages = json.loads(result.stdout or "[]")
    if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
        raise ValueError("GitHub returned an invalid paginated response")
    return [item for page in pages for item in page], result.returncode == 0, result.stderr.strip()


def fetch_discussion(repo, pr, source):
    endpoint = (f"repos/{repo}/pulls/{pr}/reviews" if source == "reviews"
                else f"repos/{repo}/issues/{pr}/comments")
    try:
        items, complete, error = _paged_gh_json(endpoint)
        state = {"items": items, "complete": complete, "error": error if not complete else ""}
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        state = {"items": [], "complete": False, "error": str(e)}
    return {source: state["items"], "sources": {source: state},
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}



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
