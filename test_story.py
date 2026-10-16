import pytest

from story import Story

class TestStory:
    def test_set(self):
        story = Story("","","","","","","","","","","","","","","")
        story.set("story_image", "chapter_title", "question", "filename", "parent_filename", "parent_id", "startsite", "text")
        assert story.story_image == "story_image"