import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

SERVER = Path(__file__).parents[1] / "scripts" / "actions-server.py"
spec = importlib.util.spec_from_file_location("actions_server", SERVER)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class DiscussionFetchTests(unittest.TestCase):
    def test_review_action_handler_remains_available(self):
        self.assertTrue(callable(getattr(server.Handler, "do_POST", None)))

    @patch.object(server.subprocess, "run")
    def test_pagination_flattens_every_page_and_marks_complete(self, run):
        run.return_value = subprocess.CompletedProcess(
            ["gh"], 0, '[[{"id":1}],[{"id":2}]]', ""
        )
        items, complete, error = server._paged_gh_json("repos/acme/app/pulls/3/reviews")
        self.assertEqual(items, [{"id": 1}, {"id": 2}])
        self.assertTrue(complete)
        self.assertEqual(error, "")
        self.assertIn("--paginate", run.call_args.args[0])

    @patch.object(server.subprocess, "run")
    def test_partial_pages_survive_later_pagination_error(self, run):
        run.return_value = subprocess.CompletedProcess(
            ["gh"], 1, '[[{"id":1}]]', "rate limit"
        )
        items, complete, error = server._paged_gh_json("repos/acme/app/issues/3/comments")
        self.assertEqual(items, [{"id": 1}])
        self.assertFalse(complete)
        self.assertEqual(error, "rate limit")

    @patch.object(server, "_paged_gh_json")
    def test_sources_are_fetched_independently(self, fetch):
        fetch.return_value = ([{"id": 8}], True, "")
        reviews = server.fetch_discussion("acme/app", 3, "reviews")
        comments = server.fetch_discussion("acme/app", 3, "comments")
        self.assertEqual(reviews["reviews"], [{"id": 8}])
        self.assertNotIn("comments", reviews)
        self.assertEqual(comments["comments"], [{"id": 8}])
        self.assertEqual(fetch.call_args_list[0].args[0], "repos/acme/app/pulls/3/reviews")
        self.assertEqual(fetch.call_args_list[1].args[0], "repos/acme/app/issues/3/comments")


if __name__ == "__main__":
    unittest.main()
