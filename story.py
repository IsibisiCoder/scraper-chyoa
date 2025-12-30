class Story:
    def __init__(self, id, url, linktext, follow, story_title, story_image, chapter_title, story_header1, story_header2, question, filename, parentFilename, parentId, startsite, mapFilename, author, text):
        self.id = id
        self.url = url
        self.linktext = linktext
        self.follow=follow
        self.story_title=story_title
        self.story_image=story_image
        self.chapter_title = chapter_title
        self.story_header1 = story_header1
        self.story_header2 = story_header2
        self.question = question
        self.filename = filename
        self.parentFilename = parentFilename
        self.parentId = parentId
        self.startsite=startsite
        self.mapFilename=mapFilename
        self.author = author
        self.text = text
