"""
This script is run by the Makefile before quarto_build
"""
import hashlib
import shutil
from importlib.resources import files as _files
from pathlib import Path

ROOT_DIR = Path(__file__).parent
EXAMPLES_DIR = ROOT_DIR / "reference/examples"
TUTORIALS_DIR = ROOT_DIR / "tutorials"


def copy_examples_and_tutorials():
    """
    Copy the examples & tutorials in plotnine_examples
    """

    # NOTE: To avoid confusing the watcher used by "quarto preview",
    # we copy only if the original files are different.
    def same_contents(f1, f2):
        h1 = hashlib.sha256(f1.read_bytes()).hexdigest()
        h2 = hashlib.sha256(f2.read_bytes()).hexdigest()
        return h1 == h2

    def copy(src_dir, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        src_files = src_dir.glob("*.ipynb")
        cur_dest_files = dest_dir.glob("*.ipynb")
        new_dest_files = []
        for src in src_files:
            dest = dest_dir / src.name
            new_dest_files.append(dest)
            if dest.exists() and same_contents(src, dest):
                continue
            shutil.copyfile(src, dest)

        # Remove any deleted files
        for dest in set(cur_dest_files).difference(new_dest_files):
            dest.unlink()

    copy(_files("plotnine_examples.examples"), EXAMPLES_DIR)
    copy(_files("plotnine_examples.tutorials"), TUTORIALS_DIR)


if __name__ == "__main__":
    copy_examples_and_tutorials()
