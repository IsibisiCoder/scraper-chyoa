# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
class Config:
    def __init__(self, login, questionClass, contentClass, chapterHtmltag, recursionLimit, storyNameWithId, multiplePages, wholeStoryOnePage, overrideHtmlSites, folderpathStories, foldernameImage, show_error_loading_image, show_chapter_name_loading_story, create_epub=False, ignore_links=None):
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

        self.show_error_loading_image = show_error_loading_image
        self.show_chapter_name_loading_story = show_chapter_name_loading_story
        
        self.create_epub = create_epub
        self.ignore_links = ignore_links if ignore_links is not None else []
