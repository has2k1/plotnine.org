#!/usr/bin/env bash

set -e

# Define the classes to remove
CLASSES_TO_REMOVE="h1,h2,h3,h4,h5,h6,fw-medium,quarto-container,page-columns,page-rows-contents,page-layout-article,page-navbar,content,fullcontent,quarto-light,quarto-title-block"

# Define the IDs to remove
IDS_TO_REMOVE="quarto-content,quarto-document-content,title-block-header"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="${SCRIPT_DIR}/../source/_site"
TEMP_FILE=$(mktemp "/tmp/${ID}_XXXXXX")

# Call the HTML cleaner script with the specified classes and IDs
<"${SITE_DIR}/index.html" uv run "${SCRIPT_DIR}/html_cleaner.py" --classes "${CLASSES_TO_REMOVE}" --ids "${IDS_TO_REMOVE}" >"${TEMP_FILE}"

mv -v "$TEMP_FILE" "${SITE_DIR}/index.html"
