from app.rag.loader import parse_frontmatter


def test_frontmatter():
    text = "---\ndocument_name: Test\npolicy_version: 1.2\n---\n# Body"
    meta, body = parse_frontmatter(text)
    assert meta["document_name"] == "Test"
    assert body.startswith("# Body")
