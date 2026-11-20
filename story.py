# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder

import os

class Story:
    def __init__(
            self,
            config,
            url):
        self.config = config
        self.url = url
        self.story_title = ""
        self.story_header1 = ""
        self.story_header2 = ""
        self.follow = True,
        self.redirect = False,
        self.published_time = ""
        self.modified_time = ""
        self.meta = ""
        self.folderpath_story = ""
        self.foldername_story = ""
        self.filename_map = ""
        self.filename_total = ""
        self.personal_settings = None
        self.personal_tags = None
        self.images_replacement_url = ""
        self.foldername_story_with_id = ""
        self.folderpath_image  = ""
        self.folderpath_personal_settings = ""
        self.foldername_images_shadow_copy = ""
        self.chapter_title = ""
        self.filename = ""
        self.parent_filename = ""
        self.parent_id = ""
        self.text = ""
        self.start_site = ""
        self.story_image = ""
        self.created = ""

    def set_header(self,
                   story_title,
                   story_header1,
                   story_header2):
        self.story_title = story_title
        self.story_header1 = story_header1
        self.story_header2 = story_header2

    def set_content(self,
            meta,
            foldername_story_with_id,
            filename_map,
            filename_total):
        self.meta = meta
        self.foldername_story_with_id = foldername_story_with_id
        self.filename_map = filename_map
        self.filename_total = filename_total

    def set_personal_settings(self, personal_settings, personal_tags, images_replacement_url):
        self.personal_settings = personal_settings
        self.personal_tags = personal_tags
        self.images_replacement_url = images_replacement_url

    def set(self, story_image, filename, startsite):
        self.story_image = story_image
        self.filename = filename
        self.start_site = startsite


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
        self.folderpath_image = image_folderpath

    def create_folder_images_shadow_copy(self):
        foldername_images_shadow_copy = self.config.foldername_images_shadow_copy
        os.makedirs(foldername_images_shadow_copy, exist_ok=True)
        self.foldername_images_shadow_copy = foldername_images_shadow_copy

    #def create_folder_personal_settings(self, foldername_story):
    #    self.folderpath_personal_settings = os.path.join(self.config.foldername_personal_settings, foldername_story)
    #    os.makedirs(self.config.foldername_personal_settings, exist_ok=True)
    #    os.makedirs(self.folderpath_personal_settings, exist_ok=True)
