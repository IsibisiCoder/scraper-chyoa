"""class to read personal tags of the chapter or story"""
# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder

import os
import json

class PersonalTags:
    """class with personal tags of the chapter or story"""
    def __init__(self, debug, config):
        self.debug = debug
        self.config = config

    def read_personal_tags(self, foldername):
        """read josn file with personal tags"""

        personal_tags_file = f"{self.config.foldername_personal_tags}/{foldername}_{self.config.suffix_personal_tags}.json"
        if self.debug:
            print(f"personal tags file: '{personal_tags_file}'")
        if not personal_tags_file:
            return None
        if not os.path.exists(personal_tags_file):
            return None

        try:
            with open(personal_tags_file, 'r', encoding='utf-8-sig') as f:
                content = json.load(f)
                personal_tags = content.get("personal_tags", {})
                return personal_tags
        except Exception as e:
            print(f"personal tags file '{personal_tags_file}' can not loaded '{e}'")
            return None
