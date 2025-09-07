#!/bin/bash
# log_parser.sh
# Usage: ./log_parser.sh logfile.log

if [ $# -ne 1 ]; then
  echo "Usage: $0 logfile.log"
  exit 1
fi

LOGFILE="$1"

if [ ! -s "$LOGFILE" ]; then
  echo "Log file is empty. Nothing to summarize."
  exit 0
fi

echo "===== Log Summary ====="

# Count total lines
total_lines=$(wc -l < "$LOGFILE")
echo "Total lines: $total_lines"

# Count errors
errors=$(grep -c "ERROR" "$LOGFILE")
echo "Errors: $errors"

# Top 5 IPs
echo "Top 5 IPs:"
grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' "$LOGFILE" \
  | sort \
  | uniq -c \
  | sort -nr \
  | head -5 \
  | awk '{print "  "$2" - "$1" times"}'

echo "======================="
