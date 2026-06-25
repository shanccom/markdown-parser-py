import pytest
from markdown_parser import MarkdownNode


def test_remove_child():
    parent = MarkdownNode(1, "Parent")
    child = MarkdownNode(2, "Child")
    parent.add_child(child)
    parent.remove_child(child)
    assert child not in parent.children


def test_print_tree_single_node(capsys):
    node = MarkdownNode(1, "Title")
    node.print_tree()
    captured = capsys.readouterr()
    assert "# Title" in captured.out
    assert "└──" in captured.out


def test_print_tree_root_no_output(capsys):
    root = MarkdownNode(0, "ROOT")
    root.print_tree()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_print_tree_last_false(capsys):
    node = MarkdownNode(1, "Title")
    node.print_tree(last=False)
    captured = capsys.readouterr()
    assert "├── # Title" in captured.out


def test_print_tree_with_children(capsys):
    parent = MarkdownNode(2, "Parent")
    child_a = MarkdownNode(3, "A")
    child_b = MarkdownNode(3, "B")
    grandchild = MarkdownNode(4, "A1")
    child_a.add_child(grandchild)
    parent.add_child(child_a)
    parent.add_child(child_b)

    parent.print_tree()

    captured = capsys.readouterr()
    assert "└── ## Parent" in captured.out
    assert "├── ### A" in captured.out
    assert "│   └── #### A1" in captured.out
    assert "└── ### B" in captured.out


def test_dump_with_content():
    node = MarkdownNode(1, "Title")
    node.add_content("Some content")
    node.add_content("More content")
    result = node.dump()
    assert "# Title" in result
    assert "Some content" in result
    assert "More content" in result


def test_dump_with_children():
    parent = MarkdownNode(1, "Parent")
    child = MarkdownNode(2, "Child")
    parent.add_child(child)
    result = parent.dump()
    assert "# Parent" in result
    assert "## Child" in result


def test_dump_level_zero():
    root = MarkdownNode(0, "ROOT")
    child = MarkdownNode(1, "Section")
    root.add_child(child)
    result = root.dump()
    assert "ROOT" not in result.split("# ")[0] if "# " in result else True
    assert "# Section" in result


def test_copy_with_level_delta_level_zero():
    root = MarkdownNode(0, "ROOT")
    clone = root.copy_with_level_delta(2)
    assert clone.level == 0


def test_copy_with_level_delta_clamp_min():
    node = MarkdownNode(1, "Title")
    clone = node.copy_with_level_delta(-2)
    assert clone.level == 1


def test_copy_with_level_delta_clamp_max():
    node = MarkdownNode(5, "Title")
    clone = node.copy_with_level_delta(3)
    assert clone.level == 6


def test_copy_with_level_delta_with_children():
    parent = MarkdownNode(2, "Parent")
    child = MarkdownNode(3, "Child")
    parent.add_child(child)
    clone = parent.copy_with_level_delta(1)
    assert clone.level == 3
    assert clone.children[0].level == 4
    assert clone.children[0].title == "Child"


def test_copy_with_level_delta_no_clamp():
    node = MarkdownNode(2, "Title")
    clone = node.copy_with_level_delta(2)
    assert clone.level == 4


def test_add_content_empty():
    node = MarkdownNode(1, "Title")
    node.add_content("   ")
    node.add_content("")
    assert node.content == []
