import pytest
from markdown_parser import MarkdownNode, MarkdownTree

# Objetivo: ejecutar TODAS las sentencias del método dump() al menos una vez.
def test_statement_dump():
    child = MarkdownNode(2, "Child")
    child.add_content("Child content")
    parent = MarkdownNode(1, "Parent")
    parent.add_child(child)

    result = parent.dump()

    assert "# Parent" in result
    assert "## Child" in result
    assert "Child content" in result


# Objetivo: transitar por las aristas True y False de cada decisión.
@pytest.mark.parametrize(
    "level, delta, expected_level",
    [
        (2, 1, 3),   # D1=F, D2=F, D3=F
        (1, -2, 1),  # D1=F, D2=T
        (5, 5, 6),   # D1=F, D3=T
        (0, 3, 0),   # D1=T
    ],
)
def test_branch_copy_with_level_delta(level, delta, expected_level):
    node = MarkdownNode(level, "Test")
    clone = node.copy_with_level_delta(delta)
    assert clone.level == expected_level


# 3. BRANCH CONDITION COMBINATION TESTING — MarkdownTree.attach_subtree()
@pytest.mark.parametrize(
    "source_path, expected",
    [
        ("NONEXISTENT", 0),  # C1=V (short-circuit)
        ("Intro", 1),        # C1=F, C2=F
    ],
)
def test_condition_combination_attach(source_path, expected):
    src = MarkdownTree()
    src.parse("# Intro\nHello\n## Sub\nNested")
    dst = MarkdownTree()
    dst.parse("# Existing\nContent")
    attached = dst.attach_subtree("Existing", src, source_path)
    assert len(attached) == expected
