import os
import shutil
import re
import requests

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
def download_image(debug, filename_base_name, imageFolderPath, imageFolderNameOnly, img_url):
    suffix = os.path.splitext(img_url)[1][1:]
    if not suffix:
        return ""
    
    # split and remove string after ? (e.g. img.png?12345 -> img.png)
    if "?" in suffix:
        suffix = suffix.split("?")[0]
    suffix = re.sub(r'[^a-zA-Z0-9áéíóàèìòîâûêäöüÄÖÜß\s]', "-", suffix)
    if debug:
        print(f"suffix: {suffix}")
        print(f"img_url: {img_url}")

    os.makedirs(imageFolderPath, exist_ok=True)
    filename = get_unique_filename(debug, imageFolderPath, filename_base_name, suffix)
    filepath = os.path.join(imageFolderPath, filename)
    filepathRelativ = os.path.join(imageFolderNameOnly, filename)
    if debug:
        print(f"Image filepath: {filepath}")
    try:
        img_data = requests.get(img_url)
        img_data.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(img_data.content)
        if debug:
            print(f"image saved: {filepath}")
    except Exception as e:
        print(f"error load image {img_url}: {e}")
    return filepathRelativ

def save(debug, foldername, filename, node, html, htmlSiteOverride):
    if not node:
        return
    if not filename:
        return
    if not foldername:
        return
    if not html:
        return
    filepath = os.path.join(foldername, filename)
    fileExists = os.path.exists(filepath)
    if not fileExists or htmlSiteOverride == True:
        if fileExists:
            print(f"Info: File exists! File were overrided!!! {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            for htmltext in html:
                f.write(htmltext)
    else:
        print(f"File can not saved, because filename exists! {filepath}")

def copyCss(debug, foldername):
    source = "style.css"
    dest = os.path.join(foldername, "style.css")
    if debug:
        print(f"Source: {source}")
        print(f"Dest: {dest}")
    shutil.copy(source, dest)
