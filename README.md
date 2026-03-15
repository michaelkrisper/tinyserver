# TinyWebServer

![Build and Release](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/release.yml/badge.svg)
![Build Verification](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/test.yml/badge.svg)

A minimalist static file server written in C. Files are read from disk on every request — no caching, no global state.

## Features
- **Any file type**: Serves HTML, CSS, JS, images, fonts, video, audio, ZIP, and more (20+ MIME types)
- **mtime cache**: Files are cached in memory and reloaded only when modified (up to 64 entries)
- **CLI arguments**: Configurable port and serve directory
- **Thread pool**: 32 pre-created worker threads, ring-buffer queue (256 slots) — no per-request thread creation
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

Load test using [Bombardier](https://github.com/codesenberg/bombardier) v1.2.6 — 100 concurrent connections, 10 seconds, Windows (v3.2 release binary):

| Endpoint      | Req/sec | Latency avg | p50     | p99     |
|---------------|---------|-------------|---------|---------|
| `/`           | ~338    | 318 ms      | 317 ms  | 345 ms  |
| `/index.html` | ~329    | 319 ms      | 317 ms  | 381 ms  |

*Thread pool (v3.2) improved throughput ~8% and tightened p99 vs. thread-per-connection (v3.1). Performance is higher on Linux.*

### Running the benchmark yourself
```bash
python tests/bench_bombardier.py [port] [tag]
```
Downloads the server binary from the GitHub release and bombardier automatically, starts the server, and runs the load test.

## License
MIT License. Attribution required (see `LICENSE`).
