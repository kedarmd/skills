import subprocess
import unittest
from unittest.mock import patch

from test_discussion import server


def thread_node(thread_id, comments, has_next=False, end_cursor=None):
    return {
        "id": thread_id, "path": "src/app.py", "line": 8, "originalLine": 6,
        "startLine": None, "originalStartLine": None, "diffSide": "RIGHT",
        "startDiffSide": None, "isResolved": False, "isOutdated": False,
        "comments": {"nodes": comments, "pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor}},
    }


def comment(comment_id, reply_to=None):
    return {"id": comment_id, "body": comment_id, "createdAt": "2026-09-30T10:00:00Z",
            "updatedAt": "2026-09-30T10:00:00Z", "url": "https://example.test/comment",
            "path": "src/app.py", "line": 8, "originalLine": 6,
            "author": {"login": "reviewer"}, "replyTo": {"id": reply_to} if reply_to else None}


def connection(nodes, has_next=False, end_cursor=None):
    return {"repository": {"pullRequest": {"reviewThreads": {
        "nodes": nodes, "pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor}}}}}


class ReviewThreadFetchTests(unittest.TestCase):
    @patch.object(server, "_graphql")
    def test_outer_and_nested_pages_preserve_reply_parent(self, graphql):
        graphql.side_effect = [
            connection([thread_node("thread-1", [comment("root")], True, "comment-cursor")], True, "thread-cursor"),
            {"node": {"comments": {"nodes": [comment("reply", "root")], "pageInfo": {"hasNextPage": False, "endCursor": None}}}},
            connection([thread_node("thread-2", [comment("another-root")])]),
        ]
        result = server.fetch_review_threads("acme/app", 3)
        self.assertTrue(result["complete"])
        self.assertEqual([t["id"] for t in result["threads"]], ["thread-1", "thread-2"])
        self.assertEqual([c["reply_to_id"] for c in result["threads"][0]["comments"]], [None, "root"])
        self.assertEqual(result["threads"][0]["comments"][1]["author"], "reviewer")
        self.assertTrue(result["threads"][0]["comments_complete"])

    @patch.object(server, "_graphql")
    def test_nested_reply_failure_keeps_partial_thread(self, graphql):
        graphql.side_effect = [
            connection([thread_node("thread-1", [comment("root")], True, "comment-cursor")]),
            subprocess.CalledProcessError(1, ["gh"], stderr="rate limited"),
        ]
        result = server.fetch_review_threads("acme/app", 3)
        self.assertFalse(result["complete"])
        self.assertEqual(len(result["threads"]), 1)
        self.assertFalse(result["threads"][0]["comments_complete"])
        self.assertEqual([c["id"] for c in result["threads"][0]["comments"]], ["root"])
        self.assertIn("rate limited", result["error"])

    @patch.object(server, "_graphql")
    def test_outer_page_failure_keeps_prior_threads(self, graphql):
        graphql.side_effect = [
            connection([thread_node("thread-1", [comment("root")])], True, "next"),
            subprocess.CalledProcessError(1, ["gh"], stderr="connection lost"),
        ]
        result = server.fetch_review_threads("acme/app", 3)
        self.assertFalse(result["complete"])
        self.assertEqual([t["id"] for t in result["threads"]], ["thread-1"])
        self.assertIn("connection lost", result["error"])


if __name__ == "__main__":
    unittest.main()
