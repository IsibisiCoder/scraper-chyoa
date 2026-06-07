# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
import sys
import os
import requests
import re
from config import Config
from story import Story
from node import Node
from util import get_unique_filename, download_image, save, copyCss
from bs4 import BeautifulSoup


class Chyoa:
    def getStories(debug, session, config, urls):
        for idx, url in enumerate(urls, 1):
            try:
                print(f"load {url} ...")

                soup = Chyoa.getSoup(debug, session, url)
                storyHeader1, storyHeader2, foldernameStory = Chyoa.scrapeStoryTitle(debug, soup)
                if len(foldernameStory) > 100:
                    foldernameStory = foldernameStory[0:100]
                storyTitle = storyHeader2
                foldernameStory = foldernameStory.lstrip("-")

                id = 1

                print(f"foldernameStory {foldernameStory}")

                root_story = Story(
                    config = config,
                    id = id,
                    url = url,
                    linktext = "",
                    follow = True,
                    storyTitle = storyTitle,
                    story_header1 = storyHeader1,
                    story_header2 = storyHeader2,
                    filenameMap = foldernameStory + "-map.html",
                    filenameTotal = foldernameStory + "-total.html"
                )

                # create folder
                root_story.createFolder(foldernameStory)
                root_story.createFolderImage()
                if debug:
                    print(f"root.storyFolderpath: {root_story.folderpathStory}")
                    print(f"root.imageFolderPath: {root_story.imageFolderPath}")

                chapter_title, ignore1, ignore2, author = Chyoa.scrape_title_author(debug, soup)
                filename = Chyoa.createFilename(debug, storyHeader2, storyTitle, config.folderpathStories).lstrip("-")
                question = Chyoa.scrape_question(debug, soup)
                story = Chyoa.scrape_content(debug, soup, root_story.imageFolderPath, config)
                imageFilename = Chyoa.scrape_StoryCover(debug, soup, root_story.imageFolderPath, config.foldernameImage)
                
                startsite = f"{id:04d}"+"-"+filename

                root_story.set(
                    storyImage = imageFilename,
                    chapter_title = chapter_title,
                    question = question,
                    filename = f"{id:04d}"+"-"+filename,
                    parentFilename = "",
                    parentId = "",
                    startsite = startsite,
                    author = author,
                    text = story
                )
                root = Node(root_story)

                sys.setrecursionlimit(config.recursionLimit)
                id = Chyoa.getlinksfromsite(debug, config, root, root, session, url, id, startsite, id)
                if debug:
                    print(f"Count: {id}")
                    #Chyoa.getAllLinks(debug, root)

                copyCss(debug, root.value.folderpathStory)
                Chyoa.saveStories(debug, root_story.folderpathStory, root, config)

                if config.multiplePages:
                    Chyoa.createMap(debug, root_story.folderpathStory, root_story.filenameMap, root, config.multiplePages, config.overrideHtmlSites)

            except requests.RequestException as e:
                print(f"Error loading {url}: {e}")

    def getSoup(debug, session, url):
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def getlinksfromsite(debug, config, root, node, session, url, id, parentFilename, parentId):
        print(f"Url: {url}")
        
        soup = Chyoa.getSoup(debug, session, url)
        linksfromsite, id = Chyoa.scrape_links(debug, config, session, soup, root, id, parentFilename, parentId)
        for link in linksfromsite:
            currentNode = Node(link)
            node.add_child(currentNode)
            if link.follow == True:
                id = Chyoa.getlinksfromsite(debug, config, root, currentNode, session, link.url, id, currentNode.value.filename, currentNode.value.id)
            else:
                print(f"Url: {link.url} / Parent {parentFilename} exists and links from url do not follow!")
        return id

    def scrape_links(debug, config, session, soup, root, id, parentFilename, parentId):
        all_links = []
        content_navigable_all = soup.find_all(config.chapterHtmltag, class_=config.questionClass)

        # anker-tags
        for c in content_navigable_all:
            for a_tag in c.find_all("a"):
                a_href = a_tag.get("href")
                a_text = a_tag.get_text(strip=True)
                if not a_text == "Add a new chapter":
                    if debug:
                        print(f"link {a_href}")
                        print(f"text {a_text}")
                        print(f"parent {parentFilename}")
                    #    print(f"story_title {story_title}")
                    id = id + 1
                    soup_current_site = Chyoa.getSoup(debug, session, a_href)
                    chapterTitle, story_header1, story_header2, author = Chyoa.scrape_title_author(debug, soup_current_site)
                    filename = f"{id:04d}"+"-"+chapterTitle.strip()+"-"+Chyoa.createFilename(debug, story_header1, root.value.storyTitle, config.folderpathStories).strip()
                    question = Chyoa.scrape_question(debug, soup_current_site)
                    containsUrl, containsNode = Node.contains(root, a_href)
                    if containsUrl == True:
                        follow = False
                        current_link = Story(
                            config, 
                            containsNode.value.id, 
                            containsNode.value.url, 
                            containsNode.value.linktext, 
                            follow, 
                            root.value.storyTitle, 
                            containsNode.value.story_header1, 
                            containsNode.value.story_header2, 
                            root.value.filenameMap,
                            root.value.filenameTotal
                        )
                        current_link.set(
                            "", 
                            chapterTitle, 
                            containsNode.value.question, 
                            containsNode.value.filename, 
                            containsNode.value.parentFilename, 
                            containsNode.value.parentId, 
                            root.value.startSite, 
                            containsNode.value.author, 
                            containsNode.value.text
                        )
                        all_links.append(current_link)
                    if containsUrl == False:
                        story = ""
                        follow = True
                        story = Chyoa.scrape_content(debug, soup_current_site, root.value.imageFolderPath, config)
                        current_link = Story(
                            config, 
                            id, 
                            a_href, 
                            a_text, 
                            follow, 
                            root.value.storyTitle, 
                            story_header1, 
                            story_header2, 
                            root.value.filenameMap,
                            root.value.filenameTotal
                        )
                        current_link.set(
                            "", 
                            chapterTitle, 
                            question, 
                            filename, 
                            parentFilename, 
                            parentId, 
                            root.value.startSite, 
                            author, 
                            story)
                        all_links.append(current_link)
        return all_links, id

    def getAllLinks(debug, node, level=0):
        if debug:
            print("  " * level + str(node.value.linktext))
            print("  " * level + str(node.value.url))
            print("  " * level + str(node.value.storyTitle))
            print("  " * level + str(node.value.chapter_title))
            print("  " * level + str(node.value.filename))
            #print("  " * level + str(node.value.text))
        for child in node.children:
            if child.value.follow == True:
                Chyoa.getAllLinks(debug, child, level + 1)

    def scrapeStoryTitle(debug, soup):
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

    def scrape_title_author(debug, soup):
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
        #search by author
        meta_complete = meta.get_text()
        index = meta_complete.find("by ")
        chapter_title = meta_complete[:index].strip()

        a_tag = meta.find('a')
        if a_tag:
            author = a_tag.get_text(strip=True)
        if not a_tag:
            author = ""
        if debug:
            print(f"author: {author}")
        return chapter_title, story_header1, story_header2, author

    def createFilename(debug, title, story_title, folder):
        filename = title
        if not filename:
            filename = story_title
        filename = get_unique_filename(debug, folder, re.sub(r'[^a-zA-Z0-9áéíóàèìòîâûêäöüÄÖÜß\s]', "-", title).replace(" ", "_").replace('"', '_'), "html")
        if debug:
            print(f"filename: {filename}")
        return filename

    def scrape_question(debug, soup):
        header = soup.find('header', class_='question-header')
        if header:
            h2 = header.find('h2')
            if h2:
                question = h2.get_text(strip=True)
            if not h2:
                question = ""
        if debug:
            print(f"question: {question}")
        return question

    def scrape_images(debug, soup, config, imageFolderPath, content):
        contentNew = content
        for img in soup.find_all("img"):
            img_src = img.get("src")
            if img_src:
                if debug:
                    print(f'image-src: {img_src}')
                filenameImage = download_image(debug, "chapter-image", imageFolderPath, config.foldernameImage, img_src)
                if filenameImage:
                    if debug:
                        print(f'image-src: {img_src}')
                        print(f'replace with: {filenameImage}')
                    contentNew = content.replace(f'{img_src}', f'{filenameImage}') 
        return contentNew

    def scrape_StoryCover(debug, soup, imageFolderPath, foldernameImage):
        filenameImage = ""
        html = ""
        cover = soup.find('div', class_='cover')
        if cover:
            img = cover.find('img')
            img_src = img.get("src")
            if img_src:
                if debug:
                    print(f'cover image-src: {img_src}')
                filenameImage = download_image(debug, "story", imageFolderPath, foldernameImage, img_src)
        return filenameImage

    def scrape_content(debug, soup, imageFolderPath, config):
        content_navigable_all = soup.find_all(config.chapterHtmltag, class_=config.contentClass)
        content = content_navigable_all[0].prettify() if content_navigable_all else "<!-- no content found -->"

        #save iamges
        content = Chyoa.scrape_images(debug, content_navigable_all[0], config, imageFolderPath, content)
        #if debug:
        #    print(f"Story: {content[1:50]}")
        return content

    def saveStories(debug, foldername, node, config):
        if debug:
            print(f"save Filename {node.value.filename} - {node.value.follow}")
        if config.wholeStoryOnePage == True:
            html = Chyoa.createHtml(debug, node, False)
            save(debug, foldername, node.value.filenameTotal, node, html, config.overrideHtmlSites)
        if node.value.follow == True:
            html = Chyoa.createHtml(debug, node, config.multiplePages)
            save(debug, foldername, node.value.filename, node, html, config.overrideHtmlSites)
        if config.multiplePages == True and node.value.follow == True:
            for child in node.children:
                Chyoa.saveStories(debug, foldername, child, config)

    def createHtml(debug, node, multiplePages):
        htmltext = []
        htmltext = Chyoa.createHtmlHead(htmltext, node, multiplePages)
        htmltext = Chyoa.createJavascript(htmltext)
        if multiplePages == False:
            htmltext = Chyoa.createMapBody(debug, htmltext, node, multiplePages)
            htmltext = Chyoa.createHtmlRecursive(debug, htmltext, node, multiplePages)
        else:
            htmltext = Chyoa.createHtmlBody(htmltext, node, multiplePages)
        htmltext.append("</body></html>")
        return htmltext

    def createHtmlRecursive(debug, htmltext, node, multiplePages):
        htmltext = Chyoa.createHtmlBody(htmltext, node, multiplePages)
        if node.value.follow:
            htmltext.append('<hr>')
            for child in node.children:
                htmltext = Chyoa.createHtmlRecursive(debug, htmltext, child, multiplePages)
        return htmltext

    def createHtmlBody(htmltext, node, multiplePages):
        if node.value.chapter_title:
            htmltext.append(f'<h2 id={str(node.value.id)} class="chapterheader">{node.value.chapter_title}')
        if node.value.author:
            htmltext.append(f" by {node.value.author}")
        htmltext.append(f"</h2><br>")
        if node.value.story_header2:
            htmltext.append(f'<h2 class="storyheader2">{node.value.story_header2}</h2>')
        if node.value.story_header1:
            htmltext.append(f'<h1 class="storyheader1">{node.value.story_header1}</h1>')
        htmltext.append('<hr>')
        htmltext.append(node.value.text)
        htmltext.append(f'<hr>')
        htmltext.append(f'<div class="question-header"><h2>{node.value.question}</h2></div>')
        htmltext.append('<div class="question-content">')
        if node.children:
            for child in node.children:
                if multiplePages == True:
                    htmltext.append(f'<div class="list-item"><a href="{child.value.filename}" class="anker-text">{child.value.linktext}</a></div>')
                else:
                    htmltext.append(f'<div class="list-item"><a href="#{child.value.id}" class="anker-text">{child.value.linktext}</a></div>')
        htmltext.append(f'<hr>')
        if node.value.parentFilename:
            if multiplePages == True:
                htmltext.append(f'<div class="list-item-previous"><a href="{node.value.parentFilename}" class="anker-text">Previous Chapter</a></div>')
            else:
                htmltext.append(f'<div class="list-item-previous"><a href="#{node.value.parentId}" class="anker-text">Previous Chapter</a></div>')
        if node.value.startSite:
            if multiplePages == True:
                htmltext.append(f'<div class="list-item-previous"><a href="{node.value.startSite}" class="anker-text">Start Over</a></div>')
            else:
                htmltext.append(f'<div class="list-item-previous"><a href="#" class="anker-text">Start Over</a></div>')
        if node.value.filenameMap and multiplePages == True:
            htmltext.append(f'<div class="list-item-previous"><a href="{node.value.filenameMap}" class="anker-text">Map</a></div>')
        htmltext.append("</div>")
        return htmltext

    def createHtmlHead(htmltext, node, multiplePages):
        htmltext.append("<!DOCTYPE html>")
        htmltext.append("<html><head><meta charset='utf-8'>")
        if multiplePages:
            htmltext.append(f"<title>{node.value.chapter_title} - {node.value.story_header2}</title>")
        else:
            htmltext.append(f"<title>{node.value.storyTitle}</title>")
        htmltext.append('<link rel="stylesheet" href="style.css">')
        htmltext.append("</head><body>")
        if node.value.storyImage:
            htmltext.append(f'<div class="cover"><img src="{node.value.storyImage}" alt="{node.value.storyTitle}" /></div>')
        if node.value.storyTitle:
            htmltext.append(f'<h1 class="storytitle">Story: {node.value.storyTitle}</h1>')
        return htmltext

    def createMapLinks(debug, node, htmltext, multiplePages, follow, level=0):
        linktext = node.value.linktext
        if not linktext:
            linktext = node.value.storyTitle
        style = "margin-left: 30px;"
        display = "display: block;"
        htmltext.append('<div class="node">')
        if follow == True:
            childrenlen = len(node.children)
            htmltext = Chyoa.createButton(htmltext, node.value.filename, node.value.id, node.value.chapter_title + " - " + linktext, multiplePages, (childrenlen>0))
            if childrenlen > 0:
                htmltext.append(f'<div class="children" style="{style}">')
            for child in node.children:
                htmltext = Chyoa.createMapLinks(debug, child, htmltext, multiplePages, node.value.follow, level + 1)
            if childrenlen > 0:
                htmltext.append('</div>')    
        htmltext.append('</div>')
        return htmltext

    def createButton(htmltext, url, id, linktext, multiplePages, showButton):
        htmltext.append(f'<div class="item">')
        if showButton:
            htmltext.append(f'<button class="toggle"> ▶ </button>')
            #htmltext.append(f'<button class="toggle"> ▼ </button>')
        if multiplePages == True:
            htmltext.append(f'<a href="{url}">{linktext}</a>')
        else:
            htmltext.append(f'<a href="#{id}">{linktext}</a>')
        htmltext.append(f'</div>')
        return htmltext

    def createJavascript(htmltext):
        htmltext.append('<script>')
        htmltext.append('document.addEventListener("DOMContentLoaded", function () {')
        htmltext.append('    const toggles = document.querySelectorAll(".toggle");')
        htmltext.append('    const toggleAllBtn = document.getElementById("toggleAll");')
        htmltext.append('    const childrenLists = document.querySelectorAll(".children");')
        htmltext.append("    let allOpen = sessionStorage.getItem('chyoa-scraper-document.title');")
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
        htmltext.append("        sessionStorage.setItem('chyoa-scraper-document.title', allOpen);")
        htmltext.append('    });')
        htmltext.append('    function updateArrow(button, isOpen) {')
        htmltext.append('        button.textContent = isOpen')
        htmltext.append('            ? button.textContent.replace("▶", "▼")')
        htmltext.append('            : button.textContent.replace("▼", "▶");')
        htmltext.append('    }')
        htmltext.append('    toggleAllBtn.click(); ')
        htmltext.append('});')
        htmltext.append('</script>')
        return htmltext

    def createMap(debug, foldername, filename, node, multiplePages, htmlSiteOverride):
        htmltext = []
        if debug:
            print(f"Map-filename: {filename}")
            print(f"Map-foldername: {foldername}")
        htmltext = Chyoa.createMapHead(htmltext, node)
        if node.value.storyTitle and multiplePages == True:
            htmltext.append(f'<h1 class="storytitle">Story: {node.value.storyTitle}</h1>')
        htmltext = Chyoa.createMapBody(debug, htmltext, node, multiplePages)
        htmltext.append("</body></html>")
        save(debug, foldername, filename, node, htmltext, htmlSiteOverride)

    def createMapBody(debug, htmltext, node, multiplePages):
        htmltext.append(f'<div class="storyurl"><a href="{node.value.url}">Original Url: {node.value.url}</a></div>')
        htmltext.append(f'<hr>')
        htmltext.append(f'<h2>Content</h2>')
        htmltext.append(f'<hr>')
        htmltext.append('<div class="toggleButton"><button id="toggleAll">Expand all</button></div>')
        style = "margin-left: 30px;"
        htmltext.append(f'<div class="map" style="{style}">')
        htmltext = Chyoa.createMapLinks(debug, node, htmltext, multiplePages, True)
        htmltext.append('</div>')
        return htmltext

    def createMapHead(htmltext, node):
        htmltext.append("<!DOCTYPE html>")
        htmltext.append("<html><head><meta charset='utf-8'>")
        htmltext.append(f"<title>{node.value.storyTitle}</title>")
        htmltext.append('<link rel="stylesheet" href="style.css">')
        htmltext = Chyoa.createJavascript(htmltext)
        htmltext.append('</head><body>')
        return htmltext
