import os
import subprocess
import urllib.request
import sys

# Professional HTTP load tester: bombardier
BOMBARDIER_URL = "https://github.com/codesenberg/bombardier/releases/download/v1.2.6/bombardier-windows-amd64.exe"
BOMBARDIER_EXE = os.path.join(os.path.dirname(__file__), "bombardier.exe")
CONCURRENCY = 100
DURATION = "10s"

def ensure_bombardier():
    if not os.path.exists(BOMBARDIER_EXE):
        if os.name == 'nt':
            print("Downloading Bombardier (Professional HTTP Load Tester)...")
            urllib.request.urlretrieve(BOMBARDIER_URL, BOMBARDIER_EXE)
            print("Download complete.")
        else:
            print("Please install bombardier on Linux: go install github.com/codesenberg/bombardier@latest")
            sys.exit(1)

def run_benchmark(target_url):
    ensure_bombardier()
    print("\n=======================================================")
    print(f" Running Professional Benchmark against {target_url}")
    print("=======================================================")
    print(f"Tool Engine: Bombardier")
    print(f"Concurrency: {CONCURRENCY} connections")
    print(f"Duration:    {DURATION}\n")
    
    cmd = [BOMBARDIER_EXE, "-c", str(CONCURRENCY), "-d", DURATION, target_url]
    subprocess.run(cmd)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:80/"
    try:
        run_benchmark(url)
    except KeyboardInterrupt:
        print("\nBenchmark aborted.")
