"""read stories and save them"""
#(c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
import sys
import re
from datetime import datetime
import time
import random
import os
from ebooklib import epub
import uuid
import requests
from bs4 import BeautifulSoup

import story
from story import Story
from meta import Meta
from node import Node
from util import get_unique_filename, download_image, save, copy_css
from personal_settings import PersonalSettings

class Chyoa:
    """class chyoa"""
    def get_stories(self, debug, session, config, urls):
        """get all stories defined in urls"""
        print()
        # pylint: disable=W0612
        for idx, url in enumerate(urls, 1):
            try:
                start = time.perf_counter()

                soup, _ = self.get_soup(debug, session, config, url)
                if not soup:
                    continue

                story_header1, story_header2, foldername_story = self.scrape_story_title(debug, soup)
                if len(foldername_story) > 100:
                    foldername_story = foldername_story[0:100]
                story_title = story_header2

                meta = Meta(debug)
                meta.scrape_meta_properties(soup)
                meta.scrape_json(soup)
                meta.url = url

                foldername_story = foldername_story.strip("-")
                # Determine the ID of the home page from the URL (the number after the period)
                id_of_startsite = url.split(".")[-1]
                if id_of_startsite:
                    foldername_story_with_id = f"{foldername_story}_({id_of_startsite})"
                else:
                    foldername_story_with_id = foldername_story

                personal_settings = PersonalSettings(debug, config)
                personal_tags_of_story, images_replacement_url = personal_settings.read_personal_settings(foldername_story_with_id)

                story_id = 1

                root_story = Story(
                    config = config,
                    story_id = story_id,
                    url = url,
                    meta = meta,
                    linktext = "",
                    follow = True,
                    redirect = False,
                    story_title = story_title,
                    story_header1 = story_header1,
                    story_header2 = story_header2,
                    filename_map = foldername_story + "-map.html",
                    filename_total = foldername_story + "-total.html",
                    personal_tags = personal_tags_of_story,
                    images_replacement_url = images_replacement_url
                )

                # create folder with modified_time
                folder = foldername_story_with_id
                if meta.modified_time_short != '':
                    folder = folder + f'_({meta.modified_time_short})'
                if config.directory_exists_skip_download and root_story.check_folder_if_exists(folder):
                    print(f"[skip story]    {story_title}")
                    continue
                root_story.create_folder(folder)
                root_story.create_folder_image()
                if debug:
                    print(f"root.storyFolderpath: {root_story.folderpath_story}")
                    print(f"root.imageFolderPath: {root_story.image_folderpath}")

                print(f"[story]         {story_title}")
                print(f"[folder]        {root_story.folderpath_story}")
                if (personal_tags_of_story):
                    print("[personal]      personal tags found")
                if (images_replacement_url):
                    print("[personal]      personal settings - replacement url for images found")
                print(f"[downloading]   {url}")

                chapter_title, author,  _, _ = self.scrape_chapter_title_story_header(debug, soup)
                root_story.meta.author = author
                filename = self.create_filename(debug, story_header2, story_title, config.folderpath_stories)
                question = self.scrape_question(debug, soup)
                story_content = self.scrape_content(debug, soup, images_replacement_url, root_story.image_folderpath, config)
                image_filename, soup = self.scrape_story_cover(debug, config, soup, images_replacement_url, root_story.image_folderpath, config.foldername_image)

                startsite = f"{story_id:04d}"+"-"+filename

                root_story.set(
                    story_image = image_filename,
                    chapter_title = chapter_title,
                    question = question,
                    filename = f"{story_id:04d}"+"-"+filename,
                    parent_filename = "",
                    parent_id = "",
                    startsite = startsite,
                    text = story_content
                )
                root = Node(root_story)

                sys.setrecursionlimit(config.recursion_limit)
                story_id = self.get_links_from_site(debug, config, images_replacement_url, root, root, session, url, story_id, startsite, story_id)
                if not story_id:
                    return
                if debug:
                    print(f"Count: {story_id}")

                # Find the links and replace the placeholders with the linked information
                Node.check_all_chapters(root, root)

                copy_css(debug, root.value.folderpath_story, "style.css")
                print("[saving]")

                if config.multiple_pages:
                    self.save_stories(debug, root_story.folderpath_story, root, config, True)
                if config.whole_story_one_page:
                    self.save_stories_to_one_file(debug, root_story.folderpath_story, root, config)

                if config.multiple_pages:
                    self.create_map(debug, root_story.folderpath_story, root_story.filename_map, root, config.multiple_pages, config.override_html_sites)

                if getattr(config, 'create_epub', False):
                    print(f"[Generate EPUB] {root_story.folderpath_story} ...")
                    self.save_epub(debug, root_story.folderpath_story, root, config)

                end = time.perf_counter()
                duration = end - start
                hours, rest = divmod(duration, 3600)
                minutes, seconds = divmod(rest, 60)

                print(f"[completed]     duration: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}\n")

            except requests.RequestException as e:
                print(f"Error loading {url}: {e}")
        print("[finished]")

    def get_soup(self, debug, session, config, url):
        try:
            # A wait time to prevent the web server from becoming overloaded.
            # Random pauses are inserted between two values to prevent the server from being locked out.
            wait_time = random.uniform(config.waiting_time_between_downloads_of, config.waiting_time_between_downloads_until)
            time.sleep(wait_time)
            response = session.get(url)
            # If a link in chyao points to a new page, an HTTP redirect (302) is performed.
            # To intercept and evaluate this redirect, the response-url must be returned as well
            response_url = response.url
            #status_code = response.status_code
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup, response_url
        except requests.exceptions.HTTPError as err_http:
            print(f"HTTP-Error story link: {url}: {err_http}")
        return None, None

    def get_links_from_site(self, debug, config, images_replacement_url, root, node, session, url, story_id, parent_filename, parent_id):
        soup, _ = self.get_soup(debug, session, config, url)
        if not soup:
            return None

        linksfromsite, story_id = self.scrape_links(debug, config, session, soup, images_replacement_url, root, story_id, parent_filename, parent_id)
        for link in linksfromsite:
            current_node = Node(link)
            node.add_child(current_node)
            if link.follow:
                story_id = self.get_links_from_site(debug, config, images_replacement_url, root, current_node, session, link.url, story_id, current_node.value.filename, current_node.value.id)
            else:
                if debug:
                    print(f"Url: {link.url} / Parent {parent_filename} exists and links from url do not follow!")
        return story_id

    def scrape_links(self, debug, config, session, soup, images_replacement_url, root, story_id, parent_filename, parent_id):
        all_links = []
        content_navigable_all = soup.find_all(config.chapter_htmltag, class_=config.question_class)

        # anker-tags
        for c in content_navigable_all:
            for a_tag in c.find_all("a"):
                a_href = a_tag.get("href")
                a_text = a_tag.get_text(strip=True)

                # Filter out links based on config.ignore_links
                check_link_text = False
                if getattr(config, 'ignore_links', None):
                    check_link_text = any(ignore in a_text for ignore in config.ignore_links) or any(ignore in a_href for ignore in config.ignore_links)

                if not check_link_text:
                    if debug:
                        print(f"link {a_href}")
                        print(f"text {a_text}")
                        print(f"parent {parent_filename}")

                    story_id = story_id + 1
                    soup_current_site, response_url = self.get_soup(debug, session, config, a_href)
                    if not soup_current_site:
                        continue

                    redirect = False
                    if a_href != response_url:
                        redirect = True

                    meta = Meta(debug)
                    meta.scrape_meta_properties(soup_current_site)
                    meta.scrape_json(soup_current_site)

                    chapter_title, author, story_header1, story_header2 = self.scrape_chapter_title_story_header(debug, soup_current_site)
                    meta.author = author
                    filename = f"{story_id:04d}"+"-"+chapter_title.replace(" ", "_").strip()+"-"+self.create_filename(debug, story_header1, root.value.story_title, config.folderpath_stories).strip()

                    question = self.scrape_question(debug, soup_current_site)

                    # If the link is to another chapter, the correct chapter must only be linked once all chapters have been scanned
                    if redirect:
                        follow = False
                        current_link = Story(
                            config,
                            None,
                            response_url,
                            meta,
                            a_text,
                            follow,
                            redirect,
                            root.value.story_title,
                            None,
                            None,
                            root.value.filename_map,
                            root.value.filename_total,
                            root.value.personal_tags,
                            root.value.images_replacement_url
                        )
                        current_link.set(
                            "",
                            chapter_title,
                            None,
                            None,
                            None,
                            None,
                            root.value.start_site,
                            None
                        )
                        all_links.append(current_link)
                        continue

                    contains_url, contains_node = Node.contains(root, a_href)
                    if contains_url:
                        follow = False
                        current_link = Story(
                            config,
                            contains_node.value.id,
                            contains_node.value.url,
                            meta,
                            contains_node.value.linktext,
                            follow,
                            redirect,
                            root.value.story_title,
                            contains_node.value.story_header1,
                            contains_node.value.story_header2,
                            root.value.filename_map,
                            root.value.filename_total,
                            root.value.personal_tags,
                            root.value.images_replacement_url
                        )
                        current_link.set(
                            "", 
                            chapter_title,
                            contains_node.value.question,
                            contains_node.value.filename,
                            contains_node.value.parent_filename,
                            contains_node.value.parent_id,
                            root.value.start_site,
                            contains_node.value.text
                        )
                        all_links.append(current_link)

                    if not contains_url:
                        follow = True
                        story_content = self.scrape_content(debug, soup_current_site, images_replacement_url, root.value.image_folderpath, config)
                        if config.show_chapter_name_loading_story:
                            print(f"Chapter {story_header1}")

                        current_link = Story(
                            config,
                            story_id,
                            a_href,
                            meta,
                            a_text,
                            follow,
                            redirect,
                            root.value.story_title,
                            story_header1,
                            story_header2,
                            root.value.filename_map,
                            root.value.filename_total,
                            root.value.personal_tags,
                            root.value.images_replacement_url
                        )
                        current_link.set(
                            "", 
                            chapter_title,
                            question,
                            filename,
                            parent_filename,
                            parent_id,
                            root.value.start_site,
                            story_content)
                        all_links.append(current_link)
        return all_links, story_id

    def get_all_links(self, debug, node, level=0):
        if debug:
            print("  " * level + str(node.value.linktext))
            print("  " * level + str(node.value.url))
            print("  " * level + str(node.value.storyTitle))
            print("  " * level + str(node.value.chapter_title))
            print("  " * level + str(node.value.filename))
            #print("  " * level + str(node.value.text))
        for child in node.children:
            if child.value.follow:
                self.get_all_links(debug, child, level + 1)

    def scrape_story_title(self, debug, soup):
        header = soup.find('header', class_='story-header')
        story_header1 = ""
        story_header2 = ""
        if header:
            headerh1 = header.find('h1')
            if headerh1:
                story_header2 = headerh1.get_text(strip=True)
            headerh2 = header.find('h2')
            if headerh2:
                story_header1 = headerh2.get_text(strip=True)
        foldername = re.sub(r'[^a-zA-Z0-9áéíóàèìòîâûêäöüÄÖÜß\s]', "-", story_header2).replace(" ", "_")
        if debug:
            print(f"story_header1: {story_header1}")
            print(f"story_header2: {story_header2}")
            print(f"Folder: {foldername}")
        return story_header1, story_header2, foldername

    def scrape_chapter_title_story_header(self, debug, soup):
        """scrape chapter_title_story_header"""
        header = soup.find('header', class_='chapter-header')
        if header:
            h2 = header.find('h2')
            story_header2 = h2.get_text(strip=True)
            h1 = header.find('h1')
            story_header1 = h1.get_text(strip=True)
            if debug:
                print(f"story_header 1: {story_header1}")
                print(f"story_header 2: {story_header2}")
        if not header:
            story_header1 = ""
            story_header2 = ""

        meta = soup.find('p', class_='meta')
        if not meta:
            return "", "", "", ""

        #search by author
        meta_complete = meta.get_text()
        index = meta_complete.find("by ")
        chapter_title = meta_complete[:index].strip()

        a_tag = meta.find('a')
        if a_tag:
            author = a_tag.get_text(strip=True)
        else:
            author = ""
        if debug:
            print(f"author: {author}")

        return chapter_title, author, story_header1, story_header2

    def create_filename(self, debug, title, story_title, folder):
        filename = title
        if not filename:
            filename = story_title
        filename = get_unique_filename(debug, folder, re.sub(r'[^a-zA-Z0-9áéíóàèìòîâûêäöüÄÖÜß\s]', "-", title).replace(" ", "_").replace('"', '_').strip("-"), "html")
        if debug:
            print(f"filename: {filename}")
        return filename

    def scrape_question(self, debug, soup):
        """read the question"""
        header = soup.find('header', class_='question-header')
        question = ""
        if header:
            h2 = header.find('h2')
            if h2:
                question = h2.get_text(strip=True)
        if debug:
            print(f"question: {question}")
        return question

    def scrape_images(self, debug, soup, config, images_replacement_url, image_folderpath):
        """scrape images"""
        for img in soup.find_all("img"):
            img_src = img.get("src")
            if img_src:
                if debug:
                    print(f'image-src: {img_src}')
                filename_image = download_image(debug, config, images_replacement_url, "chapter-image", image_folderpath, config.foldername_image, img_src)
                if filename_image != "":
                    img["src"] = filename_image
                    img_alt = img.get("alt")
                    if img_alt == "" or img_alt is None:
                        img["alt"] = config.http_img_alt_text
                    if debug:
                        print(f'image-src: {img_src}')
                        print(f'replace with: {filename_image}')
                else:
                    img.decompose()
        return soup

    def scrape_story_cover(self, debug, config, soup, images_replacement_url, image_folderpath, foldername_image):
        """scrape cover"""
        filename_image = ""
        cover = soup.find('div', class_='cover')
        if cover:
            img = cover.find('img')
            img_src = img.get("src")
            if img_src:
                if debug:
                    print(f'cover image-src: {img_src}')
                filename_image = download_image(debug, config, images_replacement_url, "story", image_folderpath,
                                                foldername_image, img_src)
                img_alt = img.get("alt")
                if img_alt == "" or img_alt is None:
                    img["alt"] = config.http_img_alt_text_cover
            else:
                img.decompose()
        return filename_image, soup

    def scrape_content(self, debug, soup, images_replacement_url, image_folderpath, config):
        """scrape the content"""
        content_navigable_all = soup.find_all(config.chapter_htmltag, class_=config.content_class)
        if not content_navigable_all:
            return "<!-- no content found -->"

        #save images and convert image name in html
        soup = self.scrape_images(debug, content_navigable_all[0], config, images_replacement_url, image_folderpath)
        content = soup.prettify() if content_navigable_all else "<!-- no content found -->"
        if debug:
            print(f"Story: {content[1:50]}")
        return content

    def save_stories(self, debug, foldername, node, config, first_page):
        """save stories"""
        if not node.value.follow:
            return
        if debug:
            print(f"save Filename {node.value.filename} - {node.value.follow}")
        html = self.create_html(debug, config, node, config.multiple_pages, first_page)
        if first_page:
            first_page = False
        save(foldername, node.value.filename, node, html, config.override_html_sites)

        if config.multiple_pages:
            for child in node.children:
                self.save_stories(debug, foldername, child, config, first_page)

    def save_stories_to_one_file(self, debug, foldername, node, config):
        if debug:
            print(f"save to one filen {node.value.filename} - {node.value.follow}")
        if config.whole_story_one_page:
            html = self.create_html(debug, config, node, False, True)
            save(foldername, node.value.filename_total, node, html, config.override_html_sites)

    def create_html(self, debug, config, node, multiple_pages, first_page):
        htmltext = []
        htmltext = self.create_html_head(config, htmltext, node, multiple_pages, first_page)
        htmltext = self.create_javascript(htmltext)
        if not multiple_pages:
            htmltext = self.create_map_body(debug, htmltext, node, multiple_pages)
            htmltext = self.create_html_recursive(debug, htmltext, node, multiple_pages, False)
        else:
            htmltext = self.create_html_body(htmltext, node, multiple_pages, first_page)
        htmltext.append("</body></html>")
        return htmltext

    def create_html_recursive(self, debug, htmltext, node, multiple_pages, first_page):
        """get html content of all chapters"""
        htmltext = self.create_html_body(htmltext, node, multiple_pages, first_page)
        if node.value.follow:
            htmltext.append('<hr>')
            for child in node.children:
                htmltext = self.create_html_recursive(debug, htmltext, child, multiple_pages, first_page)
                if first_page:
                    first_page = False
        return htmltext

    def create_html_body(self, htmltext, node, multiple_pages, first_page):
        """get html content of one chapter"""
        if first_page:
            htmltext = self.create_meta(htmltext, node)

        htmltext.append('\n<aside><div class="description">')
        if multiple_pages and not first_page:
            htmltext.append(f'<div class="storytitleshort">| Story: {node.value.story_title}</div>\n')
        htmltext = self.create_description_chapter_body(htmltext, node)
        if first_page:
            htmltext = self.create_description_story_body(htmltext, node)
            htmltext = self.create_personal_tags_story_body(htmltext, node)
        htmltext.append('</div></aside>\n')

        htmltext.append(f'<p id={str(node.value.id)} class="storyheader2">')
        if node.value.story_header2 and node.value.story_header2.strip():
            htmltext.append(f'{node.value.story_header2}')
        htmltext.append('</p>')
        if node.value.story_header1 and node.value.story_header1.strip():
            htmltext.append(f'<div class="storyheader1">{node.value.story_header1}</div>')

        htmltext.append(f'<div class="chapterheader">{node.value.chapter_title.strip()}')
        if node.value.meta.author.strip():
            htmltext.append(f" by {node.value.meta.author}")
            if node.value.meta.published_time_short != "" or node.value.meta.modified_time_short != "":
                htmltext.append('<span class="publisheddate">')
                published_time = ""
                if node.value.meta.published_time_short != "":
                    published_time = f" created on {node.value.meta.published_time_short}"
                if node.value.meta.published_time_short != "" and node.value.meta.modified_time_short != "":
                    published_time = f"{published_time}, "
                if node.value.meta.modified_time_short != "":
                    published_time = f"{published_time}updated on {node.value.meta.modified_time_short}"
                htmltext.append(published_time)
                htmltext.append('</span>')
        htmltext.append("</div>")

        htmltext.append('<hr>')
        htmltext.append(f'<section>{node.value.text}</section>')
        htmltext.append('<hr>')
        htmltext.append(f'<div class="question-header">{node.value.question}</div>')
        htmltext.append('<div class="question-content">')
        if node.children:
            for child in node.children:
                if multiple_pages:
                    htmltext.append(f'<div class="list-item anker-text"><a href="{child.value.filename}">{child.value.linktext}</a></div>')
                else:
                    htmltext.append(f'<div class="list-item"><a href="#{child.value.id}" class="anker-text">{child.value.linktext}</a></div>')
        htmltext.append('<br><hr>')
        if node.value.parent_filename:
            if multiple_pages:
                htmltext.append(f'<div class="list-item-previous"><a href="{node.value.parent_filename}" class="anker-text-map-start">Previous Chapter</a></div>')
            else:
                htmltext.append(f'<div class="list-item-previous"><a href="#{node.value.parent_id}" class="anker-text-map-start">Previous Chapter</a></div>')
        if node.value.start_site:
            if multiple_pages:
                htmltext.append(f'<div class="list-item-previous"><a href="{node.value.start_site}" class="anker-text-map-start">Start Over</a></div>')
            else:
                htmltext.append('<div class="list-item-previous"><a href="#" class="anker-text-map-start">Start Over</a></div>')
        if node.value.filename_map and multiple_pages:
            htmltext.append(f'<div class="list-item-previous"><a href="{node.value.filename_map}" class="anker-text-map-start">Map</a></div>')
        htmltext.append("</div>\n")
        return htmltext

    def create_meta(self, htmltext, node):
        """create meta-tags of one chapter"""
        htmltext.append(f'\n<meta name="story" content="{node.value.story_title}">\n')
        htmltext.append(f'<meta name="title" content="{node.value.chapter_title}">\n')
        htmltext.append(f'<meta name="author" content="{node.value.meta.author}">\n')
        htmltext.append(f'<meta name="language" content="{node.value.meta.language}">\n')
        if node.value.meta.tag.strip():
            htmltext.append(f'<meta name="tag" content="{node.value.meta.tag}">\n')
        if node.value.meta.category.strip():
            htmltext.append(f'<meta name="category" content="{node.value.meta.category}">\n')
        if node.value.meta.published_time_short.strip():
            htmltext.append(f'<meta name="published_time" content="{node.value.meta.published_time_short}">\n')
        if node.value.meta.modified_time_short.strip():
            htmltext.append(f'<meta name="modified_time" content="{node.value.meta.modified_time_short}">\n')
        htmltext.append(f'<meta name="likes" content="{node.value.meta.likes}">\n')
        htmltext.append(f'<meta name="views" content="{node.value.meta.views}">\n')
        htmltext.append(f'<meta name="scraper_date" content="{datetime.now().strftime('%Y-%m-%d')}">\n')

        if node.value.personal_tags:
            for key, value in node.value.personal_tags.items():
                if not value:
                    continue
                personal_tag_value = value.replace("<br>", "").replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "").replace("<u>", "").replace("</u>", "")
                htmltext.append(f'<meta name="{key}" content="{personal_tag_value}">\n')

        return htmltext

    def create_html_head(self, config, htmltext, node, multiple_pages, first_page):
        """create html body with title"""
        htmltext.append("<!DOCTYPE html>\n")
        htmltext.append(f'<html><head><meta charset="utf-8"><meta name="generator" content="{config.version}">\n')
        if multiple_pages:
            htmltext.append(f"<title>{node.value.chapter_title} - {node.value.story_header2}</title>\n")
        else:
            htmltext.append(f"<title>{node.value.story_title}</title>\n")
        htmltext.append('<link rel="stylesheet" href="style.css">\n')
        htmltext.append("</head><body>\n")
        if node.value.story_image:
            htmltext.append(f'<div class="cover"><img src="{node.value.story_image}" alt="Image of {node.value.story_title}" /></div>\n')
        if node.value.story_title and (not multiple_pages or first_page):
            htmltext.append(f'<h1 class="storytitle">{node.value.story_title}</h1>\n')
        return htmltext

    def create_map_links(self, debug, node, htmltext, multiple_pages, follow, level=0):
        """create links"""
        linktext = node.value.linktext

        if not linktext:
            linktext = node.value.story_title

        additional_text = ""
        if node.value.meta.author != "":
            additional_text = additional_text + f'<span class="author-link">by {node.value.meta.author}</span>'
        if node.value.meta.published_time_short != "" or node.value.meta.modified_time_short != "":
            published_time = '<span class="publisheddate-link">'
            if node.value.meta.published_time_short != "":
                published_time = f"{published_time} (created on {node.value.meta.published_time_short}"
            if node.value.meta.published_time_short != "" and node.value.meta.modified_time_short != "":
                published_time = f"{published_time},   "
            if node.value.meta.modified_time_short != "":
                published_time = f"{time}updated on {node.value.meta.published_time_short}"
            published_time = published_time + '</span>'

        style = "margin-left: 30px;"
        #display = "display: block;"
        htmltext.append('<div class="node">')
        if follow:
            childrenlen = len(node.children)
            htmltext = self.create_button(htmltext, node.value.filename, node.value.id, node.value.chapter_title + " - " + linktext, additional_text, multiple_pages, (childrenlen>0))
            if childrenlen > 0:
                htmltext.append(f'<div class="children" style="{style}">')
            for child in node.children:
                htmltext = self.create_map_links(debug, child, htmltext, multiple_pages, node.value.follow, level + 1)
            if childrenlen > 0:
                htmltext.append('</div>')
        htmltext.append('</div>')
        return htmltext

    def create_button(self, htmltext, url, story_id, linktext, additional_text, multiple_pages, show_button):
        """create toogle button"""
        htmltext.append('<div class="item">')
        if show_button:
            htmltext.append('<button class="toggle"> ▶ </button>')
            #htmltext.append(f'<button class="toggle"> ▼ </button>')
        else:
            htmltext.append('<span class="withoutbutton"> </span>')
        if multiple_pages:
            htmltext.append(f'<a href="{url}">{linktext}</a> {additional_text}')
        else:
            htmltext.append(f'<a href="#{story_id}">{linktext}</a> {additional_text}')
        htmltext.append('</div>')
        return htmltext

    def create_javascript(self, htmltext):
        """create the javascript"""
        htmltext.append('\n<script>')
        htmltext.append('document.addEventListener("DOMContentLoaded", function () {')
        htmltext.append('    const storageKey = "chyoa-scraper-" + document.title;')
        htmltext.append('    const toggles = document.querySelectorAll(".toggle");')
        htmltext.append('    const toggleAllBtn = document.getElementById("toggleAll");')
        htmltext.append('    const childrenLists = document.querySelectorAll(".children");')
        htmltext.append('    let allOpen = sessionStorage.getItem(storageKey) === true;')
        htmltext.append('    toggles.forEach(btn => {')
        htmltext.append('        btn.addEventListener("click", function () {')
        htmltext.append('            const children = this.closest(".node").querySelector(":scope > .children");')
        htmltext.append('            if (!children) return;')
        htmltext.append('            const isOpen = children.classList.toggle("open");')
        htmltext.append('            updateArrow(this, isOpen);')
        htmltext.append('        });')
        htmltext.append('    });')
        htmltext.append('    toggleAllBtn.addEventListener("click", function () {')
        htmltext.append('        allOpen = !allOpen;')
        htmltext.append('        childrenLists.forEach(children => {')
        htmltext.append('            children.classList.toggle("open", allOpen);')
        htmltext.append('        });')
        htmltext.append('        toggles.forEach(btn => {')
        htmltext.append('            updateArrow(btn, allOpen);')
        htmltext.append('        });')
        htmltext.append('        this.textContent = allOpen ? "Collapse all" : "Expand all";')
        htmltext.append('        sessionStorage.setItem(storageKey, allOpen);')
        htmltext.append('    });')
        htmltext.append('    function updateArrow(button, isOpen) {')
        htmltext.append('        button.textContent = isOpen')
        htmltext.append('            ? button.textContent.replace("▶", "▼")')
        htmltext.append('            : button.textContent.replace("▼", "▶");')
        htmltext.append('    }')
        htmltext.append('    toggleAllBtn.click(); ')
        htmltext.append('});')
        htmltext.append('</script>\n\n')
        return htmltext

    def create_map(self, debug, foldername, filename, node, multiple_pages, html_site_override):
        htmltext = []
        if debug:
            print(f"Map-filename: {filename}")
            print(f"Map-foldername: {foldername}")
        htmltext = self.create_map_head(htmltext, node)
        if node.value.story_title and multiple_pages:
            htmltext.append(f'<h1 class="storytitle">Story: {node.value.story_title}</h1>')
        htmltext = self.create_map_body(debug, htmltext, node, multiple_pages)
        htmltext.append("</body></html>")
        save(foldername, filename, node, htmltext, html_site_override)

    def create_personal_tags_story_body(self, htmltext, node):
        if node.value.personal_tags:
            htmltext.append('<div class="personal-tags">')
            for key, value in node.value.personal_tags.items():
                if not value:
                    continue
                htmltext.append(f'| <b>{key}</b>: {value} ')
            htmltext.append('</div>')
        return htmltext

    def create_description_story_body(self, htmltext, node):
        if node.value.meta.description:
            htmltext.append(f'<div>| <b>Description</b>: {node.value.meta.description}</div>')
        properties = "<div>"
        if node.value.meta.category:
            properties = properties + f'| <b>Category</b>: {node.value.meta.category} '
        if node.value.meta.pov:
            properties = properties + f'| <b>Pov</b>: {node.value.meta.pov} '
        if node.value.meta.language:
            properties = properties + f'| <b>Language</b>: {node.value.meta.language} '
        if node.value.meta.url:
            properties = properties + f'| <b>Url</b>: <a href="{node.value.meta.url}" target="_blank">{node.value.meta.url}</a> '
        properties = properties + "</div>"
        htmltext.append(properties)

        return htmltext

    def create_description_chapter_body(self, htmltext, node):
        if node.value.meta.author:
            htmltext.append(f'| <b>Author</b>: {node.value.meta.author} ')
        if node.value.meta.published_time_short:
            htmltext.append(f'| <b>Created</b>: {node.value.meta.published_time_short} ')
        if node.value.meta.modified_time_short:
            htmltext.append(f'| <b>Modified</b>: {node.value.meta.modified_time_short} ')
        if node.value.meta.likes:
            htmltext.append(f'| <b>Likes</b>: {node.value.meta.likes} ')
        if node.value.meta.views:
            htmltext.append(f'| <b>Views</b>: {node.value.meta.views} ')
        if node.value.meta.tag:
            htmltext.append(f'<div class="tag">| <b>Tags</b>: {node.value.meta.tag}</div>\n')

        return htmltext

    def create_map_body(self, debug, htmltext, node, multiple_pages):
        htmltext.append('\n<div class="description">')
        htmltext = self.create_description_chapter_body(htmltext, node)
        htmltext = self.create_description_story_body(htmltext, node)
        htmltext = self.create_personal_tags_story_body(htmltext, node)
        htmltext.append('</div>\n')

        htmltext.append('<hr>')
        htmltext.append('<div class="toggleButton"><button id="toggleAll">Expand all</button></div>')
        style = "margin-left: 30px;"
        htmltext.append(f'<div class="map" style="{style}">')
        htmltext = self.create_map_links(debug, node, htmltext, multiple_pages, True)
        htmltext.append('</div>')
        return htmltext

    def create_map_head(self, htmltext, node):
        htmltext.append("<!DOCTYPE html>")
        htmltext.append("<html><head><meta charset='utf-8'>")
        htmltext.append(f"<title>{node.value.story_title}</title>")
        htmltext.append('<link rel="stylesheet" href="style.css">')
        htmltext = self.create_javascript(htmltext)
        htmltext.append('</head><body>')
        return htmltext

    def _add_epub_chapter(self, book, parent_nav_item, epub_chapters, node):
        """Recursively builds the EPUB structure starting from a root node"""
        current_epub_item = epub_chapters.get(node.value.id)
        if current_epub_item:
            # Check if this node has children
            if len(node.children) > 0:
                # Add it as a section containing its children
                children_nav = []
                for child in node.children:
                    child_nav = self._add_epub_chapter(book, current_epub_item, epub_chapters, child)
                    if child_nav:
                        children_nav.append(child_nav)
                return (current_epub_item, children_nav)
            else:
                return current_epub_item
        return None

    def save_epub(self, debug, folderpath, root, config):
        book = epub.EpubBook()
        book.set_identifier(str(uuid.uuid4()))
        story_title = root.value.story_title or root.value.chapter_title
        book.set_title(story_title)

        # Use language_alternate_name if available, fallback to en
        lang = getattr(root.value.meta, 'language_alternate_name', 'en')
        if not lang:
            lang = 'en'
        book.set_language(lang)

        if root.value.meta.author:
            book.add_author(root.value.meta.author)

        if root.value.meta.description:
            book.add_metadata('DC', 'description', root.value.meta.description)

        if root.value.meta.published_time_short:
            book.add_metadata('DC', 'date', root.value.meta.published_time_short)

        # add cover if available
        if root.value.story_image and os.path.exists(os.path.join(folderpath, root.value.story_image)):
            with open(os.path.join(folderpath, root.value.story_image), "rb") as f:
                book.set_cover(root.value.story_image, f.read())
 

        # Gather all nodes to process chapters
        all_nodes = []
        def gather_nodes(node, level, sibling_index):
            if not hasattr(node, 'toc_number'):
                node.toc_number = f"{level}.{sibling_index}"
            if node not in all_nodes:
                all_nodes.append(node)
                for idx, child in enumerate(node.children, 1):
                    if (child.value.follow):
                        gather_nodes(child, level + 1, idx)
        gather_nodes(root, 1, 1)

        # Add the CSS styling
        style_css_path = "style-epub.css"
        css_content = ""
        if os.path.exists(style_css_path):
            with open(style_css_path, "r", encoding="utf-8") as css_file:
                css_content = css_file.read()
        else:
            # Fallback default CSS
            css_content = """body { font-family: Arial, sans-serif; }
                             img { max-width: 100%; height: auto; }
                             .chapter-header { text-align: center; }"""

        default_css = epub.EpubItem(uid="style_nav",
                                  file_name="style/style-epub.css",
                                  media_type="text/css",
                                  content=css_content)
        book.add_item(default_css)

        # Map node ids to epub chapters
        epub_chapters = {}
        for node in all_nodes:
            c_title = node.value.story_header1 or node.value.chapter_title or story_title
            c = epub.EpubHtml(title=f"{node.toc_number} {c_title}", file_name=f'chapter_{node.value.id}.xhtml', lang=lang)
            c.add_item(default_css)

            # Build the chapter HTML content
            chapter_html = ""
            if node.value.story_header1 and node.value.chapter_title:
                if node.value.story_header1.strip() != node.value.chapter_title.strip():
                    chapter_html += f"<h1>{node.value.story_header1}</h1>"
                    chapter_html += f"<h2>{node.value.chapter_title}</h2>"
                else:
                    chapter_html += f"<h1>{node.value.chapter_title}</h1>"
            elif node.value.story_header1:
                chapter_html += f"<h1>{node.value.story_header1}</h1>"
            else:
                chapter_html += f"<h1>{node.value.chapter_title}</h1>"

            if getattr(config, 'include_meta_in_epub', False):
                meta_html = ""
                if node.value.meta.author:
                    meta_html += f"<b>Author:</b> {node.value.meta.author}<br/>"
                if node.value.meta.published_time_short:
                    meta_html += f"<b>Created:</b> {node.value.meta.published_time_short}<br/>"
                if node.value.meta.modified_time_short:
                    meta_html += f"<b>Modified:</b> {node.value.meta.modified_time_short}<br/>"
                if meta_html:
                    chapter_html += f'<p style="font-size: small; color: #666;">{meta_html}</p>'

            chapter_html += node.value.text

            # Add links to child chapters ("What's Next")
            if len(node.children) > 0:
                chapter_html += "<h3>What's Next:</h3><ul>"
                for child in node.children:
                    child_title = child.value.story_header1 or child.value.chapter_title or "Next Chapter"
                    chapter_html += f'<li><a href="chapter_{child.value.id}.xhtml">{child_title}</a></li>'
                chapter_html += "</ul>"
            elif not node.value.follow:
                chapter_html += "<p><em>This path ends here.</em></p>"

            if getattr(config, 'include_url_in_epub', False) and node.value.url:
                chapter_html += f'<br/><p><a href="{node.value.url}">Original Chapter URL</a></p>'

            c.content = f'<html><head><link href="style/style-epub.css" rel="stylesheet" type="text/css"/></head><body>{chapter_html}</body></html>'
            book.add_item(c)
            epub_chapters[node.value.id] = c

        # Images logic
        image_foldername = config.foldername_image
        image_dir = os.path.join(folderpath, image_foldername)
        if os.path.exists(image_dir):
            for img_name in os.listdir(image_dir):
                # Skip the cover image if it's already set as the book cover
                if root.value.story_image:
                    relative_img_path = os.path.join(image_foldername, img_name)
                    if relative_img_path == root.value.story_image:
                        continue
                img_path = os.path.join(image_dir, img_name)
                if os.path.isfile(img_path):
                    with open(img_path, "rb") as f:
                        img_content = f.read()

                    media_type = "image/jpeg"
                    if img_name.lower().endswith('.png'):
                        media_type = "image/png"
                    elif img_name.lower().endswith('.gif'):
                        media_type = "image/gif"
                    elif img_name.lower().endswith('.webp'):
                        media_type = "image/webp"

                    epub_img = epub.EpubItem(uid=img_name,
                                           file_name=f"{image_foldername}/{img_name}",
                                           media_type=media_type,
                                           content=img_content)
                    book.add_item(epub_img)

        # Build TOC recursively
        # Replace the nested TOC with a flat TOC to prevent deep nesting off-screen
        book.toc = tuple(epub_chapters.values())

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        book.spine = ['nav'] + list(epub_chapters.values())

        # Cleanup story title for filename
        safe_title = "".join([c for c in story_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        safe_title = safe_title.replace(' ', '_')
        if not safe_title:
            safe_title = "story"
        epub_filename = os.path.join(folderpath, f"{safe_title}.epub")
        epub.write_epub(epub_filename, book, {})
