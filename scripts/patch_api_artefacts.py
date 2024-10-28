# Patch api stuff to correct anything that cannot weight for the
# next release
# This file should be cleaned up after a release when the patches
# are not required
from pathlib import Path

SOURCE_DIR = Path(__file__).parent.parent / "source"

def cleanup_v0_14_0_changelog():
    """
    Remove (not-yet-released)
    """
    file = SOURCE_DIR / "changelog.qmd"
    contents = (
        file
        .read_text()
        .replace(
            "## v0.14.0\n(2024-10-28)\n\n(not-yet-released)",
            "## v0.14.0\n(2024-10-28)\n"
        )
    )
    file.write_text(contents)


if __name__ == "__main__":
    cleanup_v0_14_0_changelog()
