import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_readme_links_to_files_that_exist():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    links = re.findall(r"\]\(((?!http)[^)#]+)\)", text)
    assert links
    for link in links:
        assert (ROOT / link).exists(), link
