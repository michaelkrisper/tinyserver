# Tiny C Web Server - Makefile

CC ?= gcc
CFLAGS = -O3 -Wall -Wextra -pthread
LDFLAGS = -lpthread
TARGET = server

.PHONY: all clean bench test

all: $(TARGET)

$(TARGET): server.c
	@echo "Compiling $(TARGET) with $(CC)..."
	$(CC) $(CFLAGS) -o $(TARGET) server.c $(LDFLAGS)
	@echo "Successfully built $(TARGET)!"

clean:
	@echo "Cleaning up build artifacts..."
	rm -f $(TARGET)
	@echo "Clean complete."

bench:
	@echo "Running Benchmark Suite..."
	python3 tests/bench.py

test:
	@echo "Running ETag Cache Tests..."
	python3 tests/test.py
