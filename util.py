# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
import filecmp
import os
from urllib.parse import parse_qs, urlparse
import shutil
import re
import requests

import personal_settings

"""
create unique filename
base_name: filename without extension (e.g. 'output')
extension: extension without point (e.g. 'html')
"""
#@staticmethod
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

def get_filename_from_url(url, folder):
    parsed = urlparse(url)

    filename = os.path.basename(parsed.path)

    # filename are in query-parameter (e.g. ?file=image.jpg)
    if not filename or "." not in filename:
        query_params = parse_qs(parsed.query)
        if "file" in query_params:
            filename = query_params["file"][0]

    filename_without_suffix, suffix = os.path.splitext(str(filename))

    # The file name can be up to 255 characters long, so it must be shortened here
    short_filename_without_suffix = filename_without_suffix[:200]
    short_filename_without_suffix = re.sub(r'[^a-zA-Z0-9áéíóàèìòîâûêäöüÄÖÜß\s]', "-", short_filename_without_suffix)
    new_filepath = os.path.join(folder, short_filename_without_suffix + suffix)
    filename = f"{short_filename_without_suffix}{suffix}"

    counter = 1
    while os.path.exists(new_filepath):
        filename = f"{short_filename_without_suffix}_{counter:03d}{suffix}"
        new_filepath = os.path.join(folder, filename)
        counter += 1

    return str(filename)



# save image, return local filename
def download_image(debug, config, root_story, img_url):
    # remove markdown syntax, if markdown detected
    if img_url.startswith("![](<") or img_url.startswith("[![](<")  or img_url.startswith("[]"):
        _, _, img_url = img_url.partition(')')
        img_url, _, _ = img_url.partition(')')

    img_url = img_url.split("?")[0].replace("<", "").replace(">", "")
    img_url = requests.utils.quote(img_url, safe=":/")

    #check if url is in ignore list or if url is in replacement list
    if check_if_ignore_image(config, img_url):
        if config.show_skip_loading_image:
            print(f"                Ignore image url is in ignore list: {img_url}")
        return ""

    replacement_img_url, is_replacement = get_image_url_if_replacement_image_exists(root_story.images_replacement_url, img_url)
    img_url_replace = replacement_img_url
    if debug and is_replacement and config.show_skip_loading_image:
        print(f"                image url is in replacement list, image-url: {img_url}")

    if img_url_replace == "" and not config.connect_invalid_image_empty_image:
        return ""

    os.makedirs(root_story.folderpath_image, exist_ok=True)

    filename = get_filename_from_url(img_url, root_story.folderpath_image)
    filepath = os.path.join(root_story.folderpath_image, filename)
    filepath_relativ = os.path.join(config.foldername_image, filename)
    if debug:
        print(f"Image filepath: {filepath}")
        print(f"filepath relativ: {filepath_relativ}")
        print(f"laenge: {len(filename)}")

    if not is_replacement:
        if debug:
            print(f"              downloading image url: {img_url}")
        status_code = 200
        try:
            #headers = {
            #    "User-Agent": config.http_header_user_agent,
            #   "Referer": config.http_header_referer
            #}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://google.com"
            }

            img_data = requests.get(img_url, stream=True, timeout=30, allow_redirects=False, headers=headers)
            status_code = img_data.status_code
            if status_code != 200:
                if config.show_error_loading_image:
                    print(f"                Error downloading image: Status {status_code} - {img_url}")
                    if config.connect_invalid_image_empty_image:
                        shutil.copy2(src=config.empty_image, dst=filepath)
                    else:
                        filepath_relativ = ""
                    if root_story.personal_settings:
                        root_story.personal_settings.write_personal_settings_with_ignore_url(img_url)
                return ""
            img_data.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in img_data.iter_content(chunk_size=8192):
                    f.write(chunk)
            if debug:
                print(f"image saved: {filepath}")

            if config.foldername_images_shadow_copy:
                dest_pfad = copy_shadow_image(config, filepath, filename)
                if config.connect_always_images and root_story.personal_settings:
                    root_story.personal_settings.write_personal_settings_with_ignore_url(img_url, dest_pfad)

        except requests.exceptions.HTTPError as err_http:
            if config.show_error_loading_image:
                print(f"                HTTP-Error image: {img_url}: {err_http}")
            if config.connect_invalid_image_empty_image:
                shutil.copy2(src=config.empty_image, dst=filepath)
            else:
                filepath_relativ = ""
            if root_story.personal_settings:
                root_story.personal_settings.write_personal_settings_with_ignore_url(img_url)
        except requests.exceptions.ConnectionError:
            if config.show_error_loading_image:
                print(f"                ConnectionError image: Please check your connection or the url. {img_url}")
            if config.connect_invalid_image_empty_image:
                shutil.copy2(src=config.empty_image, dst=filepath)
            else:
                filepath_relativ = ""
            if root_story.personal_settings:
                root_story.personal_settings.write_personal_settings_with_ignore_url(img_url)
        except requests.exceptions.Timeout:
            if config.show_error_loading_image:
                print(f"                Timeout image: The website has an timeout: {img_url}")
            if config.connect_invalid_image_empty_image:
                shutil.copy(src=config.empty_image, dst=filepath)
            else:
                filepath_relativ = ""
            if root_story.personal_settings:
                root_story.personal_settings.write_personal_settings_with_ignore_url(img_url)
        except Exception as err:
            if config.show_error_loading_image:
                print(f"                An unexpected error occurred while loading image: {img_url}: {err}")
            if config.connect_invalid_image_empty_image:
                shutil.copy2(src=config.empty_image, dst=filepath)
            else:
                filepath_relativ = ""
            if root_story.personal_settings:
                #print(f"p: {root_story.personal_settings.personal_settings_file}")
                #root_story.personal_settings.write_personal_settings_with_ignore_url(img_url)
                root_story.personal_settings.write_personal_settings_with_ignore_url(img_url)
    else:
        if img_url_replace == "":
            shutil.copy2(src=config.empty_image, dst=filepath)
            return filepath_relativ

        if os.path.isfile(img_url_replace):
            shutil.copy2(img_url_replace, filepath)
            if debug:
                print(f"              Image copied from local file: {img_url_replace} to {filepath_relativ}")
        else:
            if config.show_error_loading_image:
                print(f"                Error copying image from local file: {img_url_replace} to {filepath_relativ}. File does not exist.")
            filepath_relativ = ""

    return filepath_relativ

def copy_shadow_image(config, filepath, filename):
    foldername_images_shadow = f"{config.foldername_images_shadow_copy}/{config.foldername_story_with_id}"
    os.makedirs(foldername_images_shadow, exist_ok=True)
    filepath_images_shadow = os.path.join(foldername_images_shadow, filename)

    counter = 0
    dest_pfad = os.path.join(foldername_images_shadow, filename)
    base_name, file_suffix = os.path.splitext(filepath_images_shadow)
    while os.path.exists(dest_pfad):
        if filecmp.cmp(dest_pfad, filepath, shallow=False):
            return dest_pfad
        new_filename = f"{base_name}_{counter}{file_suffix}"
        dest_pfad = os.path.join(foldername_images_shadow, new_filename)
        counter += 1

    shutil.copy(src=filepath, dst=dest_pfad)
    return dest_pfad

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
