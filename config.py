# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
class Config:
    def __init__(self, login, questionClass, contentClass, chapterHtmltag, recursionLimit, storyNameWithId, multiplePages, wholeStoryOnePage, overrideHtmlSites, folderpathStories, foldernameImage):
        self.login = login
        self.questionClass = questionClass
        self.contentClass = contentClass
        self.chapterHtmltag = chapterHtmltag
        self.recursionLimit = recursionLimit
        self.multiple_pages = multiplePages
        self.whole_story_one_page = wholeStoryOnePage
        self.overrideHtmlSites = overrideHtmlSites
        self.storyNameWithId = storyNameWithId,

        # Foldername and path
        self.folderpathStories = folderpathStories
        self.foldernameImage = foldernameImage


