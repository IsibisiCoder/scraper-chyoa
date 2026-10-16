"""Combine downloaded chapter pages into one linked HTML story."""

import argparse
import re
import chyoa
from pathlib import Path
from typing import Any, Literal

CHAPTER_FILE_PATTERN = re.compile(r"^(\d{4})[-_].+\.html$", re.IGNORECASE)

def _tag_text(markup):
    return re.sub(r"<[^>]*>", "", markup).strip()


def _escape_text(text):
    text = re.sub(r"&(?!#?\w+;)", "&amp;", text)
    return text.replace("<", "&lt;").replace(">", "&gt;")


def _chapter_details(path):
    source = path.read_text(encoding="utf-8")
    heading = re.search(
        r"<p\b[^>]*class=[\"'][^\"']*\bstoryheader2\b[^\"']*[\"'][^>]*>(.*?)</p>",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    opening_tag = re.search(
        r"<p\b[^>]*class=[\"'][^\"']*\bstoryheader2\b[^\"']*[\"'][^>]*>",
        source,
        re.IGNORECASE,
    )
    chapter_id = ""
    if opening_tag:
        id_attribute = re.search(
            r"\bid\s*=\s*(?:\"([^\"]+)\"|'([^']+)'|([^\s>]+))",
            opening_tag.group(),
            re.IGNORECASE,
        )
        if id_attribute:
            chapter_id = next(value for value in id_attribute.groups() if value)

    chapter_header = re.search(
        r"<div\b[^>]*class=[\"'][^\"']*\bchapterheader\b[^\"']*[\"'][^>]*>(.*?)</div>",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    chapter_number = _tag_text(chapter_header.group(1)) if chapter_header else ""
    chapter_number = re.sub(r"\s+by\b.*$", "", chapter_number).strip()

    secondary_heading = re.search(
        r"<div\b[^>]*class=[\"'][^\"']*\bstoryheader1\b[^\"']*[\"'][^>]*>(.*?)</div>",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    title = _tag_text(secondary_heading.group(1)) if secondary_heading else ""
    if not title and heading:
        title = _tag_text(heading.group(1))
    if chapter_number and title:
        toc_title = f"{chapter_number} - {title}"
    else:
        toc_title = title or chapter_number or path.stem

    story_heading = re.search(
        r"<h1\b[^>]*class=[\"'][^\"']*\bstorytitle\b[^\"']*[\"'][^>]*>(.*?)</h1>",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    story_title = _tag_text(story_heading.group(1)) if story_heading else ""

    body_start = re.search(r"<aside\b", source, re.IGNORECASE)
    if not body_start:
        body_start = re.search(r"<body\b[^>]*>", source, re.IGNORECASE)
    body_end = re.search(r"</body\s*>", source, re.IGNORECASE)
    if not body_start or not body_end or body_end.start() <= body_start.start():
        raise ValueError(f"Cannot find chapter content in {path.name}")
    content = source[body_start.start():body_end.start()]

    return chapter_id, toc_title, story_title, content


def _link_chapters(content, filename_to_id):
    return re.sub(r"""href=(["'])(.*?)\1""",
                  lambda match: _replace_link_href(match, filename_to_id),
                  content, flags=re.IGNORECASE)


def _replace_link_href(match, filename_to_id):
    quote = match.group(1)
    url = match.group(2)
    filename = url.removeprefix("./")
    if filename in filename_to_id:
        return f"href={quote}#{filename_to_id[filename]}{quote}"
    if filename.lower().endswith("-map.html"):
        return f"href={quote}#toc{quote}"
    return match.group(0)


def generate_total_html(directory, output_file=None):
    """Combine chapter files in *directory* and return the output path."""
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    output_file = determine_output_filepath(directory, output_file)

    chapter_files, chapters, filename_to_id = read_html_files(directory)
    if output_file.resolve() in {path.resolve() for path in chapter_files}:
        raise ValueError("The output file must not replace a chapter HTML file")

    story_title = next((chapter[2] for chapter in chapters if chapter[2]), directory.name)
    htmltext = []
    htmltext = chyoa.create_html_head(config, htmltext, node, multiple_pages, first_page)
    htmltext = chyoa.create_javascript(htmltext)

    html = [
        "<!DOCTYPE html>",
        '<html><head><meta charset="utf-8">',
        f"<title>{_escape_text(story_title)}</title>",
        '<link rel="stylesheet" href="style.css">',
        "</head><body>",
        f'<h1 class="storytitle">{_escape_text(story_title)}</h1>',
        '<nav id="toc"><h2>Table of Contents</h2><ol>',
    ]
    for chapter_id, title, _, _ in chapters:
        if chapter_id:
            html.append(
                f'<li><a href="#{chapter_id}">{_escape_text(title)}</a></li>'
            )
    html.extend(["</ol></nav>", "<hr>"])
    html.extend(_link_chapters(chapter[3], filename_to_id) for chapter in chapters)
    html.append("</body></html>")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(html), encoding="utf-8")
    return output_file


def determine_output_filepath(
        directory: list[tuple[Literal[""] | str | Any, str | Literal[""] | Any, str | Literal[""], Any]],
        output_file) -> Any:
    if output_file is None:
        map_files = sorted(directory.glob("*-map.html"))
        output_file = (
            map_files[0].with_name(map_files[0].name.removesuffix("-map.html") + "-total.html")
            if map_files
            else directory / f"{directory.name}-total.html"
        )
    else:
        output_file = Path(output_file)
    return output_file


def read_html_files(directory) -> tuple[
    Path, list[Path], list[tuple[Literal[""] | str | Any, str | Literal[""] | Any, str | Literal[""], Any]], dict[
        str, str | Any]]:

    chapter_files = sorted(
        (path for path in directory.iterdir()
         if path.is_file() and CHAPTER_FILE_PATTERN.match(path.name)),
        key=lambda path: (int(CHAPTER_FILE_PATTERN.match(path.name).group(1)), path.name.lower()),
    )
    if not chapter_files:
        raise ValueError(f"No numbered chapter HTML files found in {directory}")

    chapters = [_chapter_details(path) for path in chapter_files]
    filename_to_id = {
        path.name: chapter[0]
        for path, chapter in zip(chapter_files, chapters)
        if chapter[0]
    }
    return chapter_files, chapters, filename_to_id


def main():
    print("do not use the script")
    return
    parser = argparse.ArgumentParser(
        description="Combine numbered chapter HTML files into one story file."
    )
    parser.add_argument("directory", type=Path, help="Directory containing chapter HTML files")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output HTML path (defaults to the story's *-total.html filename in the directory)",
    )
    args = parser.parse_args()
    try:
        output_file = generate_total_html(args.directory, args.output)
    except ValueError as error:
        parser.error(str(error))
    print(f"Created: {output_file}")


if __name__ == "__main__":
    main()
