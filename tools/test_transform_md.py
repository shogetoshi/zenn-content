import pytest
import transform_md as target


@pytest.mark.parametrize(
    "lines,expected",
    [
        (["aaa\n", "bbb\n"], ["aaa ", "bbb\n"]),
        (["aaa\n", "\n", "bbb\n"], ["aaa\n", "\n", "bbb\n"]),
        (["## aaa\n", "bbb\n"], ["## aaa\n", "bbb\n"]),
        (["1. aaa\n", "bbb\n"], ["1. aaa\n", "bbb\n"]),
        (["- aaa\n", "  - bbb\n"], ["- aaa\n", "  - bbb\n"]),
        (["aaa\n", "## bbb\n"], ["aaa\n", "## bbb\n"]),
        (
            ["aaa\n", "![](https://example.com/bbb)\n"],
            ["aaa\n", "![](https://example.com/bbb)\n"],
        ),
        (
            ["```python\n", "aaa\n", "bbb\n", "```\n", "aaa\n", "bbb\n"],
            ["```python\n", "aaa\n", "bbb\n", "```\n", "aaa ", "bbb\n"],
        ),
        (
            ["```aaa\n", "https://www.google.co.jp \n", "bbb\n"],
            ["```aaa\n", "https://www.google.co.jp \n", "bbb\n"],
        ),
        (
            ["aaa\n", ":::messages\n", "bbb\n", "ccc\n", ":::\n", "ddd\n"],
            ["aaa\n", ":::messages\n", "bbb ", "ccc\n", ":::\n", "ddd\n"],
        ),
    ],
)
def test_delete_newlines(lines, expected):
    response = target.delete_newline(lines)
    assert response == expected


@pytest.mark.parametrize(
    "lines,expected",
    [
        (["- aaa\n", "bbb\n"], ["- aaa\n", "\n", "bbb\n"]),
        (
            ["---\n", "title\n"],
            ["---\n", "title\n"],
        ),
        (
            ["- aaa\n", "  - bbb\n"],
            ["- aaa\n", "  - bbb\n"],
        ),
        (
            ["- aaa\n", "  - bbb\n", "ccc\n"],
            ["- aaa\n", "  - bbb\n", "\n", "ccc\n"],
        ),
    ],
)
def test_insert_newline(lines, expected):
    response = target.insert_newline(lines)
    assert response == expected


@pytest.mark.parametrize(
    "lines,expected",
    [
        (
            ["# aaa\n"],
            ["## aaa\n"],
        ),
        (
            ["```\n", "# aaa\n"],
            ["```\n", "# aaa\n"],
        ),
    ],
)
def test_adjust_heading(lines, expected):
    response = target.adjust_heading(lines)
    assert response == expected
