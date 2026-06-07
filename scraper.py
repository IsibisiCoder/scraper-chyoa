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
    debug = os.environ.get("DEBUG", False)
    if debug:
        print(f"args: {len(sys.argv)}")
    if len(sys.argv) < 2:
        print("call: python scraper.py <config_file> optional: <url>")
        sys.exit(1)

    def __init__(self):
        self.chyoa = Chyoa()

    config_json_file = sys.argv[1]
    url = ""
    if len(sys.argv) == 3:
        url=sys.argv[2]

    # load config and urls from extern json-file
    if not os.path.exists(config_json_file):
        print(f"config-json-file '{config_json_file}' not found!")
        sys.exit(1)

    try:
        with open(config_json_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"config '{config_json_file}' can not loaded '{e}'")
        return

    loginData = config.get("login")
    if not login:
        print(f"No login defined.")
    question_class = config.get("question_class")
    contentClass = config.get("chapter_class")
    chapterHtmltag = config.get("htmltag")
    recursionLimit = config.get("recursionlimit")
    multiplePages = config.get("multiple_pages")
    wholeStoryOnePage = config.get("whole_story_one_page")
    overrideHtmlSites = config.get("override_html_sites")
    storyNameWithId = config.get("storyname_with_id")

    if multiplePages == False and  wholeStoryOnePage == False:
        print("Configuration error: Please set either `multiplepages` or `wholeStoryOnePage` to True")
        return

    if not question_class:
        print("configfile: question_class not found!")
        sys.exit(1)
    if not chapterHtmltag:
        chapterHtmltag = "div"
    
    folderPathStories = config.get("folder")
    if not folderPathStories:
        folderPathStories = "story"
    foldernameImage = config.get("foldername_image")
    if not foldernameImage:
        foldernameImage = "image"

    configuration = Config(loginData, question_class, contentClass, chapterHtmltag, recursionLimit, storyNameWithId, multiplePages, wholeStoryOnePage, overrideHtmlSites, folderPathStories, foldernameImage)

    if debug:
        print(f"download-folder is: '{folderPathStories}'")
        print(f"content_class {contentClass} ...")
        print(f"htmltag {chapterHtmltag} ...")

    # read url's from config, if one url not in args
    urls = []
    if not url:
        urls = config.get("urls")
        if not urls or not isinstance(urls, list):
            print(f"configfile: no url's define!")
            sys.exit(1)
    if url:
        urls.append(url)

    with requests.Session() as session:
        login.login(debug, session, configuration)

        if debug:
            print(f"urls: {urls}")
        Chyoa.getStories(debug, session, configuration, urls)

if __name__ == "__main__":
    main()
