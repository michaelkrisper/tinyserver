#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#define PORT 80
#define FILE_NAME "index.html"
#define MAX_REQ 2048
#define MAX_CACHE_SIZE (2 * 1024 * 1024)

typedef struct {
  char data[MAX_CACHE_SIZE];
  size_t size;
  char etag[64];
  time_t last_mtime;
} CacheEntry;

CacheEntry g_cache = {0};

#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")

SRWLOCK g_cache_lock;
#define RWLOCK_INIT() InitializeSRWLock(&g_cache_lock)
#define READ_LOCK() AcquireSRWLockShared(&g_cache_lock)
#define READ_UNLOCK() ReleaseSRWLockShared(&g_cache_lock)
#define WRITE_LOCK() AcquireSRWLockExclusive(&g_cache_lock)
#define WRITE_UNLOCK() ReleaseSRWLockExclusive(&g_cache_lock)
#define RWLOCK_DESTROY()

void os_net_init() {
  WSADATA wsa;
  WSAStartup(MAKEWORD(2, 2), &wsa);
}

void os_net_cleanup() { WSACleanup(); }

void os_set_socket_timeout(SOCKET client, int seconds) {
  DWORD timeout = seconds * 1000;
  setsockopt(client, SOL_SOCKET, SO_RCVTIMEO, (const char *)&timeout, sizeof(timeout));
}

void handle_client(SOCKET client);

DWORD WINAPI client_thread_wrapper(LPVOID arg) {
  SOCKET client = (SOCKET)(intptr_t)arg;
  handle_client(client);
  return 0;
}

void os_start_client_thread(SOCKET client) {
  HANDLE thread = CreateThread(NULL, 0, client_thread_wrapper, (void *)(intptr_t)client, 0, NULL);
  if (thread) {
    CloseHandle(thread);
  } else {
    closesocket(client);
  }
}

#else
// --- POSIX (Linux/macOS) Implementation ---

#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <signal.h>
#include <stdint.h>
#include <sys/socket.h>
#include <unistd.h>
#define SOCKET int
#define INVALID_SOCKET (-1)
#define SOCKET_ERROR (-1)
#define closesocket(s) close(s)

pthread_rwlock_t g_cache_lock = PTHREAD_RWLOCK_INITIALIZER;
#define RWLOCK_INIT() ((void)0)
#define READ_LOCK() pthread_rwlock_rdlock(&g_cache_lock)
#define READ_UNLOCK() pthread_rwlock_unlock(&g_cache_lock)
#define WRITE_LOCK() pthread_rwlock_wrlock(&g_cache_lock)
#define WRITE_UNLOCK() pthread_rwlock_unlock(&g_cache_lock)
#define RWLOCK_DESTROY() pthread_rwlock_destroy(&g_cache_lock)

void os_net_init() { signal(SIGPIPE, SIG_IGN); }
void os_net_cleanup() {}

void os_set_socket_timeout(SOCKET client, int seconds) {
  struct timeval timeout;
  timeout.tv_sec = seconds;
  timeout.tv_usec = 0;
  setsockopt(client, SOL_SOCKET, SO_RCVTIMEO, (const void *)&timeout, sizeof(timeout));
}

void handle_client(SOCKET client);

void *client_thread_wrapper(void *arg) {
  SOCKET client = (SOCKET)(intptr_t)arg;
  handle_client(client);
  return NULL;
}

void os_start_client_thread(SOCKET client) {
  pthread_t thread;
  if (pthread_create(&thread, NULL, client_thread_wrapper, (void *)(intptr_t)client) == 0) {
    pthread_detach(thread);
  } else {
    closesocket(client);
  }
}

#endif

void update_cache() {
  struct _stat st;
  if (_stat(FILE_NAME, &st) == 0) {
    int needs_update = 0;

    READ_LOCK();
    if (st.st_mtime != g_cache.last_mtime || g_cache.size == 0) {
      needs_update = 1;
    }
    READ_UNLOCK();

    if (needs_update) {
      FILE *f = NULL;
      if (fopen_s(&f, FILE_NAME, "rb") == 0) {
        WRITE_LOCK();
        if (st.st_mtime != g_cache.last_mtime || g_cache.size == 0) {
          g_cache.size = fread(g_cache.data, 1, (size_t)st.st_size > MAX_CACHE_SIZE ? MAX_CACHE_SIZE : (size_t)st.st_size, f);
          g_cache.last_mtime = st.st_mtime;
          snprintf(g_cache.etag, sizeof(g_cache.etag), "W/\"%llx-%zx\"", (unsigned long long)g_cache.last_mtime, g_cache.size);
          printf("[Cache] Loaded %s into RAM (%zu bytes), ETag: %s\n", FILE_NAME, g_cache.size, g_cache.etag);
        }
        WRITE_UNLOCK();
        fclose(f);
      }
    }
  }
}

void handle_client(SOCKET client) {
  char buffer[MAX_REQ] = {0};

  os_set_socket_timeout(client, 2);

  int received = recv(client, buffer, sizeof(buffer) - 1, 0);
  if (received > 0) {
    buffer[received] = '\0';

    if (strncmp(buffer, "GET ", 4) != 0) {
      const char *bad_req = "HTTP/1.1 405 Method Not Allowed\r\nConnection: close\r\n\r\nMethod Not Allowed";
      send(client, bad_req, (int)strlen(bad_req), 0);
      closesocket(client);
      return;
    }

    char *path_start = buffer + 4;

    if (strncmp(path_start, "/favicon.ico ", 13) == 0) {
      const char *no_favicon = "HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n";
      send(client, no_favicon, (int)strlen(no_favicon), 0);
      closesocket(client);
      return;
    }

    if (strncmp(path_start, "/ ", 2) != 0 && strncmp(path_start, "/index.html ", 12) != 0) {
      const char *not_found = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\nNot Found";
      send(client, not_found, (int)strlen(not_found), 0);
      closesocket(client);
      return;
    }

    update_cache();

    READ_LOCK();
    int not_modified = 0;
    if (g_cache.etag[0] != '\0') {
      char expected_match[128];
      snprintf(expected_match, sizeof(expected_match), "\r\nIf-None-Match: %s", g_cache.etag);
      not_modified = (strstr(buffer, expected_match) != NULL);
    }

    char header[512];
    if (not_modified) {
      snprintf(header, sizeof(header), "HTTP/1.1 304 Not Modified\r\nETag: %s\r\nConnection: close\r\n\r\n", g_cache.etag);
      send(client, header, (int)strlen(header), 0);
    } else if (g_cache.size > 0) {
      snprintf(header, sizeof(header),
               "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: %zu\r\nETag: %s\r\nConnection: close\r\n\r\n",
               g_cache.size, g_cache.etag);
      send(client, header, (int)strlen(header), 0);
      send(client, g_cache.data, (int)g_cache.size, 0);
    } else {
      const char *not_found = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\nFile index.html not found!";
      send(client, not_found, (int)strlen(not_found), 0);
    }
    READ_UNLOCK();
  }

  closesocket(client);
}

int main() {
  os_net_init();

  RWLOCK_INIT();
  update_cache();

  SOCKET server = socket(AF_INET, SOCK_STREAM, 0);
  if (server == INVALID_SOCKET)
    return 1;

  struct sockaddr_in addr;
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = INADDR_ANY;
  addr.sin_port = htons(PORT);

  if (bind(server, (struct sockaddr *)&addr, sizeof(addr)) == SOCKET_ERROR) {
    printf("Bind failed. Port %d maybe in use?\n", PORT);
    return 1;
  }

  if (listen(server, SOMAXCONN) == SOCKET_ERROR)
    return 1;

  printf("Tiny C Web Server listening on http://localhost:%d\n", PORT);
  printf("Press Ctrl+C to exit.\n");

  while (1) {
    SOCKET client = accept(server, NULL, NULL);
    if (client != INVALID_SOCKET) {
      os_start_client_thread(client);
    }
  }

  RWLOCK_DESTROY();
  closesocket(server);
  os_net_cleanup();
  return 0;
}
