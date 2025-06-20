"""
This script is run by the Makefile before quarto_build
"""
import hashlib
import shutil
from pathlib import Path

THIS_DIR = Path(__file__).parent
ROOT_DIR = THIS_DIR.parent
SOURCE_DIR = ROOT_DIR / "source"
PLOTNINE_DIR = ROOT_DIR / "source"

# list of (source, destination) folders
NOTEBOOK_PATHS = [
    # The examples are built together with the plotnine api/reference
    # docs. So they have to be copied into the submodule.
    (
        ROOT_DIR / "plotnine-examples/plotnine_examples/examples",
        ROOT_DIR / "plotnine/doc/reference/examples",
    ),
    # # The tutorials are built as part of the wider website.
    # (
    #     ROOT_DIR / "plotnine-examples/plotnine_examples/tutorials",
    #     SOURCE_DIR / "tutorials",
    # ),
]


def copy_notebooks():
    """
    Copy the notebooks in plotnine_examples
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

    for src, dest in NOTEBOOK_PATHS:
        copy(src, dest)


if __name__ == "__main__":
    copy_notebooks()
