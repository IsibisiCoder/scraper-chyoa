# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
from enum import StrEnum

class Llm_system(StrEnum):
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value.lower() in (item.value.lower() for item in cls)

    @classmethod
    def from_string(cls, value: str):
        for item in cls:
            if item.value.lower() == value.lower():
                return item
        raise ValueError(f"'{value}' is not a valid value for {cls.__name__}")


class Config:
    def __init__(
            self,
            version,
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
            show_skip_loading_image,
            show_chapter_name_loading_story,
            directory_exists_skip_download,
            waiting_time_between_downloads_of,
            waiting_time_between_downloads_until,
            http_header_user_agent,
            http_header_referer,
            http_img_alt_text,
            http_img_alt_text_cover,
            images_ignore_domain_url,
            foldername_personal_settings,
            suffix_personal_settings,
            create_always_personal_settings_file,
            personal_settings_default_file,
            create_epub=False,
            ignore_links=None,
            image_prefix=False,
            include_url_in_epub=True,
            include_meta_in_epub=True,
            translate=False,
            translate_language="",
            llm_system = Llm_system.OLLAMA,
            llm_model = "",
            llm_question = "",
            llm_api = ""):
        self.version = version
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
        self.show_skip_loading_image = show_skip_loading_image
        self.show_chapter_name_loading_story = show_chapter_name_loading_story

        self.create_epub = create_epub
        self.ignore_links = ignore_links if ignore_links is not None else []
        self.image_prefix = image_prefix
        self.include_url_in_epub = include_url_in_epub
        self.include_meta_in_epub = include_meta_in_epub
        self.directory_exists_skip_download = directory_exists_skip_download

        # personal tags
        self.foldername_personal_settings = foldername_personal_settings
        self.suffix_personal_settings = suffix_personal_settings
        self.create_always_personal_settings_file = create_always_personal_settings_file
        self.personal_settings_default_file = personal_settings_default_file

        self.waiting_time_between_downloads_of = waiting_time_between_downloads_of
        self.waiting_time_between_downloads_until = waiting_time_between_downloads_until
        self.images_ignore_domain_url = images_ignore_domain_url

        # http headers and images
        self.http_header_user_agent = http_header_user_agent
        self.http_header_referer = http_header_referer
        self.http_img_alt_text = http_img_alt_text
        self.http_img_alt_text_cover = http_img_alt_text_cover

        # translate
        self.translate = translate
        self.translate_language = translate_language
        self.llm_model = llm_model
        self.llm_question = llm_question
        self.llm_api = llm_api

        try:
            self.llm_system = Llm_system.from_string(llm_system)
        except ValueError as e:
            self.llm_system = Llm_system.OLLAMA
