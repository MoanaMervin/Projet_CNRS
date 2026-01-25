import re
from pathlib import Path
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

def html_to_text(clean_html: str) -> str:
    soup = BeautifulSoup(clean_html, "lxml")
    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def fix_mojibake(s: str) -> str:
    """
    Répare le cas classique: 'IngÃ©nieur' au lieu de 'Ingénieur'
    (texte UTF-8 interprété en latin-1).
    Si ce n'est pas ce cas, ça ne change rien.
    """
    if "Ã" in s or "Â" in s:
        try:
            return s.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
        except Exception:
            return s
    return s

def main():
    in_dir = Path(".")
    out_html_dir = in_dir / "cleaned_html_full"
    out_txt_dir = in_dir / "cleaned_txt_full"
    out_html_dir.mkdir(exist_ok=True)
    out_txt_dir.mkdir(exist_ok=True)

    html_files = sorted(in_dir.glob("*.html"))
    if not html_files:
        print("Aucun fichier .html trouvé dans le dossier courant.")
        return

    print(f"{len(html_files)} fichiers HTML trouvés.")

    for fp in html_files:
        b = fp.read_bytes()

        # Lecture robuste
        try:
            raw = b.decode("utf-8")
        except UnicodeDecodeError:
            raw = b.decode("latin-1", errors="replace")

        # Répare 'IngÃ©nieur' si besoin
        raw = fix_mojibake(raw)

        cleaned_html = clean_html_full(raw)
        cleaned_txt = html_to_text(cleaned_html)

        (out_html_dir / fp.name).write_text(cleaned_html, encoding="utf-8")
        (out_txt_dir / (fp.stem + ".txt")).write_text(cleaned_txt, encoding="utf-8")

        print(f"OK: {fp.name} -> {out_html_dir.name}/{fp.name} + {out_txt_dir.name}/{fp.stem}.txt")

    print("\nTerminé.")

if __name__ == "__main__":
    main()
