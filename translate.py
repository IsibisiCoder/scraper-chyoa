"""Translate helper module."""

import os
import shutil
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup


def translate_text(config, content: str, target_language: str = "de") -> str:
    """Translate text into the target language using a public translation endpoint."""
    if not content or not content.strip():
        return content

    payload = {
        "q": contentcontent,
        "source": "auto",
        "target": target_language,
        "format": "text",
    }

    try:
        response = requests.post(
            "https://libretranslate.de/translate",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("translatedText", text)
    except requests.RequestException as exc:
        print(f"translate: translation request failed: {exc}")
        return text
    except ValueError as exc:
        print(f"translate: invalid JSON response: {exc}")
        return text


def handle_html_file(file_path: str) -> None:
    """Handle an individual HTML file.

    This function translates the contents of storyheader1, storyheader2 and chapter-content.
    """
    if not os.path.isfile(file_path):
        print(f"translate: file not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    soup = BeautifulSoup(content, "html.parser")
    translated_any = False

    for class_name in ["storyheader1", "storyheader2", "chapter-content"]:
        target_div = soup.find("div", class_=class_name)
        if target_div is None:
            print(f"translate: missing <div class=\"{class_name}\"> in {file_path}")
            continue

        original_text = target_div.get_text(separator="\n", strip=True)
        if not original_text:
            continue

        translated_text = translate_text(original_text)
        if translated_text == original_text:
            print(f"translate: no translation change for class {class_name} in {file_path}")
        else:
            print(f"translate: translated class {class_name} in {file_path}")

        target_div.clear()
        target_div.append(translated_text)
        translated_any = True

    if translated_any:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))
        print(f"translate: saved translated file {file_path}")
    else:
        print(f"translate: nothing translated in {file_path}")


def copy_translate_folder(source: str) -> str:
    """Copy a source folder to a new folder with '-translate' appended."""
    parent = os.path.dirname(source)
    name = os.path.basename(source)
    destination = os.path.join(parent, f"{name}-translate")

    if os.path.isdir(destination):
        print(f"translate: using existing copy: {destination}")
        return destination

    try:
        shutil.copytree(source, destination)
        print(f"translate: copied folder to {destination}")
    except Exception as exc:
        print(f"translate: could not copy '{source}' to '{destination}': {exc}")
        raise

    return destination


def translate_paths(config: Dict[str, Any]) -> None:
    """Walk through folders listed under the translate key in config."""
    paths = config.get("translate")
    if not paths:
        return

    if not isinstance(paths, list):
        print("config: 'translate' must be a list of folder paths")
        return

    for path in paths:
        if not isinstance(path, str):
            print(f"config: invalid translate entry (not a string): {path}")
            continue

        source_folder = os.path.expanduser(path)

        if not os.path.isdir(source_folder):
            print(f"translate: folder not found: {source_folder}")
            continue

        try:
            target_folder = copy_translate_folder(source_folder)
        except OSError as exc:
            print(f"translate: could not copy folder: {exc}")
            continue

        for root, _, files in os.walk(target_folder):
            for filename in files:
                if filename.lower().endswith(".html"):
                    html_file = os.path.join(root, filename)
                    handle_html_file(html_file)
