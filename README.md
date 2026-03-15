# TinyWebServer

![Build and Release](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/release.yml/badge.svg)
![Build Verification](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/test.yml/badge.svg)

A minimalist static file server written in C.

## Features
- **Any file type**: Serves HTML, CSS, JS, images, fonts, video, audio, ZIP, and more (20+ MIME types)
- **HTTP keep-alive**: connections are reused across requests — no TCP handshake per request
- **mtime cache**: files cached in memory, reloaded only on change (up to 64 entries, 10s re-check interval)
- **Zero-copy cache hits**: serves directly from cached buffer under read lock — no malloc/memcpy per request
- **Thread pool**: 128 pre-created workers — queue-based (Windows/macOS) or SO_REUSEPORT per-worker sockets (Linux, no shared queue)
- **CLI arguments**: configurable port and serve directory
- **Directory traversal protection**: `..` in paths returns 403
- **Small footprint**: ~180 KB binary (Windows)
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

Load test using [Bombardier](https://github.com/codesenberg/bombardier) v1.2.6 — 100 concurrent connections, 10 seconds, Windows (v3.7 release binary):

| Endpoint      | Req/sec  | Latency avg | p99      | Throughput  |
|---------------|----------|-------------|----------|-------------|
| `/`           | ~54,000  | 1.8 ms      | 16.8 ms  | 162 MB/s    |
| `/index.html` | ~53,000  | 1.9 ms      | 16.9 ms  | 159 MB/s    |

Roughly on par with v3.6 (~56,400 RPS). v3.7 adds HTTP compliance features — `Date:` header (RFC 7231), `Last-Modified:` header, and `304 Not Modified` responses via `If-Modified-Since` — with no measurable throughput cost. Linux gains `TCP_DEFER_ACCEPT` to skip waking workers until request data arrives.

### Resource usage (v3.7, Windows, 4-core machine)

| Metric                        | Value           |
|-------------------------------|-----------------|
| Memory — idle (working set)   | ~5.4 MB         |
| Memory — under load           | ~5.9 MB         |
| CPU — under full benchmark load | ~15% total (61% of 1 core) |

The server is nearly CPU-idle at rest and uses under 6 MB of RAM with no files cached. Under 100-connection benchmark load it consumes about one CPU core out of four.

**Binary size**: ~183 KB (Windows, MSVC release build)

### Running the benchmark yourself
```bash
python tests/bench_bombardier.py [port] [tag]
```
Downloads the server binary from the GitHub release and bombardier automatically, starts the server, and runs the load test.

## License
MIT License. Attribution required (see `LICENSE`).
