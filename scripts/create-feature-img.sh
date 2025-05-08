#!/usr/bin/env bash

# This script is used by ./generate-homepage-items.sh

# Check if an argument (ID) was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <ID>"
  exit 1
fi

ID=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOMEPAGE_DIR="${SCRIPT_DIR}/../source/homepage"

# Create a temporary file with the given ID
temp_file=$(mktemp "/tmp/${ID}_XXXXXX")

cat "$SCRIPT_DIR/img-start.py" > "${temp_file}"

echo -n "plot = " >> "${temp_file}"
sed -e 's/!!!//g;s/???//g;/#skip/d' < "${HOMEPAGE_DIR}/features/code/${ID}.py" >> "${temp_file}"
echo -e "\n\nplot.save('$HOMEPAGE_DIR/features/img/$ID.png')" >> "${temp_file}"

cat "${temp_file}"
python "${temp_file}"
