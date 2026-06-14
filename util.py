# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
import os
import shutil
import re
import functools
import requests
from requests.adapters import HTTPAdapter,Retry

"""
create unique filename
base_name: filename without extension (e.g. 'output')
extension: extension without point (e.g. 'html')
"""
def get_unique_filename(debug, folder, base_name, extension):
    if len(base_name) > 100:
        base_name = base_name[0:100]
    filename = f"{base_name}.{extension}"
    filepath = os.path.join(folder, filename)
    if debug:
        print(f"filepath: {filepath}")
    counter = 1
    while os.path.exists(filepath):
        filename = f"{base_name}_{counter}.{extension}"
        filepath = os.path.join(folder, filename)
        if debug:
            print(f"filepath: {filepath}")
        counter += 1
    return filename

# save image, return local filename
def download_image(debug, filename_base_name, image_folderpath, image_folder_name_only, img_url):

    # remove markdown syntax, if markdown detected
    if img_url.startswith("![](<") or img_url.startswith("[![](<")  or img_url.startswith("[]"):
        _, _, img_url = img_url.partition(')')
        img_url, _, _ = img_url.partition(')')
        #if debug:
        #print(f"neue url: {img_url}")

    img_url = img_url.split("?")[0].replace("<", "").replace(">", "")

    suffix = os.path.splitext(img_url)[1][1:]
    if not suffix:
        return ""

    suffix = re.sub(r'[^a-zA-Z0-9áéíóàèìòîâûêäöüÄÖÜß\s]', "-", suffix)

    if debug:
        print(f"suffix: {suffix}")
        print(f"imageFolderPath: {image_folderpath}")

    img_url = requests.utils.quote(img_url, safe=":/")

    os.makedirs(image_folderpath, exist_ok=True)
    filename = get_unique_filename(debug, image_folderpath, filename_base_name, suffix)
    filepath = os.path.join(image_folderpath, filename)
    filepath_relativ = os.path.join(image_folder_name_only, filename)
    if debug:
        print(f"Image filepath: {filepath}")
        print(f"filepath relativ: {filepath_relativ}")
    try:
        img_data = requests.get(img_url, timeout=30)
        img_data.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(img_data.content)
        if debug:
            print(f"image saved: {filepath}")
    except Exception as e:
        print(f"error load image {img_url}: {e}")

    return filepath_relativ

def save(foldername, filename, node, html, html_site_override):
    if not node:
        return
    if not filename:
        return
    if not foldername:
        return
    if not html:
        return
    filepath = os.path.join(foldername, filename)
    file_exists = os.path.exists(filepath)
    if not file_exists or html_site_override:
        if file_exists:
            print(f"Info: File exists! File were overrided!!! {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            for htmltext in html:
                if htmltext:
                    f.write(htmltext)
    else:
        print(f"File can not saved, because filename exists! {filepath}")

def copy_css(debug, foldername):
    source = "style.css"
    dest = os.path.join(foldername, "style.css")
    if debug:
        print(f"Source: {source}")
        print(f"Dest: {dest}")
    shutil.copy(source, dest)
