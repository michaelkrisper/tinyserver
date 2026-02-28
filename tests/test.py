import urllib.request
import urllib.error

url = "http://localhost:80"

print(f"Testing caching behavior against {url}...")
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        etag = response.headers.get('ETag')
        print(f"First request succeeded. Got ETag: {etag}")

    print("Making second request with If-None-Match header...")
    req2 = urllib.request.Request(url)
    req2.add_header("If-None-Match", etag)
    
    try:
        urllib.request.urlopen(req2)
        print("Second request succeeded (Unexpected, should be 304 Not Modified!)")
    except urllib.error.HTTPError as e:
        if e.code == 304:
            print("Second request status: 304 Not Modified (Expected behavior! Cache hits successfully.)")
        else:
            print(f"Second request status: {e.code}")

except urllib.error.URLError as e:
    print(f"Connection error: {e}. Is the server running?")
