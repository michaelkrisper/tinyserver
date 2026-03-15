# TinyWebServer

![Build and Release](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/release.yml/badge.svg)
![Build Verification](https://github.com/michaelkrisper/TinyWebServer/actions/workflows/test.yml/badge.svg)

A minimalist static file server written in C.

## Features
- **Any file type**: Serves HTML, CSS, JS, images, fonts, video, audio, ZIP, and more (20+ MIME types)
- **HTTP keep-alive**: connections are reused across requests — no TCP handshake per request
- **mtime cache**: files cached in memory, reloaded only on change (up to 64 entries, 10s re-check interval)
- **mtime cache + copy-out**: cached responses are copied into a flat send buffer under brief read lock — async I/O proceeds without holding any lock
- **Async I/O**: IOCP on Windows, io_uring on Linux (kernel 6.1+ ring optimizations), kqueue on macOS/BSD — threads never block on individual recv/send
- **Thread pool**: 128 pre-created workers; Linux and macOS use SO_REUSEPORT per-worker sockets (no shared queue)
- **CLI arguments**: configurable port and serve directory
- **Directory traversal protection**: `..` in paths returns 403
- **Small footprint**: ~212 KB binary (Windows)
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

Load test using [Bombardier](https://github.com/codesenberg/bombardier) v1.2.6 — 100 concurrent connections, 10 seconds, Windows (v3.8 release binary):

| Endpoint      | Req/sec  | Latency avg | p99      | Throughput  |
|---------------|----------|-------------|----------|-------------|
| `/`           | ~45,300  | 2.2 ms      | 17.2 ms  | 138 MB/s    |
| `/index.html` | ~44,900  | 2.2 ms      | 17.2 ms  | 138 MB/s    |

Down ~17% from v3.7 (~54,000 RPS). v3.8 replaces the blocking thread pool with native async I/O — IOCP on Windows, io_uring on Linux (kernel 6.1+ `DEFER_TASKRUN` + multishot accept), kqueue on macOS/BSD. The throughput drop comes from the copy-out model: each response is `malloc+memcpy`'d into a flat buffer so the cache lock is released before the async send begins (v3.7 held the lock for the entire synchronous `WSASend`). The tradeoff is better scalability at high connection counts where threads no longer block on individual I/O.

### Resource usage (v3.8, Windows, 4-core machine)

| Metric                        | Value           |
|-------------------------------|-----------------|
| Memory — idle (working set)   | ~5.4 MB         |
| Memory — under load           | ~5.9 MB         |
| CPU — under full benchmark load | ~15% total (61% of 1 core) |

The server is nearly CPU-idle at rest and uses under 6 MB of RAM with no files cached. Under 100-connection benchmark load it consumes about one CPU core out of four.

**Binary size**: ~212 KB (Windows, MSVC release build)

### Running the benchmark yourself
```bash
python tests/bench_bombardier.py [port] [tag]
```
Downloads the server binary from the GitHub release and bombardier automatically, starts the server, and runs the load test.

## License
MIT License. Attribution required (see `LICENSE`).
