# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
class Config:
    def __init__(
            self,
            login,
            question_class,
            content_class,
            chapter_htmltag,
            recursion_limit,
            storyname_with_id,
            multiple_pages,
            whole_story_one_page,
            override_html_sites,
            folderpath_stories,
            foldername_image,
            show_error_loading_image,
            show_chapter_name_loading_story,
            directory_exists_skip_download,
            waiting_time_between_downloads_of,
            waiting_time_between_downloads_until,
            foldername_personal_tags,
            suffix_personal_tags):
        self.login = login
        self.question_class = question_class
        self.content_class = content_class
        self.chapter_htmltag = chapter_htmltag
        self.recursion_limit = recursion_limit
        self.multiple_pages = multiple_pages
        self.whole_story_one_page = whole_story_one_page
        self.override_html_sites = override_html_sites
        self.storyname_with_id = storyname_with_id

        # Foldername and path
        self.folderpath_stories = folderpath_stories
        self.foldername_image = foldername_image
        self.show_error_loading_image = show_error_loading_image
        self.show_chapter_name_loading_story = show_chapter_name_loading_story
        self.directory_exists_skip_download = directory_exists_skip_download

        # personal tags
        self.foldername_personal_tags = foldername_personal_tags
        self.suffix_personal_tags = suffix_personal_tags

        self.waiting_time_between_downloads_of = waiting_time_between_downloads_of
        self.waiting_time_between_downloads_until = waiting_time_between_downloads_until
