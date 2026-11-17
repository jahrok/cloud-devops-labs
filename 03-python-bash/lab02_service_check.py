#!/usr/bin/env python3
"""Lab 02: check whether services respond and log the results."""

import os
import time
import urllib.error
import urllib.request
from datetime import datetime

LOG_DIR = os.path.expanduser("~/logs")
LOG_FILE = os.path.join(LOG_DIR, "service_check.log")
TIMEOUT_SECONDS = 3
LAST_LINES = 6

TARGETS = [
    "http://localhost",
    "http://localhost/no-existe",
    "http://localhost:8080",
]


def check_service(url, timeout=TIMEOUT_SECONDS):
    """Return (status, detail, elapsed_ms) for one URL."""
    start = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            status = "UP"
            detail = f"HTTP {response.status}"
    except urllib.error.HTTPError as error:
        # The server answered, but with an error code such as 404.
        status = "WARNING"
        detail = f"HTTP {error.code}"
    except urllib.error.URLError as error:
        # No answer at all: connection refused, unreachable, etc.
        status = "DOWN"
        detail = f"connection error: {error.reason}"
    except TimeoutError:
        status = "DOWN"
        detail = "timeout"
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return status, detail, elapsed_ms


def write_log(line):
    """Append one line to the log file. Return True if it worked."""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(line + "\n")
        return True
    except OSError as error:
        print(f"Could not write to the log: {error}")
        return False


def read_last_lines(path, count):
    """Return the last `count` lines of a file, or [] if it does not exist."""
    try:
        with open(path, "r", encoding="utf-8") as log_file:
            return log_file.read().splitlines()[-count:]
    except FileNotFoundError:
        return []


def main():
    print(f"Checking {len(TARGETS)} services...")
    for url in TARGETS:
        status, detail, elapsed_ms = check_service(url)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} | {status:<7} | {url} | {detail} | {elapsed_ms} ms"
        print(line)
        write_log(line)

    print()
    print(f"Last {LAST_LINES} lines of {LOG_FILE}:")
    for line in read_last_lines(LOG_FILE, LAST_LINES):
        print(line)


if __name__ == "__main__":
    main()