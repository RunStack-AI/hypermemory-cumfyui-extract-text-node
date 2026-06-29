import json
import unittest
from unittest.mock import MagicMock, patch

from core import (
    DEFAULT_OPENROUTER_MODEL,
    assemble_prompt,
    call_openrouter,
    extract_text,
    format_hypermemory_context,
    recall_hypermemory,
)


class ExtractTextTests(unittest.TestCase):
    def test_first_match(self):
        self.assertEqual(extract_text("Alpha 123 Beta 456", r"\d+", "First Match"), "123")

    def test_all_matches(self):
        self.assertEqual(extract_text("Alpha 123 Beta 456", r"\d+", "All Matches"), "123\n456")

    def test_first_group(self):
        self.assertEqual(extract_text("sku: ABC-123", r"sku: ([A-Z]+)-(\d+)", "First Group", group_index=2), "123")

    def test_all_groups(self):
        self.assertEqual(extract_text("a=1 b=2", r"([a-z])=(\d)", "All Groups", group_index=1), "a\nb")

    def test_invalid_regex_returns_empty_string(self):
        self.assertEqual(extract_text("hello", r"(", "First Match"), "")

    def test_no_match_returns_empty_string(self):
        self.assertEqual(extract_text("hello", r"\d+", "First Match"), "")


class HyperMemoryFormattingTests(unittest.TestCase):
    def test_empty_results(self):
        self.assertEqual(format_hypermemory_context({"results": []}), "")

    def test_flat_results(self):
        context = format_hypermemory_context(
            {"results": [{"key": "brand_voice", "description": "Clear and cinematic.", "score": 0.9}]}
        )
        self.assertIn("brand_voice", context)
        self.assertIn("Clear and cinematic.", context)

    def test_expansion_context(self):
        context = format_hypermemory_context(
            {
                "results": [
                    {
                        "key": "project_launch",
                        "description": "Launch campaign.",
                        "expansion_context": [
                            {
                                "key": "style_visual",
                                "rel": "defines",
                                "description": "High contrast product visuals.",
                            }
                        ],
                    }
                ]
            }
        )
        self.assertIn("Related context:", context)
        self.assertIn("style_visual", context)

    @patch("core.urllib.request.urlopen")
    def test_recall_uses_api_key_and_memory_endpoint(self, urlopen):
        response = MagicMock()
        response.read.return_value = json.dumps({"results": []}).encode("utf-8")
        response.__enter__.return_value = response
        urlopen.return_value = response

        result = recall_hypermemory("hm_test", "https://api.hypermemory.io", "brand", 5)

        self.assertEqual(result, {"results": []})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.hypermemory.io/api/v1/memory/recall")
        self.assertEqual(request.headers["Authorization"], "Bearer hm_test")


class OpenRouterTests(unittest.TestCase):
    def test_assemble_prompt(self):
        prompt = assemble_prompt("launch sneaker", "Bold, premium tone.", "Use teal highlights.")
        self.assertIn("launch sneaker", prompt)
        self.assertIn("Bold, premium tone.", prompt)
        self.assertIn("Use teal highlights.", prompt)

    @patch("core.urllib.request.urlopen")
    def test_openrouter_uses_default_model_and_messages(self, urlopen):
        response = MagicMock()
        response.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "final prompt"}}]}
        ).encode("utf-8")
        response.__enter__.return_value = response
        urlopen.return_value = response

        result = call_openrouter("or_key", "", "system", "user prompt")

        self.assertEqual(result, "final prompt")
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], DEFAULT_OPENROUTER_MODEL)
        self.assertEqual(payload["messages"][0]["content"], "system")
        self.assertEqual(payload["messages"][1]["content"], "user prompt")

    def test_openrouter_requires_key(self):
        with self.assertRaises(Exception):
            call_openrouter("", DEFAULT_OPENROUTER_MODEL, "system", "prompt")


if __name__ == "__main__":
    unittest.main()
