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
        self.personal_settings_file = f"{self.config.foldername_personal_settings}/{self.config.foldername_story_with_id}_{self.config.suffix_personal_settings}.json"
        if self.debug:
            print(f"personal settings file: '{self.personal_settings_file}'")

    def read_personal_settings(self):
        """read json file with personal settings"""

        if not self.personal_settings_file:
            return None
        if not os.path.exists(self.personal_settings_file):
            if not self.config.create_always_personal_settings_file:
                return None, None
            if not self.config.personal_settings_default_file:
                return None, None
            default_filepath = f"{self.config.personal_settings_default_file}_{self.config.suffix_personal_settings}.json"
            if os.path.isfile(default_filepath):
                shutil.copy(default_filepath, self.personal_settings_file)
            else:
                print(f"              default personal settings file not found: {default_filepath}")
                return None, None

        try:
            with open(self.personal_settings_file, 'r', encoding='utf-8-sig') as f:
                content = json.load(f)
                personal_tags = content.get("personal_tags", {})
                images_replacement_url = content.get("images", {})
                return personal_tags, images_replacement_url
        except Exception as e:
            print(f"personal tags file '{self.personal_settings_file}' can not loaded '{e}'")
            return None, None

    def write_personal_settings_with_ignore_url(self, invalid_image_url, replacement_url = ""):
        """write json file with personal settings and image ignore url"""

        if not self.personal_settings_file:
            print("              personal not exists, can not write json tags...")
            return None

        try:
            with open(self.personal_settings_file, 'r', encoding='utf-8-sig') as f:
                content = json.load(f)

            content.setdefault("images", []).append({
                "invalid_image_url": invalid_image_url,
                "replacement_url": replacement_url
            })

            # save Json
            with open(self.personal_settings_file, "w", encoding="utf-8-sig") as f:
                json.dump(content, f, ensure_ascii=False, indent=4)
            return None
        except Exception as e:
            print(f"personal tags file '{self.personal_settings_file}' can not loaded '{e}'")
            return None