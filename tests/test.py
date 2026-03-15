import unittest
import urllib.request
import urllib.error
import os

URL = os.environ.get("SERVER_URL", "http://localhost:80")

class TestTinyServer(unittest.TestCase):
    def test_01_get_root(self):
        """Test getting the root path /"""
        with urllib.request.urlopen(URL) as response:
            body = response.read()
            self.assertEqual(response.status, 200)
            self.assertIn(b"html", body.lower())

    def test_02_get_index(self):
        """Test explicitly getting /index.html"""
        with urllib.request.urlopen(URL + "/index.html") as response:
            body = response.read()
            self.assertEqual(response.status, 200)
            self.assertIn(b"html", body.lower())

    def test_03_404_not_found(self):
        """Test that missing paths return 404"""
        try:
            urllib.request.urlopen(URL + "/doesnotexist")
            self.fail("Expected 404, but request succeeded")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_04_405_method_not_allowed(self):
        """Test that POST requests return 405"""
        try:
            urllib.request.urlopen(urllib.request.Request(URL, data=b"x", method="POST"))
            self.fail("Expected 405, but request succeeded")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 405)

    def test_05_403_directory_traversal(self):
        """Test that directory traversal attempts return 403"""
        try:
            urllib.request.urlopen(URL + "/../etc/passwd")
            self.fail("Expected 403, but request succeeded")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 403)

    def test_06_content_type_html(self):
        """Test that HTML files are served with the correct Content-Type"""
        with urllib.request.urlopen(URL + "/index.html") as response:
            ct = response.headers.get("Content-Type", "")
            self.assertIn("text/html", ct)

    def test_07_query_string_ignored(self):
        """Test that query strings are stripped and the file is still served"""
        with urllib.request.urlopen(URL + "/?v=123") as response:
            self.assertEqual(response.status, 200)

if __name__ == '__main__':
    unittest.main(verbosity=2)
