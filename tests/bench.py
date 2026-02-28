import threading
import time
import socket
import sys
import subprocess
import os

HOST = "127.0.0.1"
CONCURRENCY = 100
DURATION = 10

total_requests = [0] * CONCURRENCY
errors = [0] * CONCURRENCY
running = True

def worker(worker_id, port):
    request = f"GET / HTTP/1.1\r\nHost: {HOST}\r\nConnection: close\r\n\r\n".encode('utf-8')
    while running:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((HOST, port))
            s.sendall(request)
            data = s.recv(1024)
            if b"HTTP/1.1" in data:
                total_requests[worker_id] += 1
            else:
                errors[worker_id] += 1
            s.close()
        except Exception:
            errors[worker_id] += 1

def run_benchmark(port):
    global running, total_requests, errors
    running = True
    total_requests = [0] * CONCURRENCY
    errors = [0] * CONCURRENCY
    
    print(f"Starting benchmark against http://{HOST}:{port}/")
    print(f"Concurrency: {CONCURRENCY} workers, Duration: {DURATION}s...")
    
    threads = []
    for i in range(CONCURRENCY):
        t = threading.Thread(target=worker, args=(i, port))
        t.start()
        threads.append(t)
    
    time.sleep(DURATION)
    running = False
    
    for t in threads:
        t.join()
        
    total = sum(total_requests)
    errs = sum(errors)
    rps = total / float(DURATION)
    
    print("\n--- Benchmark Results ---")
    print(f"Total Requests: {total}")
    print(f"Failed Requests: {errs}")
    print(f"Time taken: {DURATION} seconds")
    print(f"Requests Per Second (RPS): {rps:.2f}")

def main():
    print("==========================================")
    print(" COMPARING TINY C SERVER vs PYTHON SERVER ")
    print("==========================================")
    
    # 1. Python server
    print("\n[1] Starting Python http.server on port 8080...")
    python_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    time.sleep(2)
    run_benchmark(8080)
    print("Stopping Python server...")
    python_proc.terminate()
    python_proc.wait()
    
    time.sleep(2)
    
    # 2. C server
    print("\n[2] Starting Tiny C Server on port 80...")
    c_binary = "server.exe" if os.name == 'nt' else "./server"
    c_proc = subprocess.Popen(
        [os.path.join(os.getcwd(), c_binary)], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
        cwd=os.getcwd(),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    time.sleep(2)
    run_benchmark(80)
    print("Stopping Tiny C Server...")
    c_proc.terminate()
    c_proc.wait()
    
    print("\nDone! Look at the 'Requests Per Second' comparison.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "solo":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
        run_benchmark(port)
    else:
        main()
