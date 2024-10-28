import itertools
from pathlib import Path

import nbformat
from qrenderer._pandoc.blocks import Meta
from quartodoc.pandoc.blocks import BulletList
from quartodoc.pandoc.blocks import Blocks, BlockContent, Div
from quartodoc.pandoc.inlines import Link

THIS_DIR = Path(__file__).parent
SOURCE_DIR = THIS_DIR.parent / "source"
TUTORIALS_DIR = SOURCE_DIR / "tutorials"

tutorials_page = TUTORIALS_DIR / "index.qmd"


def get_tutorial_title(filepath: Path) -> str:
    """
    Lookup the title of the notebook
    """
    # The first h1 header
    nb = nbformat.read(filepath.open(), as_version=4)
    markdown_lines = itertools.chain(
        *(c.source.splitlines() for c in nb.cells if c.cell_type == "markdown")
    )
    for line in markdown_lines:
        if line.startswith("# "):
            return line.strip("# ")
    raise ValueError(f"No title found for tutorial: {filepath.name}")


def render_tutorials_items() -> BlockContent:
    """
    Generate links to the tutorials

    Returns
    -------
    :
        Links to tutorial pages in markdown format.
    """
    notebooks = [p for p in TUTORIALS_DIR.glob("*.ipynb") if p.stem != "index"]
    link_titles_and_paths = [
        (get_tutorial_title(f), f.relative_to(TUTORIALS_DIR)) for f in notebooks
    ]
    links = [Link(t, str(p)) for t, p in link_titles_and_paths]
    return BulletList(links)


def render_tutorials_page() -> BlockContent:
    """
    Render the gallery page
    """
    return Blocks(
        [
            Meta({"title": "Tutorials"}),
            Div(render_tutorials_items()),
        ]
    )


def create_tutorials():
    """
    Create tutorials qmd file
    """
    content = str(render_tutorials_page())
    tutorials_page.write_text(content)


if __name__ == "__main__":
    create_tutorials()
