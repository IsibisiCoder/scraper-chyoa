# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
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
def download_image(debug, config, images_replacement_url, filename_base_name, image_folderpath, image_folder_name_only, img_url):
    # remove markdown syntax, if markdown detected
    if img_url.startswith("![](<") or img_url.startswith("[![](<")  or img_url.startswith("[]"):
        _, _, img_url = img_url.partition(')')
        img_url, _, _ = img_url.partition(')')
        #if debug:
        #  print(f"new url: {img_url}")

    img_url = img_url.split("?")[0].replace("<", "").replace(">", "")
    img_url = requests.utils.quote(img_url, safe=":/")

    #check if url is in ignore list or if url is in replacement list
    if check_if_ignore_image(config, img_url):
        if config.show_skip_loading_image:
            print(f"                Ignore image url is in ignore list: {img_url}")
        return ""
    replacement_img_url, is_replacement = get_image_url_if_replacement_image_exists(images_replacement_url, img_url)
    original_img_url = img_url
    img_url = replacement_img_url
    if is_replacement and config.show_skip_loading_image:
        print(f"                Replacement image url is in replacement list, new url: {original_img_url}")

    if img_url == "":
        return ""

    os.makedirs(image_folderpath, exist_ok=True)
    suffix = os.path.splitext(img_url)[1][1:]
    if not suffix:
        return ""

    suffix = re.sub(r'[^a-zA-Z0-9áéíóàèìòîâûêäöüÄÖÜß\s]', "-", suffix)

    if debug:
        print(f"suffix: {suffix}")
        print(f"imageFolderPath: {image_folderpath}")

    filename = get_unique_filename(debug, image_folderpath, filename_base_name, suffix)
    filepath = os.path.join(image_folderpath, filename)
    filepath_relativ = os.path.join(image_folder_name_only, filename)
    if debug:
        print(f"Image filepath: {filepath}")
        print(f"filepath relativ: {filepath_relativ}")

    if not is_replacement:
        if debug:
            print(f"              downloading image url: {img_url}")
        status_code = 200
        try:
            headers = {
                "User-Agent": config.http_header_user_agent,
                "Referer": config.http_header_referer
            }

            img_data = requests.get(img_url, stream=True, timeout=30, allow_redirects=False, headers=headers)
            status_code = img_data.status_code
            if status_code != 200:
                if config.show_error_loading_image:
                    print(f"                Error downloading image: Status {status_code} - {img_url}")
                return ""
            img_data.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in img_data.iter_content(chunk_size=8192):
                    f.write(chunk)
            if debug:
                print(f"image saved: {filepath}")
        except requests.exceptions.HTTPError as err_http:
            if config.show_error_loading_image:
                print(f"                HTTP-Error image: {img_url}: {err_http}")
            filepath_relativ = ""
        except requests.exceptions.ConnectionError:
            if config.show_error_loading_image:
                print(f"                ConnectionError image: Please check your connection or the url. {img_url}")
            filepath_relativ = ""
        except requests.exceptions.Timeout:
            if config.show_error_loading_image:
                print(f"                Timeout image: The website has an timeout: {img_url}")
            filepath_relativ = ""
        except Exception as err:
            if config.show_error_loading_image:
                print(f"                An unexpected error occurred while loading image: {img_url}: {err}")
            filepath_relativ = ""
    else:
        filepath_new_image = os.path.join(config.foldername_personal_settings, img_url)
        if os.path.isfile(filepath_new_image):
            shutil.copy(filepath_new_image, filepath)
            if debug:
                print(f"              Image copied from local file: {img_url} to {filepath_relativ}")
        else:
            if config.show_error_loading_image:
                print(f"                Error copying image from local file: {filepath_new_image} to {filepath_relativ}. File does not exist; (Orig-file: {img_url}).")
            filepath_relativ = ""

    return filepath_relativ

def get_image_url_if_replacement_image_exists(images_replacement_url, img_url):
    if not images_replacement_url:
        return img_url, False
    for image in images_replacement_url:
        if image["invalid_image_url"] == img_url:
            return image["replacement_url"], True
    return img_url, False

def check_if_ignore_image(config, img_url):
    for image in config.images_ignore_domain_url:
        if img_url.startswith(image):
            return True
    return False

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

def copy_css(debug, foldername, source_filename):
    dest_filename = os.path.join(foldername, source_filename)
    if debug:
        print(f"Source: {source_filename}")
        print(f"Dest: {dest_filename}")
    shutil.copy(source_filename, dest_filename)
