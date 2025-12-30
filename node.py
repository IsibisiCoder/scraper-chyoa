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
            #print(f'Root: {node.value.id} / {node.value.url}-{url}')
            return True, node
        for child in node.children:
            #print(f'Child: {child.value.url}-{url}')
            containsUrl, containsNode = Node.contains(child, url)
            if containsUrl:
                #print(f'Child: true => {url}')
                return True, containsNode
        #print(f'Child: false => {url}')
        return False, None