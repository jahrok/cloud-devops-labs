#!/usr/bin/env bash
# Lab 04: health check with functions, arguments and exit codes.

LOG_FILE="$HOME/logs/health_check.log"
DEFAULT_THRESHOLD=80

usage() {
    cat <<EOF
Usage: $(basename "$0") [-h] [-t PERCENT] SERVICE [SERVICE...]

Checks systemd services and root disk usage, and logs the results.

Options:
  -h          Show this help and exit.
  -t PERCENT  Disk usage threshold, 1 to 100 (default: ${DEFAULT_THRESHOLD}).

Exit codes:
  0  all checks passed
  1  at least one problem found
  2  invalid usage
EOF
}

log_result() {
    local level="$1"
    local message="$2"
    local line
    line="$(date '+%Y-%m-%d %H:%M:%S') | ${level} | ${message}"
    echo "$line"
    echo "$line" >> "$LOG_FILE"
}

check_service() {
    local service="$1"
    local state
    state="$(systemctl is-active "$service")"
    if [[ "$state" == "active" ]]; then
        log_result "OK" "service ${service} is active"
        return 0
    fi
    log_result "FAIL" "service ${service} is ${state}"
    return 1
}

check_disk() {
    local threshold="$1"
    local used
    used="$(df --output=pcent / | tail -n 1 | tr -dc '0-9')"
    if (( used >= threshold )); then
        log_result "FAIL" "disk / at ${used}% (threshold ${threshold}%)"
        return 1
    fi
    log_result "OK" "disk / at ${used}% (threshold ${threshold}%)"
    return 0
}

main() {
    local threshold="$DEFAULT_THRESHOLD"
    local opt
    while getopts ":ht:" opt; do
        case "$opt" in
            h) usage; exit 0 ;;
            t) threshold="$OPTARG" ;;
            :) echo "Error: option -${OPTARG} needs a value." >&2; usage >&2; exit 2 ;;
            \?) echo "Error: unknown option -${OPTARG}." >&2; usage >&2; exit 2 ;;
        esac
    done
    shift $((OPTIND - 1))

    if [[ $# -lt 1 ]]; then
        echo "Error: give at least one service name." >&2
        usage >&2
        exit 2
    fi
    if ! [[ "$threshold" =~ ^[0-9]+$ ]] || (( 10#$threshold < 1 || 10#$threshold > 100 )); then
        echo "Error: threshold must be a number from 1 to 100." >&2
        exit 2
    fi

    mkdir -p "$(dirname "$LOG_FILE")"

    local problems=0
    local service
    for service in "$@"; do
        check_service "$service" || problems=$((problems + 1))
    done
    check_disk "$threshold" || problems=$((problems + 1))

    if (( problems > 0 )); then
        log_result "SUMMARY" "${problems} problem(s) found"
        exit 1
    fi
    log_result "SUMMARY" "all checks passed"
    exit 0
}

main "$@"