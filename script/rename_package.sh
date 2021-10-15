#!/usr/bin/env bash
if [ -z "$1" ]
  then
    echo "Usage: rename_package.sh new_name"
    echo "Will rename the package to \"new_name\""
    exit 1
fi
# cleanup first
./scripts/cleanup.sh
# change working directory to project root
cd "$(dirname "$0")/.." || exit
# run rename script
python3 scripts/rename_package.py "$1"
