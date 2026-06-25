import regex as re
from .node import MarkdownNode

class MarkdownTree:
    HEADER_REGEX = re.compile(r"^(#{1,6})[ \t]+(.+)$", re.MULTILINE)

    def __init__(self):
        self.root = MarkdownNode(0, "ROOT")

    def parse(self, markdown_text: str):
        positions = []
        for match in self.HEADER_REGEX.finditer(markdown_text):
            positions.append(
                (
                    match.start(),
                    match.end(),
                    len(match.group(1)),
                    match.group(2).strip(),
                )
            )
        if not positions:
            self.root.add_content(markdown_text)
            return

        nodes = []
        for idx, (start, end, level, title) in enumerate(positions):
            start_of_next = None
            if idx < len(positions) - 1:
                start_of_next = positions[idx+1][0]
            content = markdown_text[end:start_of_next].strip("\n")
            nodes.append((level, title, content))

        stack = [self.root]
        for level, title, content in nodes:
            if title is not None:
                node = MarkdownNode(level, title)
                while len(stack) > level:
                    stack.pop()
                stack[-1].add_child(node)
                stack.append(node)
                if content:
                    node.add_content(content)
            else:
                if content:
                    stack[-1].add_content(content)

    def find_node_by_path(self, path: str) -> MarkdownNode | None:
        parts = path.split(".")
        current_nodes = [self.root]
        for part in parts:
            next_level_nodes = []
            for node in current_nodes:
                found = None
                for child in node.children:
                    if child.title == part:
                        found = child
                        break
                if found:
                    next_level_nodes = [found]
                    break
            if not next_level_nodes:
                return None
            current_nodes = next_level_nodes
        return current_nodes[0] if current_nodes else None

    def remove_section(self, path: str) -> bool:
        node = self.find_node_by_path(path)
        if node and node.parent:
            node.parent.remove_child(node)
            return True
        return False

    def add_section(
        self, parent_path: str, title: str, content=""
    ) -> MarkdownNode | None:
        if parent_path in ("", "ROOT"):
            parent_node = self.root
        else:
            parent_node = self.find_node_by_path(parent_path)

        if parent_node is None:
            return None

        new_level = parent_node.level + 1
        new_node = MarkdownNode(new_level, title)
        if content:
            new_node.add_content(content)
        parent_node.add_child(new_node)
        return new_node

    def dump(self) -> str:
        return self.root.dump()

    def visualize(self):
        self.root.print_tree()

    def attach_subtree(
        self,
        target_path: str,
        source_tree: "MarkdownTree",
        source_path: str | None = None,
        max_level: int = 6,
    ):
        # Resolve parent in destination tree
        if target_path in ("", "ROOT"):
            parent = self.root
        else:
            parent = self.find_node_by_path(target_path)
        if parent is None:
            return []

        # Determine source nodes to copy
        if source_path in (None, "", "ROOT"):
            source_nodes = source_tree.root.children
            per_node = True
        else:
            node = source_tree.find_node_by_path(source_path)
            if node is None or node.level == 0:
                return []
            source_nodes = [node]
            per_node = False
            base_delta = (parent.level + 1) - node.level

        attached = []
        for sn in source_nodes:
            delta = (parent.level + 1) - sn.level if per_node else base_delta
            clone = sn.copy_with_level_delta(delta, max_level=max_level)
            parent.add_child(clone)
            attached.append(clone)
        return attached
