import base64
import io
import itertools
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Sequence

import nbformat
import PIL.Image
from nbformat.notebooknode import NotebookNode
from qrenderer._pandoc.blocks import Meta
from quartodoc.pandoc.blocks import Block, Blocks, BlockContent, Div, Header
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Image, Link

THIS_DIR = Path(__file__).parent
SOURCE_DIR = THIS_DIR.parent / "source"
GALLERY_DIR = SOURCE_DIR / "gallery"
EXAMPLES_DIR = SOURCE_DIR / "reference/examples"

# String in code cell that creates an image that will be in the gallery
GALLERY_TAG = "# Gallery Plot"
THUMBNAILS_DIR = GALLERY_DIR / "thumbnails"
THUMBNAIL_SIZE = (294, 210)

gallery_page = GALLERY_DIR / "index.qmd"
sanitize_patterns = [
    (re.compile(r"[^\w\s]|"), ""),  # keep letters and spaces
    (re.compile(r"\s+"), " "), # remove double spaces
    (re.compile(r"[^\w-]"), "-"), # replace spaces with dashes
]
GALLERY_RE = re.compile(r"^# Gallery, (?P<category>\w+)$", flags=re.MULTILINE)

NOTEBOOK_PATHS = [
    SOURCE_DIR / "reference/examples",
    SOURCE_DIR / "tutorials",
]

# The order here determines order of the sections in
# the gallery
section_names = {
    "points": "Scatter Plots",
    "lines": "Lines and Paths",
    "paths": "Lines and Paths",
    "areas": "Area Plots",
    "bars": "Bar Plots",
    "distributions": "Distributions",
    "tiles": "Tiles",
    "variations": "Variation Plots",
    "maps": "Maps",
    "labels": "Look & Feel",
    "themes": "Look & Feel",
    "elaborate": "Elaborate Graphics",
}


def sanitize_filename(s: str) -> str:
    """
    Clean strings that we make part of filenames
    """
    s = s.lower()
    for pattern, replacement in sanitize_patterns:
        s = pattern.sub(replacement, s)
    return s

@dataclass
class GalleryImage(Block):
    """
    Gallery Image
    """

    # The relative path of thumbnail from the gallery
    thumbnail: Path
    title: str
    target: str
    category: str

    def __str__(self):
        # card, card-header, card-body create bootstrap components
        # https://getbootstrap.com/docs/5.3/components/card/
        #
        # For a responsive layout, use bootstrap grid classes that select
        # for different screen sizes
        # https://getbootstrap.com/docs/5.3/layout/grid/#grid-options
        out_cls = "card g-col-12 g-col-sm-6 g-col-md-3"
        in_cls = "card-header"
        res = Div(
            [
                Div(self.title, Attr(None, in_cls.split())),
                Div(
                    Link(Image(src=self.thumbnail), target=self.target),
                    Attr(None, ["card-body"]),
                ),
            ],
            Attr(None, out_cls.split()),
        )
        return str(res)


def create_thumbnail(output_node: NotebookNode, filepath: Path):
    """
    Create a thumbnail for the gallery

    Parameters
    ----------
    output_node:
        Node containing the output image
    filepath:
        Where to save the created thumbnail on the filesystem
    """
    filepath.parent.mkdir(exist_ok=True, parents=True)
    thumb_size = THUMBNAIL_SIZE[0] * 2, THUMBNAIL_SIZE[1] * 2
    img_str = output_node["data"]["image/png"]
    file = io.BytesIO(base64.decodebytes(img_str.encode()))
    img = PIL.Image.open(file)
    img.thumbnail(thumb_size)
    img.save(filepath)


def get_gallery_image_title(cells: Sequence[NotebookNode]) -> str:
    """
    Return the first level 3 header going backwords
    """
    markdown_lines = itertools.chain(
        *(c.source.splitlines() for c in cells[::-1] if c.cell_type == "markdown")
    )
    header = ""
    for line in markdown_lines:
        if line.startswith("# "):
            header = line.strip("# ")
        if line.startswith("### "):
            return line.strip("# ")

    # raise ValueError("No title found for gallery entry")
    return header


def get_gallery_images_in_notebook(
    nb_filepath: Path,
) -> Generator[GalleryImage, None, None]:
    """
    Return all gallery images in a notebook
    """
    nb = nbformat.read(nb_filepath.open(), as_version=4)
    nb_cells = nb["cells"]
    notebook_name = nb_filepath.stem

    # The preceeding_cells and the output node that contains
    # an image for the gallery
    gallery_output_nodes = (
        (nb_cells[:ii], node, m)
        for ii, cell in enumerate(nb_cells)
        if (m := GALLERY_RE.match(cell.source))
        for node in cell.outputs
        if node.output_type == "display_data"
    )

    # Notebooks in the reference/examples are included in the
    # documentation for the object with the same filename (stem).
    #
    # e.g.
    #    /reference/examples/geom_point.ipynb
    # is included in the documentation for
    #    geom_point
    # at
    #    /reference/geom_point.qmd
    # These gallery images should point to the qmd file

    nb_relpath = nb_filepath.relative_to(SOURCE_DIR)
    target_tpl = (
        f"/reference/{notebook_name}.qmd#{{anchor}}"
        if nb_filepath.is_relative_to(EXAMPLES_DIR)
        else f"/{nb_relpath}#{{anchor}}"
    )

    for preceeding_cells, output_node, m in gallery_output_nodes:
        title = get_gallery_image_title(preceeding_cells)
        anchor = sanitize_filename(title)
        target = target_tpl.format(anchor=anchor)
        thumb_path = THUMBNAILS_DIR / f"{notebook_name}-{anchor}.png"
        rel_thumb_path = thumb_path.relative_to(thumb_path.parent.parent)
        create_thumbnail(output_node, thumb_path)
        category = m.group("category")
        yield GalleryImage(rel_thumb_path, title, target, category)


def get_gallery_images(
    nb_filepaths: Sequence[Path],
) -> Generator[GalleryImage, None, None]:
    """
    Return all gallery images
    """
    for filepath in nb_filepaths:
        try:
            yield from get_gallery_images_in_notebook(filepath)
        except Exception as err:
            raise Exception(f"Could not process {filepath}") from err


def render_gallery_items() -> BlockContent:
    """
    Rendert the items in the gallery
    """
    notebooks = sorted(
        fp
        for dir_path in NOTEBOOK_PATHS
        for fp in dir_path.glob("*.ipynb")
        if not fp.name.endswith(".out.ipynb")
    )

    # Get the images for each section
    # We intentionally inherit the order of the section_names
    section_images: dict[str, list[GalleryImage]] = {
        title: [] for title in section_names.values()
    }

    for img in get_gallery_images(notebooks):
        try:
            section_title = section_names[img.category]
        except KeyError as err:
            msg = f"Unknown gallery tag: {img.category}"
            raise ValueError(msg) from err

        section_images[section_title].append(img)

    sections: list[Block] = []
    for section_title, imgs in section_images.items():
        if not imgs:
            continue

        sections.extend(
            [
                Header(2, section_title, Attr(classes=["gallery"])),
                Div(imgs, Attr(classes=["grid"])),
            ]
        )

    return Blocks(sections)


def render_gallery_page() -> BlockContent:
    """
    Render the gallery page
    """
    return Blocks(
        [
            Meta({"title": "Gallery"}),
            render_gallery_items(),
        ]
    )


def create_gallery():
    """
    Create gallery qmd file
    """
    content = str(render_gallery_page())
    gallery_page.write_text(content)


if __name__ == "__main__":
    create_gallery()
