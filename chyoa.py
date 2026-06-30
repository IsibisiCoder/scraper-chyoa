import sys
import os
import requests
import re
from story import Story
from node import Node
from util import get_unique_filename, download_image, save, copyCss
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
import uuid
class parser:
    def getStories(debug, session, folder, imageFolderNameOnly, urls, question_class, chapter_class, htmltag, oneHtmlSite, htmlSiteOverride, recursionlimit, createEpub=False):
        for idx, url in enumerate(urls, 1):
            try:
                print(f"load {url} ...")

                soup = parser.getSoup(debug, session, url)
                story_header1, story_header2, foldername = parser.scrape_storytitle(debug, soup)
                if len(foldername) > 100:
                    foldername = foldername[0:100]
                story_title = story_header2
                filenameMap = foldername+"-map.html"
                
                # create folder
                folderPath = os.path.join(folder, foldername)
                counter = 1
                while os.path.exists(folderPath):
                    folderPath = f"{folderPath}_{counter}"
                    if debug:
                        print(f"folderPath: {folderPath}")
                    counter += 1
                os.makedirs(folderPath, exist_ok=True)

                imageFolderPath = os.path.join(folderPath, imageFolderNameOnly)
                os.makedirs(imageFolderPath, exist_ok=True)

                id = 1

                chapter_title, ignore1, ignore2, author = parser.scrape_title_author(debug, soup)
                filename = parser.createFilename(debug, story_header2, story_title, folder)
                question = parser.scrape_question(debug, soup)
                story = parser.scrape_content(debug, soup, htmltag, chapter_class, imageFolderPath, imageFolderNameOnly)
                imageFilename = parser.scrape_StoryCover(debug, soup, imageFolderPath, imageFolderNameOnly)
                
                startsite = filename;

                root_link = Story(
                    id="1",
                    url=url,
                    linktext="",
                    follow=True,
                    story_title=story_title,
                    story_image=imageFilename,
                    chapter_title=chapter_title,
                    story_header1=story_header1,
                    story_header2=story_header2,
                    question=question,
                    filename=filename,
                    parentFilename="",
                    parentId="",
                    startsite=startsite,
                    mapFilename=filenameMap,
                    author=author,
                    text=story
                )
                root = Node(root_link)

                sys.setrecursionlimit(recursionlimit)
                id = parser.getlinksfromsite(debug, root, root, session, folder, url, question_class, chapter_class, htmltag, id, filename, id, story_title, filename, imageFolderPath, imageFolderNameOnly)

                if debug:
                    print(f"Count: {id}")
                    parser.getAllLinks(debug, root)
                copyCss(debug, folderPath)
                parser.saveStories(debug, folderPath, root, oneHtmlSite, htmlSiteOverride)
                if oneHtmlSite == False:
                    parser.createMap(debug, folderPath, filenameMap, root, oneHtmlSite, htmlSiteOverride)
                if createEpub:
                    parser.saveEpub(debug, folderPath, story_title, root, imageFolderPath)

            except requests.RequestException as e:
                print(f"Error loading {url}: {e}")

    def getSoup(debug, session, url):
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def getlinksfromsite(debug, root, node, session, folder, url, question_class, chapter_class, htmltag, id, parentFilename, parentId, story_title, startsite, imageFolderPath, imageFolderNameOnly):
        soup = parser.getSoup(debug, session, url)
        linksfromsite, id = parser.scrape_links(debug, session, soup, root, question_class, chapter_class, htmltag, id, parentFilename, parentId, story_title, startsite, folder, imageFolderPath, imageFolderNameOnly)
        for link in linksfromsite:
            currentNode = Node(link)
            node.add_child(currentNode)
            if link.follow == True:
                id = parser.getlinksfromsite(debug, root, currentNode, session, folder, link.url, question_class, chapter_class, htmltag, id, currentNode.value.filename, currentNode.value.id, story_title, startsite, imageFolderPath, imageFolderNameOnly)
            else:
                print(f"Url: {link.url} / Parent {parentFilename} exists and links from url do not follow!")
        return id

    def scrape_links(debug, session, soup, root, question_class, chapter_class, htmltag, id, parentFilename, parentId, story_title, startsite, folderPath, imageFolderPath, imageFolderNameOnly):
        all_links = []
        content_navigable_all = soup.find_all(htmltag, class_=question_class)
        # anker-tags
        for c in content_navigable_all:
            for a_tag in c.find_all("a"):
                a_href = a_tag.get("href")
                a_text = a_tag.get_text(strip=True)
                
                # Filter out UI buttons for adding/linking chapters
                if "/new?type=" in a_href or "Add a new chapter" in a_text or "Write a chapter" in a_text or "Link a chapter" in a_text:
                    continue
                
                if True: # keep existing indentation for the rest of the block
                    if debug:
                        print(f"link {a_href}")
                        print(f"text {a_text}")
                        print(f"parent {parentFilename}")
                    #    print(f"story_title {story_title}")
                    id = id + 1
                    soup_current_site = parser.getSoup(debug, session, a_href)
                    chapter_title, story_header1, story_header2, author = parser.scrape_title_author(debug, soup_current_site)
                    filename = str(id)+"-"+chapter_title.strip()+"-"+parser.createFilename(debug, story_header1, story_title, folderPath).strip()
                    question = parser.scrape_question(debug, soup_current_site)
                    containsUrl, containsNode = Node.contains(root, a_href)
                    if containsUrl == True:
                        follow = False
                        current_link = Story(containsNode.value.id, containsNode.value.url, containsNode.value.linktext, follow, containsNode.value.story_title, "", containsNode.value.chapter_title, containsNode.value.story_header1, containsNode.value.story_header2, containsNode.value.question, containsNode.value.filename, containsNode.value.parentFilename, containsNode.value.parentId, startsite, root.value.mapFilename, containsNode.value.author, containsNode.value.text)
                        all_links.append(current_link)
                    if containsUrl == False:
                        story = ""
                        follow = True
                        story = parser.scrape_content(debug, soup_current_site, htmltag, chapter_class, imageFolderPath, imageFolderNameOnly)
                        current_link = Story(id, a_href, a_text, follow, story_title, "", chapter_title, story_header1, story_header2, question, filename, parentFilename, parentId, startsite, root.value.mapFilename, author, story)
                        all_links.append(current_link)
        return all_links, id

    def getAllLinks(debug, node, level=0):
        if debug:
            print("  " * level + str(node.value.linktext))
            print("  " * level + str(node.value.url))
            print("  " * level + str(node.value.story_title))
            print("  " * level + str(node.value.chapter_title))
            print("  " * level + str(node.value.filename))
            #print("  " * level + str(node.value.text))
        for child in node.children:
            if child.value.follow == True:
                parser.getAllLinks(debug, child, level + 1)

    def saveStories(debug, foldername, node, oneHtmlSite, htmlSiteOverride):
        html = parser.createHtml(debug, node, oneHtmlSite)
        if debug:
            print(f"save Filename {node.value.filename} - {node.value.follow}")
        if oneHtmlSite == True or node.value.follow == True:
            save(debug, foldername, node.value.filename, node, html, htmlSiteOverride)
        if oneHtmlSite == False and node.value.follow == True:
            for child in node.children:
                parser.saveStories(debug, foldername, child, oneHtmlSite, htmlSiteOverride)

    def saveEpub(debug, folderPath, story_title, root, imageFolderPath):
        book = epub.EpubBook()
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(story_title)
        book.set_language('en')
        if root.value.author:
            book.add_author(root.value.author)

        # Get all nodes in a flat list
        all_nodes = []
        def _flatten(n):
            all_nodes.append(n)
            for c in n.children:
                if c.value.follow:
                    _flatten(c)
        _flatten(root)

        # Map node ids to epub chapters
        epub_chapters = {}
        for n in all_nodes:
            # use original HTML creation logic but modified for EPUB formatting
            c = epub.EpubHtml(title=n.value.chapter_title or story_title, file_name=f'chapter_{n.value.id}.xhtml', lang='en')
            htmltext = []
            htmltext.append("<html><head><title>{}</title></head><body>".format(n.value.chapter_title or story_title))
            if n.value.story_image and n == root:
                 # It's root, add cover image to book
                 cover_file = n.value.story_image
                 if cover_file and os.path.exists(os.path.join(folderPath, cover_file)):
                     with open(os.path.join(folderPath, cover_file), 'rb') as f:
                         book.set_cover(cover_file.replace('\\', '/'), f.read())
            
            if n.value.chapter_title:
                htmltext.append(f"<h2>{n.value.chapter_title}")
                if n.value.author:
                    htmltext.append(f" by {n.value.author}")
                htmltext.append("</h2>")
            
            if n.value.story_header2:
                htmltext.append(f"<h2>{n.value.story_header2}</h2>")
            if n.value.story_header1:
                htmltext.append(f"<h1>{n.value.story_header1}</h1>")
            htmltext.append("<hr/>")
            htmltext.append(n.value.text)
            htmltext.append("<hr/>")
            htmltext.append(f"<h3>{n.value.question}</h3>")
            
            # Choice Links
            htmltext.append("<div>")
            for child in n.children:
                htmltext.append(f'<div><a href="chapter_{child.value.id}.xhtml">{child.value.linktext}</a></div>')
            htmltext.append("</div>")
            
            htmltext.append("</body></html>")
            
            c.content = "".join(htmltext)
            book.add_item(c)
            epub_chapters[n.value.id] = c

        # Add images
        if os.path.exists(imageFolderPath):
            for img_file in os.listdir(imageFolderPath):
                img_path = os.path.join(imageFolderPath, img_file)
                if os.path.isfile(img_path):
                    with open(img_path, 'rb') as f:
                        img_item = epub.EpubImage()
                        rel_path = os.path.relpath(img_path, folderPath).replace('\\', '/')
                        img_item.file_name = rel_path
                        img_item.content = f.read()
                        book.add_item(img_item)
        
        # Define Spine and TOC
        book.spine = ['nav']
        for n in all_nodes:
            book.spine.append(epub_chapters[n.value.id])

        def build_toc(node):
            toc_entry = epub_chapters[node.value.id]
            children_toc = []
            for child in node.children:
                if child.value.follow:
                    children_toc.append(build_toc(child))
            
            if children_toc:
                return (toc_entry, children_toc)
            return toc_entry
            
        book.toc = [build_toc(root)]
            
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        epub_filename = os.path.join(folderPath, f"{root.value.filename}.epub")
        epub.write_epub(epub_filename, book, {})
        if debug:
            print(f"EPUB created: {epub_filename}")

    def scrape_storytitle(debug, soup):
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

    def scrape_images(debug, element, imageFolderPath, imageFolderNameOnly, soup_context):
        for img in element.find_all("img"):
            img_src = img.get("src")
            if img_src:
                if debug:
                    print(f'image-src: {img_src}')
                filenameImage = download_image(debug, "chapter-image", imageFolderPath, imageFolderNameOnly, img_src)
                if filenameImage:
                    if debug:
                        print(f'replace with: {filenameImage}')
                    img['src'] = filenameImage.replace('\\', '/')
                    # Apply responsive styling for eReaders
                    img['style'] = "max-width: 100%; height: auto; display: block;"
                    # Insert the requested prefix before the image
                    prefix_span = soup_context.new_tag("div")
                    prefix_span.string = "illustration-"
                    img.insert_before(prefix_span)
        return element
    def scrape_StoryCover(debug, soup, imageFolderPath, imageFolderNameOnly):
        filenameImage = ""
        html = ""
        cover = soup.find('div', class_='cover')
        if cover:
            img = cover.find('img')
            img_src = img.get("src")
            if img_src:
                if debug:
                    print(f'cover image-src: {img_src}')
                filenameImage = download_image(debug, "story", imageFolderPath, imageFolderNameOnly, img_src)
        return filenameImage

    def scrape_content(debug, soup, htmltag, chapter_class, imageFolderPath, imageFolderNameOnly):
        content_navigable_all = soup.find_all(htmltag, class_=chapter_class)
        if not content_navigable_all:
            return "<!-- no content found -->"
        
        chapter_element = content_navigable_all[0]
        # Modify images in the tree before prettifying
        parser.scrape_images(debug, chapter_element, imageFolderPath, imageFolderNameOnly, soup)
        
        content = chapter_element.prettify()
        return content
        #    print(f"Story: {content}")
        return content

    def createHtml(debug, node, oneHtmlSite):
        htmltext = []
        htmltext = parser.createHtmlHead(htmltext, node, oneHtmlSite)
        htmltext = parser.createJavascript(htmltext)
        if oneHtmlSite == True:
            htmltext = parser.createMapBody(debug, htmltext, node, oneHtmlSite)
            htmltext = parser.createHtmlRecursive(debug, htmltext, node, oneHtmlSite)
        else:
            htmltext = parser.createHtmlBody(htmltext, node, oneHtmlSite)
        htmltext.append("</body></html>")
        return htmltext

    def createHtmlRecursive(debug, htmltext, node, oneHtmlSite):
        htmltext = parser.createHtmlBody(htmltext, node, oneHtmlSite)
        if node.value.follow == True:
            htmltext.append('<hr>')
            for child in node.children:
                htmltext = parser.createHtmlRecursive(debug, htmltext, child, oneHtmlSite)
        return htmltext

    def createHtmlBody(htmltext, node, oneHtmlSite):
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
                if oneHtmlSite == False:
                    htmltext.append(f'<div class="list-item"><a href="{child.value.filename}" class="anker-text">{child.value.linktext}</a></div>')
                else:
                    htmltext.append(f'<div class="list-item"><a href="#{child.value.id}" class="anker-text">{child.value.linktext}</a></div>')
        htmltext.append(f'<hr>')
        if node.value.parentFilename:
            if oneHtmlSite == False:
                htmltext.append(f'<div class="list-item-previous"><a href="{node.value.parentFilename}" class="anker-text">Previous Chapter</a></div>')
            else:
                htmltext.append(f'<div class="list-item-previous"><a href="#{node.value.parentId}" class="anker-text">Previous Chapter</a></div>')
        if node.value.startsite:
            if oneHtmlSite == False:
                htmltext.append(f'<div class="list-item-previous"><a href="{node.value.startsite}" class="anker-text">Start Over</a></div>')
            else:
                htmltext.append(f'<div class="list-item-previous"><a href="#" class="anker-text">Start Over</a></div>')
        if node.value.mapFilename and oneHtmlSite == False:
            htmltext.append(f'<div class="list-item-previous"><a href="{node.value.mapFilename}" class="anker-text">Map</a></div>')
        htmltext.append("</div>")
        return htmltext

    def createHtmlHead(htmltext, node, oneHtmlSite):
        htmltext.append("<!DOCTYPE html>")
        htmltext.append("<html><head><meta charset='utf-8'>")
        if oneHtmlSite:
            htmltext.append(f"<title>{node.value.story_title}</title>")
        else:
            htmltext.append(f"<title>{node.value.chapter_title}</title>")
        htmltext.append('<link rel="stylesheet" href="style.css">')
        htmltext.append("</head><body>")
        if node.value.story_image:
            htmltext.append(f'<div class="cover"><img src="{node.value.story_image}" alt="{node.value.story_title}" /></div>')
        if node.value.story_title:
            htmltext.append(f'<h1 class="storytitle">Story: {node.value.story_title}</h1>')
        return htmltext

    def createMapLinks(debug, node, htmltext, oneHtmlSite, follow, level=0):
        linktext = node.value.linktext
        if not linktext:
            linktext = node.value.story_title
        style = "margin-left: 30px;"
        display = "display: block;"
        htmltext.append('<div class="node">')
        if follow == True:
            childrenlen = len(node.children)
            htmltext = parser.createButton(htmltext, node.value.filename, node.value.id, node.value.chapter_title + " - " + linktext, oneHtmlSite, (childrenlen>0))
            if childrenlen > 0:
                htmltext.append(f'<div class="children" style="{style}">')
            for child in node.children:
                htmltext = parser.createMapLinks(debug, child, htmltext, oneHtmlSite, node.value.follow, level + 1)
            if childrenlen > 0:
                htmltext.append('</div>')    
        htmltext.append('</div>')
        return htmltext

    def createButton(htmltext, url, id, linktext, oneHtmlSite, showButton):
        htmltext.append(f'<div class="item">')
        if showButton:
            htmltext.append(f'<button class="toggle"> ▶ </button>')
            #htmltext.append(f'<button class="toggle"> ▼ </button>')
        if oneHtmlSite == True:
            htmltext.append(f'<a href="#{id}">{linktext}</a>')
        else:
            htmltext.append(f'<a href="{url}">{linktext}</a>')
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

    def createMap(debug, foldername, filename, node, oneHtmlSite, htmlSiteOverride):
        htmltext = []
        if debug:
            print(f"Map-filename: {filename}")
            print(f"Map-foldername: {foldername}")
        htmltext = parser.createMapHead(htmltext, node)
        if node.value.story_title and oneHtmlSite == False:
            htmltext.append(f'<h1 class="storytitle">Story: {node.value.story_title}</h1>')
        htmltext = parser.createMapBody(debug, htmltext, node, oneHtmlSite)
        htmltext.append("</body></html>")
        save(debug, foldername, filename, node, htmltext, htmlSiteOverride)

    def createMapBody(debug, htmltext, node, oneHtmlSite):
        htmltext.append(f'<div class="storyurl"><a href="{node.value.url}">Original Url: {node.value.url}</a></div>')
        htmltext.append(f'<hr>')
        htmltext.append(f'<h2>Content</h2>')
        htmltext.append(f'<hr>')
        htmltext.append('<div class="toggleButton"><button id="toggleAll">Expand all</button></div>')
        style = "margin-left: 30px;"
        htmltext.append(f'<div class="map" style="{style}">')
        htmltext = parser.createMapLinks(debug, node, htmltext, oneHtmlSite, True)
        htmltext.append('</div>')
        return htmltext

    def createMapHead(htmltext, node):
        htmltext.append("<!DOCTYPE html>")
        htmltext.append("<html><head><meta charset='utf-8'>")
        htmltext.append(f"<title>{node.value.story_title}</title>")
        htmltext.append('<link rel="stylesheet" href="style.css">')
        htmltext = parser.createJavascript(htmltext)
        htmltext.append('</head><body>')
        return htmltext
