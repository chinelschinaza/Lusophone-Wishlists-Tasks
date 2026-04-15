# CHINAZA 
"""Unit tests for the synchronous version of the URL status checker.
"""

import unittest
from unittest.mock import MagicMock, patch

import requests
import task2_sync

class FetchStatusTest(unittest.TestCase):
    """Tests for fetch_status()."""

    @patch("task2_sync.requests.head")
    def test_head_success(self, mock_head):
        mock_head.return_value = MagicMock(status_code=200)
        url, status = task2_sync.fetch_status("https://example.com")
        self.assertEqual(url, "https://example.com")
        self.assertEqual(status, "200")

    @patch("task2_sync.requests.head")
    def test_non_200(self, mock_head):
        mock_head.return_value = MagicMock(status_code=404)
        _, status = task2_sync.fetch_status("https://example.com/missing")
        self.assertEqual(status, "404")

    @patch("task2_sync.requests.get")
    @patch("task2_sync.requests.head")
    def test_405_fallback(self, mock_head, mock_get):
        mock_head.return_value = MagicMock(status_code=405)
        mock_get.return_value = MagicMock(status_code=200)
        _, status = task2_sync.fetch_status("https://example.com")
        self.assertEqual(status, "200")
        mock_get.assert_called_once()

    @patch("task2_sync.requests.get")
    @patch("task2_sync.requests.head")
    def test_501_fallback(self, mock_head, mock_get):
        mock_head.return_value = MagicMock(status_code=501)
        mock_get.return_value = MagicMock(status_code=200)
        _, status = task2_sync.fetch_status("https://example.com")
        self.assertEqual(status, "200")
        mock_get.assert_called_once()

    @patch("task2_sync.requests.head")
    def test_connection_error(self, mock_head):
        mock_head.side_effect = requests.ConnectionError()
        _, status = task2_sync.fetch_status("https://example.com")
        self.assertTrue(status.startswith("ERR"))
        self.assertIn("ConnectionError", status)

    @patch("task2_sync.requests.head")
    def test_timeout(self, mock_head):
        mock_head.side_effect = requests.Timeout()
        _, status = task2_sync.fetch_status("https://example.com")
        self.assertTrue(status.startswith("ERR"))
        self.assertIn("Timeout", status)


if __name__ == "__main__":
    unittest.main()
