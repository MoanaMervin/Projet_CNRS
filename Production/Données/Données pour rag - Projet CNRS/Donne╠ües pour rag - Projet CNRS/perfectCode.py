import re
from bs4 import BeautifulSoup

def clean_html_full(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    # enlever bruit
    for tag in soup(["script", "style", "noscript", "iframe", "svg"]):
        tag.decompose()

    # garder body si possible
    root = soup.body if soup.body else soup

    # enlever attributs
    for t in root.find_all(True):
        t.attrs = {}

    cleaned = str(root)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned
