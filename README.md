# TinyWebServer

![Build and Release](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/release.yml/badge.svg)
![Build Verification](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/test.yml/badge.svg)

A minimalist static file server written in C.

## Features
- **Any file type**: Serves HTML, CSS, JS, images, fonts, video, audio, ZIP, and more (20+ MIME types)
- **HTTP keep-alive**: connections are reused across requests — no TCP handshake per request
- **mtime cache**: files cached in memory, reloaded only on change (up to 64 entries, 1s re-check interval)
- **Zero-copy cache hits**: serves directly from cached buffer under read lock — no malloc/memcpy per request
- **Thread pool**: 128 pre-created workers, ring-buffer queue (512 slots) — no per-request thread creation
- **CLI arguments**: configurable port and serve directory
- **Directory traversal protection**: `..` in paths returns 403
- **Small footprint**: ~12 KB binary (Windows)
- **Cross-platform**: Windows (MSVC/GCC/Clang) and Linux/macOS (GCC)

## Usage

```
server [port] [directory]
```

| Argument    | Default                     |
|-------------|-----------------------------|
| `port`      | `80`                        |
| `directory` | Directory of the executable |

### Windows
```bat
build.bat
.\server.exe 8080 C:\www
```

### Linux / macOS
```bash
make
./server 8080 /var/www
```

## Benchmarks

Load test using [Bombardier](https://github.com/codesenberg/bombardier) v1.2.6 — 100 concurrent connections, 10 seconds, Windows (v3.4 release binary):

| Endpoint      | Req/sec  | Latency avg | p50      | p99      | Throughput  |
|---------------|----------|-------------|----------|----------|-------------|
| `/`           | ~33,700  | 2.95 ms     | 2.54 ms  | 15.3 ms  | 100 MB/s    |
| `/index.html` | ~35,100  | 2.86 ms     | 2.56 ms  | 11.2 ms  | 104 MB/s    |

### Resource usage (v3.4, Windows, 4-core machine)

| Metric                        | Value           |
|-------------------------------|-----------------|
| Memory — idle (working set)   | ~5.4 MB         |
| Memory — under load           | ~5.9 MB         |
| CPU — under full benchmark load | ~15% total (61% of 1 core) |

The server is nearly CPU-idle at rest and uses under 6 MB of RAM with no files cached. Under 100-connection benchmark load it consumes about one CPU core out of four.

### Running the benchmark yourself
```bash
python tests/bench_bombardier.py [port] [tag]
```
Downloads the server binary from the GitHub release and bombardier automatically, starts the server, and runs the load test.

## License
MIT License. Attribution required (see `LICENSE`).
