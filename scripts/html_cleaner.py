#!/usr/bin/env python3
# Dependencies:
# requirements.txt: beautifulsoup4>=4.12.0
"""
HTML Attribute Cleaner

This script reads HTML from stdin, removes specified IDs and class names,
and writes the modified HTML to stdout.

Usage:
    cat input.html | python html_cleaner.py --ids id1,id2 --classes class1,class2
"""

import argparse
import sys
from typing import List, Optional
from bs4 import BeautifulSoup


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Remove specified IDs and class names from HTML."
    )
    parser.add_argument("--ids", type=str, help="Comma-separated list of IDs to remove")
    parser.add_argument(
        "--classes", type=str, help="Comma-separated list of class names to remove"
    )
    return parser.parse_args()


def remove_attributes(
    html_content: str,
    ids_to_remove: Optional[List[str]],
    classes_to_remove: Optional[List[str]],
) -> str:
    """
    Remove specified IDs and class names from HTML content.

    Args:
        html_content: The HTML content to process
        ids_to_remove: List of ID values to remove
        classes_to_remove: List of class names to remove

    Returns:
        Modified HTML content as a string
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Process elements with IDs to remove
    if ids_to_remove:
        for id_value in ids_to_remove:
            elements = soup.find_all(id=id_value)
            for element in elements:
                del element["id"]

    # Process elements with classes to remove
    if classes_to_remove:
        for element in soup.find_all(class_=True):
            current_classes = element.get("class", [])
            # Filter out the classes we want to remove
            new_classes = [
                cls for cls in current_classes if cls not in classes_to_remove
            ]

            if not new_classes:
                # If no classes left, remove the class attribute entirely
                del element["class"]
            else:
                # Otherwise, update with the remaining classes
                element["class"] = new_classes

    return str(soup)


def main() -> None:
    """Main function to process HTML content."""
    args = parse_arguments()

    # Parse comma-separated lists
    ids_to_remove = args.ids.split(",") if args.ids else []
    classes_to_remove = args.classes.split(",") if args.classes else []

    # Read HTML from stdin
    html_content = sys.stdin.read()

    # Process the HTML
    result = remove_attributes(html_content, ids_to_remove, classes_to_remove)

    # Write modified HTML to stdout
    sys.stdout.write(result)


if __name__ == "__main__":
    main()
