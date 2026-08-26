"""script to scrape one or more stories"""
# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder

import sys
import os
import json
import requests
import login
from config import Config
from chyoa import Chyoa

#call: python scraper.py scraper_config.json <url>
def main():
    """main"""
    version = "scraper-chyoa V1.3.1alpha"
    print(f"{version}, MIT-License")

    debug = os.environ.get("DEBUG", False)
    debug = False
    if debug:
        print(f"args: {len(sys.argv)}")
    if len(sys.argv) < 2:
        print("call: python scraper.py <config_file> optional: <url>")
        sys.exit(1)

    config_json_file = sys.argv[1]
    url = ""
    if len(sys.argv) == 3:
        url=sys.argv[2]

    # load config and urls from extern json-file
    if not os.path.exists(config_json_file):
        print(f"config-json-file '{config_json_file}' not found!")
        sys.exit(1)

    try:
        with open(config_json_file, 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
    except Exception as e:
        print(f"config '{config_json_file}' can not loaded '{e}'")
        sys.exit(1)

    login_data = config.get("login")
    question_class = config.get("question_class")
    content_class = config.get("chapter_class")
    chapter_htmltag = config.get("htmltag", "div")
    folderpath_stories = config.get("folder", "story")
    recursion_limit = config.get("recursionlimit")
    multiple_pages = config.get("multiple_pages")
    whole_story_one_page = config.get("whole_story_one_page")
    override_html_sites = config.get("htmlSiteOverride")
    storyname_with_id = config.get("storyname_with_id")
    show_error_loading_image = config.get("show_error_loading_image")
    show_skip_loading_image = config.get("show_skip_loading_image", True)
    show_chapter_name_loading_story = config.get("show_chapter_name_loading_story")
    directory_exists_skip_download = config.get("directory_exists_skip_download", False)
    waiting_time_between_downloads_of = config.get("waiting_time_between_downloads_of", 2)
    waiting_time_between_downloads_until = config.get("waiting_time_between_downloads_until", 5)
    ignore_links = config.get("ignore_links", [])

    http_header = config.get("http_header")
    http_header_user_agent = http_header.get("http_header_user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0")
    http_header_referer = http_header.get("http_header_referer", "https://www.google.com")

    image = config.get("image")
    http_img_alt_text = image.get("http_img_alt_text", "Image")
    http_img_alt_text_cover = image.get("http_img_alt_text_cover", "Cover Image")
    foldername_image = image.get("foldername_image", "image")
    images_ignore_domain_url = image.get("images_ignore_domain_url", [])

    personal_settings = config.get("personal_settings")
    foldername_personal_settings = personal_settings.get("foldername_personal_settings", "personal_settings")
    suffix_personal_settings = personal_settings.get("suffix_personal_settings", "mytags")

    epub = config.get("epub")
    create_epub = epub.get("create_epub", False)
    image_prefix = epub.get("image_prefix", False)
    include_url_in_epub = config.get("include_url_in_epub", True)
    include_meta_in_epub = config.get("include_meta_in_epub", True)

    translation = config.get("translation")
    translate = translation.get("translate", False)
    translate_language = translation.get("translate_language")
    llm_system = translation.get("llm_system")
    llm_model = translation.get("llm_model")
    llm_question = translation.get("llm_question")
    llm_api = translation.get("llm_api")

    if not multiple_pages and not whole_story_one_page:
        print("Configuration error: Please set either `multiplepages` or `wholeStoryOnePage` to True")
        return

    if not question_class:
        print("configfile: question_class not found!")
        sys.exit(1)

    configuration = Config(
        version,
        login_data,
        question_class,
        content_class,
        chapter_htmltag,
        recursion_limit,
        storyname_with_id,
        multiple_pages,
        whole_story_one_page,
        override_html_sites,
        folderpath_stories,
        foldername_image,
        show_error_loading_image,
        show_skip_loading_image,
        show_chapter_name_loading_story,
        directory_exists_skip_download,
        waiting_time_between_downloads_of,
        waiting_time_between_downloads_until,
        http_header_user_agent,
        http_header_referer,
        http_img_alt_text,
        http_img_alt_text_cover,
        images_ignore_domain_url,
        foldername_personal_settings,
        suffix_personal_settings,
        create_epub,
        ignore_links,
        image_prefix,
        include_url_in_epub,
        include_meta_in_epub,
        translate,
        translate_language,
        llm_system,
        llm_model,
        llm_question,
        llm_api)

    if debug:
        print(f"download-folder is: '{folderpath_stories}'")
        print(f"content_class {content_class} ...")
        print(f"htmltag {chapter_htmltag} ...")

    # read url's from config, if one url not in args
    urls = []
    if not url:
        urls = config.get("urls")
        if not urls or not isinstance(urls, list):
            print("configfile: no url's define!")
            sys.exit(1)
    if url:
        urls.append(url)

    headers = {
        "User-Agent": http_header_user_agent,
        "Referer": http_header_referer
    }

    with requests.Session() as session:
        session.headers.update(headers)

        login.login(debug, session, configuration)

        if debug:
            print(f"urls: {urls}")
        chyoa = Chyoa()
        chyoa.get_stories(debug, session, configuration, urls)

if __name__ == "__main__":
    main()
