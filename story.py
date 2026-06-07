# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder

import os
from config import Config

class Story:
    def __init__(self, config, id, url, linktext, follow, storyTitle, story_header1, story_header2, filenameMap, filenameTotal):
        self.config = config
        self.id = id
        self.url = url
        self.linktext = linktext
        self.follow=follow
        self.storyTitle=storyTitle
        self.story_header1 = story_header1
        self.story_header2 = story_header2
        self.folderpathStory = ""
        self.foldernameStory = ""
        self.filenameMap = filenameMap
        self.filenameTotal = filenameTotal


    def set(self, storyImage, chapter_title, question, filename, parentFilename, parentId, startsite, author, text):
        self.chapter_title = chapter_title
        self.published_time = ""
        self.modified_time = ""
        self.question = question
        self.filename = filename
        self.parentFilename = parentFilename
        self.parentId = parentId
        self.author = author
        self.text = text
        self.startSite = startsite
        self.storyImage = storyImage


    def setStory(self, created, updated, genre, category, likes, startSite, storyTitle, storyImage, description):
        self.startSite = startSite
        self.storyTitle = storyTitle
        self.storyImage = storyImage
        self.created = created
        self.category = category
        self.likes = likes
        self.updated = updated
        self.description = description
        self.genre = genre

    def setFileAndFolder(self, mapFilename, base_filename, base_folderame):
        self.base_filename = ""

    def getFilename(self):
        return self.base_filename + ".html"

    def getFilenamePath(self):
        return self.base_filename + ".html"

    def createFolder(self, foldernameStory):
        folderpathStory = os.path.join(self.config.folderpathStories, foldernameStory)
        counter = 1
        while os.path.exists(folderpathStory):
            folderpathStory = f"{folderpathStory}_{counter}"
            counter += 1
        os.makedirs(folderpathStory, exist_ok=True)
        self.folderpathStory = folderpathStory
        self.foldernameStory = foldernameStory

    def createFolderImage(self):
        imageFolderPath = os.path.join(self.folderpathStory, self.config.foldernameImage)
        os.makedirs(imageFolderPath, exist_ok=True)
        self.imageFolderPath = imageFolderPath

    def getImageFolderPath(self, config):
        os.path.join(self.folderPath, config.imageFolder)
        pass