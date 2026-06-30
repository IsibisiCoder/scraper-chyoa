import sys
import os
import json
import requests
import login
from chyoa import parser

#call: python scraper.py scraper_config.json <url>
def main():
    debug = os.environ.get("DEBUG", False)
    if debug:
        print(f"args: {len(sys.argv)}")
    if len(sys.argv) < 2:
        print("call: python scraper.py <config_datei> optional: <url>")
        sys.exit(1)

    def __init__(self):
        self.parser = parser()

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

    question_class = config.get("question_class")
    content_class = config.get("chapter_class")
    chapter_htmltag = config.get("htmltag")
    recursionlimit = config.get("recursionlimit")
    oneHtmlSite = config.get("oneHtmlSite")
    htmlSiteOverride = config.get("htmlSiteOverride")
    createEpub = config.get("createEpub", False)
    if not question_class:
        print("configfile: question_class not found!")
        sys.exit(1)
    if not chapter_htmltag:
        chapter_htmltag = "div"
    
    folder = config.get("folder")
    if not folder:
        folder = "story"
    imagefolder = config.get("imagefolder")
    if not imagefolder:
        imagefolder = "image"

    if debug:
        print(f"download-folder is: '{folder}'")
        print(f"content_class {content_class} ...")
        print(f"htmltag {chapter_htmltag} ...")

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
        login.login(debug, session, config)

        if debug:
            print(f"urls: {urls}")
        parser.getStories(debug, session, folder, imagefolder, urls, question_class, content_class, chapter_htmltag, oneHtmlSite, htmlSiteOverride, recursionlimit, createEpub)

if __name__ == "__main__":
    main()
