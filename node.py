# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

    def contains(node, url):
        if node.value.url == url and not node.value.redirect:
            #if debug:
            #    print(f'Root: {node.value.id} / {node.value.url}-{url}')
            return True, node
        for child in node.children:
            #if debug:
            #    print(f'Child: {child.value.url}-{url}')
            contains_url, contains_node = Node.contains(child, url)
            if contains_url:
                #if debug:
                #    print(f'Child: true => {url}')
                return True, contains_node
        #if debug:
        #    print(f'Child: false => {url}')
        return False, None

    def check_all_chapters(root, node):
        for chapter in node.children:
            if not chapter.value.redirect:
                Node.check_all_chapters(root, chapter)
            else:
                contains_url, contains_node = Node.contains(root, chapter.value.url)
                if contains_url:
                    contains_url, contains_node = Node.contains(root, chapter.value.url)
                    chapter.value.id = contains_node.value.id
                    chapter.value.story_header1 = contains_node.value.story_header1
                    chapter.value.story_header2 = contains_node.value.story_header2
                    chapter.value.question = contains_node.value.question
                    chapter.value.filename = contains_node.value.filename
                    chapter.value.parent_filename = contains_node.value.parent_filename
                    chapter.value.parent_id = contains_node.value.parent_id
                    chapter.value.text = contains_node.value.text
        return
