#!/bin/bash
# Usage: ./log_parser.sh logfile.log

if [ $# -ne 1 ]; then
    echo "Usage: $0 logfile.log"
    exit 1
fi

grep "ERROR" "$1" | sort -k1,1
