#!/usr/bin/env python3
"""Lab 01: Python basics applied to system administration."""

import platform
import shutil
import socket

WARNING_LEVEL = 75
CRITICAL_LEVEL = 90


def get_hostname():
    return socket.gethostname()


def disk_usage_percent(path):
    total, used, _free = shutil.disk_usage(path)
    return round(used / total * 100, 1)


def classify(percent):
    if percent >= CRITICAL_LEVEL:
        return "CRITICAL"
    if percent >= WARNING_LEVEL:
        return "WARNING"
    return "OK"


def main():
    print(f"Host:   {get_hostname()}")
    print(f"OS:     {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("Disk usage:")
    for path in ["/", "/var", "/tmp"]:
        percent = disk_usage_percent(path)
        print(f"  {path:<6} {percent:>5}%  [{classify(percent)}]")


if __name__ == "__main__":
    main()