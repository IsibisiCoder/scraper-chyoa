class Links:
    def __init__(
            self,
            link_text,
            url):
        self.link_text = link_text
        self.url = url
        self.redirect = False

    def set_redirect(self, redirect, url):
        self.redirect = redirect
        self.url = url

class Chapter:
    def __init__(
            self,
            config,
            url,
            chapter_id,
            counter
        ):
        self.config = config
        self.chapter_id = chapter_id
        self.counter = counter
        self.url = url
        self.redirect = False
        self.links_checked = False
        self.links = []
        self.title = ""
        self.header1 = ""
        self.header2 = ""
        self.soup = None
        self.meta = None
        self.content = ""
        self.question = ""
        self.content = ""
        self.filename = ""
        self.parent_chapter_id = ""

    def set_content(self, soup, title, header1, header2, meta):
        self.soup = soup
        self.title = title
        self.header1 = header1
        self.header2 = header2
        self.meta = meta

    def set_header(self, title, header1, header2, meta):
        self.title = title
        self.header1 = header1
        self.header2 = header2
        self.meta = meta

    def add_link(self, link_text, url):
        link = Links(link_text, url)
        self.links.append(link)

    def set_links_checked(self, links_checked):
        self.links_checked = links_checked

    def set_redirect(self, redirect, url):
        for link in self.links:
            if link.url == url:
                link.set_redirect(redirect, url)

    def set_soup(self, soup):
        self.soup = soup

    def set_question(self, question):
        self.question = question

    def set_filename(self, filename):
        self.filename = filename