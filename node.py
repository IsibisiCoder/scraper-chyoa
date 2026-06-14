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
        if node.value.url == url:
            #if debug:
            #    print(f'Root: {node.value.id} / {node.value.url}-{url}')
            return True, node
        for child in node.children:
            #if debug:
            #    print(f'Child: {child.value.url}-{url}')
            containsUrl, containsNode = Node.contains(child, url)
            if containsUrl:
                #if debug:
                #    print(f'Child: true => {url}')
                return True, containsNode
        #if debug:
        #    print(f'Child: false => {url}')
        return False, None