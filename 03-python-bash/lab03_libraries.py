#!/usr/bin/env python3
"""Lab 03: the os, subprocess and requests libraries."""

import os
import subprocess
import time

import requests

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
COMMAND_TIMEOUT = 5
REQUEST_TIMEOUT = 3

SERVICES = ["nginx", "no-such-service"]
TARGETS = [
    "http://localhost",
    "http://localhost/no-existe",
    "http://localhost:8080",
]


def show_os_info():
    """Part 1: read the environment and list a folder with os."""
    print("== Part 1: os ==")
    print(f"Shell: {os.getenv('SHELL', 'unknown')}")
    print(f"Language: {os.getenv('LANG', 'unknown')}")
    print(f"CPU cores: {os.cpu_count()}")
    print(f"Lab folder: {os.path.basename(LAB_DIR)}")

    lab02 = os.path.join(LAB_DIR, "lab02_service_check.py")
    print(f"Lab 02 script exists: {os.path.exists(lab02)}")

    print("Files:")
    for entry in sorted(os.scandir(LAB_DIR), key=lambda item: item.name):
        if entry.name.startswith("__"):
            continue
        if entry.is_file():
            print(f"  {entry.name:<28} {entry.stat().st_size:>6} bytes")
        else:
            print(f"  {entry.name}/")


def run_command(command):
    """Run a command (a list) and return (exit_code, output)."""
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=COMMAND_TIMEOUT
        )
    except FileNotFoundError:
        return None, f"command not found: {command[0]}"
    except subprocess.TimeoutExpired:
        return None, "timeout"
    return result.returncode, result.stdout.strip()


def show_subprocess_info():
    """Part 2: run system commands and capture their output."""
    print()
    print("== Part 2: subprocess ==")
    for service in SERVICES:
        code, output = run_command(["systemctl", "is-active", service])
        print(f"{service}: {output} (exit code {code})")

    code, output = run_command(["df", "-h", "/"])
    print(f"df -h / (exit code {code}):")
    print(output)

    code, output = run_command(["no-such-command"])
    print(f"no-such-command: {output} (exit code {code})")


def check_with_requests(url):
    """Return (status, detail, elapsed_ms) for one URL using requests."""
    start = time.monotonic()
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        status = "UP"
        detail = f"HTTP {response.status_code}"
    except requests.exceptions.HTTPError as error:
        # raise_for_status() turns 4xx and 5xx into an exception.
        status = "WARNING"
        detail = f"HTTP {error.response.status_code}"
    except requests.exceptions.Timeout:
        # Must come before ConnectionError: a connect timeout is both.
        status = "DOWN"
        detail = "timeout"
    except requests.exceptions.ConnectionError:
        status = "DOWN"
        detail = "connection refused or unreachable"
    except requests.exceptions.RequestException as error:
        status = "DOWN"
        detail = f"request error: {type(error).__name__}"
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return status, detail, elapsed_ms


def show_requests_info():
    """Part 3: query web services with requests."""
    print()
    print(f"== Part 3: requests {requests.__version__} ==")
    for url in TARGETS:
        status, detail, elapsed_ms = check_with_requests(url)
        print(f"{status:<7} | {url} | {detail} | {elapsed_ms} ms")


def main():
    show_os_info()
    show_subprocess_info()
    show_requests_info()


if __name__ == "__main__":
    main()