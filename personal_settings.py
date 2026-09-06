"""class to read personal settings of the chapter or story"""
# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder

import os
import shutil
import json

class PersonalSettings:
    """class with personal settings of the chapter or story"""
    def __init__(self, debug, config):
        self.debug = debug
        self.config = config

    def read_personal_settings(self):
        """read josn file with personal settings"""

        personal_settings_file = f"{self.config.foldername_personal_settings}/{self.config.foldername_story_with_id}_{self.config.suffix_personal_settings}.json"
        if self.debug:
            print(f"personal settings file: '{personal_settings_file}'")
        if not personal_settings_file:
            return None
        if not os.path.exists(personal_settings_file):
            if not self.config.create_always_personal_settings_file:
                return None, None
            if not self.config.personal_settings_default_file:
                return None, None
            default_filepath = f"{self.config.personal_settings_default_file}_{self.config.suffix_personal_settings}.json"
            if os.path.isfile(default_filepath):
                shutil.copy(default_filepath, personal_settings_file)
            else:
                print(f"              default personal settings file not found: {default_filepath}")
                return None, None

        try:
            with open(personal_settings_file, 'r', encoding='utf-8-sig') as f:
                content = json.load(f)
                personal_tags = content.get("personal_tags", {})
                images_replacement_url = content.get("images", {})
                return personal_tags, images_replacement_url
        except Exception as e:
            print(f"personal tags file '{personal_settings_file}' can not loaded '{e}'")
            return None, None
