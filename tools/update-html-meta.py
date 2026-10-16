"""Update chapter, map and total HTML personal metadata from its personal settings JSON file. created by github copilot """

import argparse
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape
from xml.sax.saxutils import unescape as xml_unescape

PERSONAL_TAGS_SUFFIX = "_mytags.json"
CHAPTER_PREFIX = re.compile(r"^\d{4}[-_]")
STORY_FOLDER = re.compile(r"^(.+?)_\(\d+\)_\(\d{4}-\d{2}-\d{2}\)")
PERSONAL_TAGS_DIV = re.compile(
    r"<div\b(?=[^>]*\sclass\s*=\s*(['\"])[^'\"]*\bpersonal-tags\b[^'\"]*\1)"
    r"[^>]*>.*?</div\s*>",
    re.IGNORECASE | re.DOTALL,
)
META_TAG = re.compile(r"<meta\b[^>]*>", re.IGNORECASE)
META_NAME = re.compile(
    r"(?:^|\s)name\s*=\s*(?:([\"'])(.*?)\1|([^\s/>]+))",
    re.IGNORECASE | re.DOTALL,
)
PERSONAL_TAG_LABEL = re.compile(r"<b\b[^>]*>(.*?)</b\s*>\s*:", re.IGNORECASE | re.DOTALL)
FORMATTING_TAG = re.compile(r"</?(?:br|b|i|u)\b[^>]*>", re.IGNORECASE)
HTML_ENTITIES = {"quot": '"', "apos": "'", "nbsp": "\xa0"}
HTML_ATTRIBUTE_ENTITIES = {'"': "&quot;", "'": "&#x27;"}


def _settings_file(html_path, settings_dir):
    folder_match = STORY_FOLDER.match(html_path.parent.name)
    names = []
    if folder_match:
        names.append(folder_match.group(1))

    chapter_name = CHAPTER_PREFIX.sub("", html_path.stem, count=1)
    names.append(chapter_name)

    for name in dict.fromkeys(names):
        candidate = settings_dir / f"{name}{PERSONAL_TAGS_SUFFIX}"
        if candidate.is_file():
            return candidate

    expected = ", ".join(f"{name}{PERSONAL_TAGS_SUFFIX}" for name in dict.fromkeys(names))
    raise FileNotFoundError(
        f"No personal settings JSON found in {settings_dir} (tried: {expected})"
    )


def _read_personal_tags(settings_path):
    with settings_path.open("r", encoding="utf-8-sig") as settings_file:
        settings = json.load(settings_file)

    if not isinstance(settings, dict):
        raise ValueError(f"The settings file {settings_path} must contain a JSON object")
    tags = settings.get("personal_tags", {})
    if not isinstance(tags, dict):
        raise ValueError(f"'personal_tags' in {settings_path} must be a JSON object")
    if not all(isinstance(key, str) for key in tags):
        raise ValueError(f"All personal tag names in {settings_path} must be strings")
    if not all(isinstance(value, str) for value in tags.values()):
        raise ValueError(f"All personal tag values in {settings_path} must be strings")
    return tags


def _render_personal_tags(tags):
    entries = []
    for key, value in tags.items():
        if not value:
            continue
        entries.append(f"| <b>{xml_escape(key)}</b>: {value} ")
    if not entries:
        return ""
    return '<div class="personal-tags">' + "".join(entries) + "</div>"


def _render_meta_tag(key, value):
    plain_value = FORMATTING_TAG.sub("", str(value))
    return (
        f'<meta name="{xml_escape(key, HTML_ATTRIBUTE_ENTITIES)}" '
        f'content="{xml_escape(plain_value, HTML_ATTRIBUTE_ENTITIES)}">'
    )


def _update_meta_tags(source, tags, old_tag_names):
    targets = {name.casefold() for name in old_tag_names}
    targets.update(name.casefold() for name in tags)
    rendered = {
        name.casefold(): _render_meta_tag(name, value)
        for name, value in tags.items()
        if value
    }
    found = set()

    def replace_meta(match):
        name_match = META_NAME.search(match.group())
        if not name_match:
            return match.group()
        name = name_match.group(2) or name_match.group(3)
        normalized_name = xml_unescape(name, HTML_ENTITIES).casefold()
        if normalized_name not in targets:
            return match.group()
        if normalized_name in found or normalized_name not in rendered:
            return ""
        found.add(normalized_name)
        return rendered[normalized_name]

    source = META_TAG.sub(replace_meta, source)
    missing = [tag for name, tag in rendered.items() if name not in found]
    if missing:
        head_end = re.search(r"</head\s*>", source, re.IGNORECASE)
        if not head_end:
            raise ValueError("The HTML file does not contain a closing </head> tag")
        source = (
            source[:head_end.start()]
            + "\n"
            + "\n".join(missing)
            + "\n"
            + source[head_end.start():]
        )
    return source


def update_html(html_path, settings_dir):
    source_bytes = html_path.read_bytes()
    has_bom = source_bytes.startswith(b"\xef\xbb\xbf")
    source = source_bytes.decode("utf-8-sig")
    settings_path = _settings_file(html_path, settings_dir)
    tags = _read_personal_tags(settings_path)

    old_div_match = PERSONAL_TAGS_DIV.search(source)
    old_tag_names = []
    if old_div_match:
        old_tag_names = [
            xml_unescape(re.sub(r"<[^>]*>", "", label), HTML_ENTITIES).strip()
            for label in PERSONAL_TAG_LABEL.findall(old_div_match.group())
        ]

    source = _update_meta_tags(source, tags, old_tag_names)
    replacement_div = _render_personal_tags(tags)
    old_div_match = PERSONAL_TAGS_DIV.search(source)
    if old_div_match:
        source = (
            source[:old_div_match.start()]
            + replacement_div
            + source[old_div_match.end():]
        )
    elif replacement_div:
        closing_tag = re.search(r"</aside\s*>", source, re.IGNORECASE)
        if not closing_tag:
            closing_tag = re.search(r"</body\s*>", source, re.IGNORECASE)
        if not closing_tag:
            raise ValueError("The HTML file does not contain a closing </body> tag")
        source = source[:closing_tag.start()] + replacement_div + source[closing_tag.start():]

    encoding = "utf-8-sig" if has_bom else "utf-8"
    with html_path.open("w", encoding=encoding, newline="") as html_file:
        html_file.write(source)


def _related_html_files(html_path):
    folder_match = STORY_FOLDER.match(html_path.parent.name)
    if folder_match:
        story_name = folder_match.group(1)
    else:
        story_name = CHAPTER_PREFIX.sub("", html_path.stem, count=1)
        story_name = re.sub(r"-(?:map|total|totla)$", "", story_name, flags=re.IGNORECASE)

    related_files = [html_path]
    for suffix in ("map", "total", "totla"):
        related_path = html_path.with_name(f"{story_name}-{suffix}.html")
        if related_path.is_file() and related_path not in related_files:
            related_files.append(related_path)
    return related_files


def main():
    parser = argparse.ArgumentParser(
        description="Update personal metadata in a chapter HTML file and in the *map- and *total HTML files."
    )
    parser.add_argument("html_file", type=Path, help="HTML file to update")
    parser.add_argument(
        "--settings-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "personal_settings",
        help="directory containing *_mytags.json files",
    )
    args = parser.parse_args()
    html_path = args.html_file
    if not html_path.is_absolute() and not html_path.is_file():
        script_relative_path = Path(__file__).resolve().parent / html_path
        if script_relative_path.is_file():
            html_path = script_relative_path
    if not html_path.is_file():
        parser.error(f"HTML file not found: {html_path}")

    try:
        for related_path in _related_html_files(html_path):
            update_html(related_path, args.settings_dir)
            print(f"Updated HTML metadata in {related_path}")
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
