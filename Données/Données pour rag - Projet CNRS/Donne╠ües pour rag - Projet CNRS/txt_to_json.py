import re
import json
from pathlib import Path

def split_postes(text):
    pattern = r"(\d+(?:er|eme) poste du concours[^\n]*)"
    parts = re.split(pattern, text)
    postes = []

    for i in range(1, len(parts), 2):
        title = parts[i]
        content = parts[i+1]
        postes.append((title, content))
    return postes

def extract_section(name, text):
    pattern = rf"{name}\s*:\s*(.*?)(?=\n[A-ZÉÈÀ].*?:|\Z)"
    m = re.search(pattern, text, re.S | re.I)
    return m.group(1).strip() if m else ""

def main():
    in_dir = Path("cleaned_txt_full")
    out_dir = Path("cleaned_json")
    out_dir.mkdir(exist_ok=True)

    for fp in in_dir.glob("*.txt"):
        text = fp.read_text(encoding="utf-8")

        postes_raw = split_postes(text)
        postes = []

        for i, (_, ptext) in enumerate(postes_raw, 1):
            postes.append({
                "poste_num": i,
                "mission": extract_section("Mission", ptext),
                "activites": extract_section("Activités", ptext),
                "competences": extract_section("Compétences", ptext),
                "contexte": extract_section("Contexte", ptext)
            })

        data = {
            "source_file": fp.name,
            "postes": postes
        }

        (out_dir / (fp.stem + ".json")).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"OK: {fp.name}")

if __name__ == "__main__":
    main()
