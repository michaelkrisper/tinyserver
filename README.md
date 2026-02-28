# TinyWebServer

![Build and Release](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/release.yml/badge.svg)
![Build Verification](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/test.yml/badge.svg)

A minimalist web server designed to serve a single file (`index.html`) directly from memory.

## Features
- **Memory Caching**: The target file is loaded into a pre-allocated buffer once.
- **Concurrency**: Uses `SRWLOCK` (Windows) or `pthread_rwlock` (Linux) for thread-safe parallel access.
- **Cache Support**: Implements ETags and `304 Not Modified` responses.
- **Small Footprint**: Binary size is approximately 12KB (Windows).
- **Fast Path**: Returns `204 No Content` for `/favicon.ico` requests.
- **Cross-Platform**: Supports Windows (MSVC) and Linux/macOS (GCC/Make).

## Benchmarks
Load test results using [Bombardier](https://github.com/codesenberg/bombardier) (100 concurrent connections):
- **Python (`http.server`)**: ~4 RPS
- **TinyWebServer**: ~3,380 RPS

*Note: Benchmarks were performed on an older laptop. Performance is higher on modern hardware.*

## Usage

### Windows
Run the build script from a Developer Command Prompt:
```bat
build.bat
.\server.exe
```

### Linux / macOS
```bash
make
./server
```

The server hosts `index.html` on `http://localhost:80/`.

## License
MIT License. Attribution required (see `LICENSE`).
