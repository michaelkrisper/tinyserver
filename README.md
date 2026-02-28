# 🚀 Tiny C Web Server

A brutally minimalist, ultra-high-performance C Web Server. 

Built specifically to serve a single file (`index.html`) out of RAM with face-melting speed. Perfect for microcontrollers, embedded systems, or as an extremely lightweight fallback/maintenance server.

## ✨ Features
* **Zero-Copy RAM Caching:** The file is held in a 2MB pre-allocated RAM buffer. Read operations from clients never hit the disk.
* **Massive Concurrency:** Utilizes OS-level lockless `SRWLOCK` on Windows (and `pthread_rwlock` on POSIX) to allow thousands of clients to read from the cache simultaneously without blocking.
* **Smart ETags & Caching:** Fully implements `HTTP 304 Not Modified` via computed ETags to completely avoid sending data to returning visitors, drastically saving bandwidth.
* **Minimalist Footprint:** The compiled Windows executable is ~12 Kilobytes. RAM usage is completely static.
* **Zero 404 Overhead:** Features a hardcoded, zero-payload `204 No Content` fast-path for `/favicon.ico` to keep logs clean and reduce network overhead from aggressive browsers.
* **Cross-Platform:** Compiles on Windows (MSVC/Winsock) and UNIX/macOS (GCC/POSIX).

## 📊 Benchmark
In a harsh 100-concurrent-connection stress test over localhost:
* 🐍 **Python (`http.server`)**: ~4 RPS (Frequent timeouts/drops under load)
* 🚀 **Tiny C Web Server**: **~880 RPS** (0 failed requests, 100% stability)

## 🛠️ Usage

### Windows (MSVC)
Simply run the included build script from a Developer Command Prompt:
```bat
build.bat
```
Then start the server:
```bat
.\server.exe
```

### Linux / macOS (GCC)
```bash
gcc server.c -o server -lpthread
./server
```

The server will automatically look for an `index.html` file in the same directory and host it on `http://localhost:80/`.

## 📜 License
This project is licensed under the **MIT License**.
You are free to use, modify, and distribute this software, provided that the original copyright notice and permission notice are included in all copies or substantial portions of the software (Attribution required). See the `LICENSE` file for details.
