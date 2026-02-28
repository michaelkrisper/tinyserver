import unittest
import urllib.request
import urllib.error

URL = "http://localhost:80"

class TestTinyServer(unittest.TestCase):
    def test_01_get_root(self):
        """Test getting the root path /"""
        req = urllib.request.Request(URL)
        with urllib.request.urlopen(req) as response:
            body = response.read()
            self.assertEqual(response.status, 200, f"Expected 200, got {response.status}. Body: {body}")
            self.assertIn(b"html", body.lower(), f"Expected HTML content, got: {body}")
            self.assertIsNotNone(response.headers.get('ETag'), "ETag missing on /")

    def test_02_get_index(self):
        """Test explicitly getting /index.html"""
        req = urllib.request.Request(URL + "/index.html")
        with urllib.request.urlopen(req) as response:
            body = response.read()
            self.assertEqual(response.status, 200, f"Expected 200, got {response.status}. Body: {body}")
            self.assertIn(b"html", body.lower())

    def test_03_get_favicon(self):
        """Test that /favicon.ico returns 204 No Content for browser optimization"""
        req = urllib.request.Request(URL + "/favicon.ico")
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 204)
            self.assertEqual(response.read(), b"")

    def test_04_404_not_found(self):
        """Test that random paths correctly return 404 Not Found"""
        req = urllib.request.Request(URL + "/doesnotexist")
        try:
            urllib.request.urlopen(req)
            self.fail("Expected 404, but request succeeded")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_05_405_method_not_allowed(self):
        """Test that POST methods are explicitly blocked with 405 Method Not Allowed"""
        req = urllib.request.Request(URL, data=b"post_data", method="POST")
        try:
            urllib.request.urlopen(req)
            self.fail("Expected 405, but request succeeded")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 405)

    def test_06_etag_caching(self):
        """Test caching mechanism yielding a 304 Not Modified status"""
        # First request fetches ETag
        req1 = urllib.request.Request(URL)
        with urllib.request.urlopen(req1) as response:
            etag = response.headers.get('ETag')
            
        self.assertIsNotNone(etag, "ETag header is missing in response from /")

        # Second request mimics browser sending back If-None-Match
        req2 = urllib.request.Request(URL)
        req2.add_header("If-None-Match", etag)
        try:
            urllib.request.urlopen(req2)
            self.fail("Expected 304 Not Modified, but request succeeded")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 304)

    def test_07_etag_spoofing_defense(self):
        """Test that caching ignores the ETag if it's spoofed into the wrong header (e.g. User-Agent)"""
        req1 = urllib.request.Request(URL)
        with urllib.request.urlopen(req1) as response:
            etag = response.headers.get('ETag')

        self.assertIsNotNone(etag, "ETag header is missing in response from /")

        req2 = urllib.request.Request(URL)
        req2.add_header("User-Agent", etag) # Fake placement
        with urllib.request.urlopen(req2) as response:
            self.assertEqual(response.status, 200)

if __name__ == '__main__':
    unittest.main(verbosity=2)
