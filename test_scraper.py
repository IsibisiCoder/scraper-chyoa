import pytest
import json

from config import Config
from scraper import read_config

class TestScraper:
    def test_read_config(self):
        version = "scraper-chyoa V1.3.1"
        config_file = {
            "question_class": "question-content",
            "chapter_class": "chapter-content",
            "login": {
                "login_url": "https://chyoa.com/auth/login",
                "username": "user",
                "password": "password"
            },
            "http_header": {},
            "personal_settings": {
                "suffix_personal_settings": "mytags"
            },
            "epub": {},
            "translation": {},
            "image": {}
        }
        fake_json_config_file = json.dumps(config_file, indent=4)
        config: Config = read_config(fake_json_config_file, version)
        assert config.question_class == "question-content"
        assert config.suffix_personal_settings == "mytags"

