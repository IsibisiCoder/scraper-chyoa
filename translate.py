"""Translate helper module."""

import os
import ollama
from openai import OpenAI
import shutil
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup

from config import Llm_system


def translate_text(config, content: str, target_language: str = "de") -> str:
    """Translate text into the target language using a public translation endpoint."""
    if not content or not content.strip():
        return content

    llm = config.llm_system
    question = config.llm_question.replace("{LANGUAGE}", config.translate_language)
    question = f"{question}: {content}"

    # uncensored:
    # dolphin-llama3, dolphin-mistral-nemo, dolphin3, llama2-uncensored
    # https://erichartford.com/uncensored-models
    #
    # dolphin3                      => einige Texte und Wörter mal nicht übersetzt, mal ja
    # wizardlm-uncensored           => ungeeignet, konnte Texte / Überschriften nicht übersetzen
    # wizard-vicuna-uncensored:30b  => stehengeblieben
    # llama2-uncensored:7b          => nichts wurde übersetzt, fragen wie what next werden mit weiss ich doch nicht übersetzt
    # hf.co/cognitivecomputations/Dolphin3.0-Llama3.1-8B-GGUF:Q4_0 => bisher okay
    # GFalcon-UA/dolphin3-llama3.1

    #ollama run CognitiveComputations/dolphin-llama3.1:8b-v2.9.4
    #
    # no
    # gemma4:12b-mlx
    #
    # Für hochwertige Ergebnisse eignen sich mittelgroße, mehrsprachig trainierte Modelle (wie Qwen mit 7B/8B oder größer) meist am besten.

    system_prompt = (
        "Du bist ein präzises Übersetzungs-Tool. Übersetze die User-Nachricht in das Deutsche.\n"
        "Halte dich strikt an diese drei Regeln:\n"
        "1. Antworte AUSSCHLIESSLICH mit dem direkt übersetzten Text incl. der enthaltenen Html-Tags.\n"
        "2. Füge KEINE Einleitungen, Erklärungen, Kommentare oder Labels hinzu.\n"
        "3. Wenn der Text unklar ist oder du ihn nicht übersetzen kannst, "
        "antworte mit einem absolut leeren Text (leerer String)."
    )

#    messages = [
#        {"role": "user", "content": question},
#        {"role": "system", "content": "Code-Assistent."},
#    ]

    if llm == Llm_system.OLLAMA:
        response = ollama.chat(
            model=config.llm_model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': content}
            ],
            options={
                'temperature': 0.0  # Verhindert kreative Abweichungen
            }
        )
        translation_content = response['message']['content'].strip()
        print(f"orig:      {content[0:30]}")
        print(f"translate: {translation_content[0:30]}\n")
        # --- Python-Filter als Sicherheitsnetz ---
        # Wenn das Modell trotz Verbot versucht, sich zu entschuldigen,
        # leeren wir den Text manuell.
        verbotene_woerter = ["sorry", "entschuldigung", "ich kann", "bitte geben", "unverständlich"]
        if any(wort in translation_content.lower() for wort in verbotene_woerter):
            print(f"ai can not translate the text: {translation_content[0:300]}")
            return ""

    if llm == Llm_system.LMSTUDIO:
        # Verbindet sich mit dem lokalen LM-Studio-Server
        #client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
        client = OpenAI(base_url=config.llm_api, api_key="not-needed")

        response = client.chat.completions.create(
            model=config.llm_model,  # Name des in LM Studio geladenen Modells
            messages=[{"role": "user", "content": question}],
        )
        #print(response.choices[0].message.content)
        translation_content = response.choices[0].message.content
        print(f"content:{translation_content}")
    return translation_content
    #payload = {
    #    "q": content,
    #    "source": "auto",
    #    "target": target_language,
    #    "format": "text",
    #}

    #try:
    #    response = requests.post(
    #        "https://libretranslate.de/translate",
    #        json=payload,
    #        timeout=30,
    #    )
    #    response.raise_for_status()
    #    data = response.json()
    #    return data.get("translatedText", content)
    #except requests.RequestException as exc:
    #    print(f"translate: translation request failed: {exc}")
    #    return content
    #except ValueError as exc:
    #    print(f"translate: invalid JSON response: {exc}")
    #    return content


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
