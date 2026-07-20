# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder

import os
#from meta import Meta
#from config import Config

class Story:
    def __init__(
            self,
            config,
            story_id,
            url,
            meta,
            linktext,
            follow,
            story_title,
            story_header1,
            story_header2,
            filename_map,
            filename_total,
            personal_tags):
        self.config = config
        self.id = story_id
        self.url = url
        self.meta = meta
        self.linktext = linktext
        self.follow=follow
        self.story_title = story_title
        self.story_header1 = story_header1
        self.story_header2 = story_header2
        self.published_time = ""
        self.modified_time = ""
        self.folderpath_story = ""
        self.foldername_story = ""
        self.filename_map = filename_map
        self.filename_total = filename_total
        self.personal_tags = personal_tags
        self.image_folderpath  = ""
        self.chapter_title = ""
        self.question = ""
        self.filename = ""
        self.parent_filename = ""
        self.parent_id = ""
        self.text = ""
        self.start_site = ""
        self.story_image = ""
        self.created = ""


    def set(self, story_image, chapter_title, question, filename, parent_filename, parent_id, startsite, text):
        self.chapter_title = chapter_title
        self.question = question
        self.filename = filename
        self.parent_filename = parent_filename
        self.parent_id = parent_id
        self.text = text
        self.start_site = startsite
        self.story_image = story_image


    def create_folder(self, foldername_story):
        folderpath_story = os.path.join(self.config.folderpath_stories, foldername_story)
        counter = 1
        while os.path.exists(folderpath_story):
            folderpath_story = f"{folderpath_story}_{counter}"
            counter += 1
        os.makedirs(folderpath_story, exist_ok=True)
        self.folderpath_story = folderpath_story
        self.foldername_story = foldername_story

    def check_folder_if_exists(self, foldername_story):
        folderpath_story = os.path.join(self.config.folderpath_stories, foldername_story)
        return os.path.exists(folderpath_story)

    def create_folder_image(self):
        image_folderpath = os.path.join(self.folderpath_story, self.config.foldername_image)
        os.makedirs(image_folderpath, exist_ok=True)
        self.image_folderpath = image_folderpath
