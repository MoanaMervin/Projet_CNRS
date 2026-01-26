import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

def detect_encoding(raw: bytes) -> str:
    # les pages CNRS ont souvent charset=iso-8859-1
    m = re.search(br'charset\s*=\s*([A-Za-z0-9_\-]+)', raw[:5000], flags=re.I)
    if m:
        enc = m.group(1).decode("ascii", errors="ignore").lower()
        return enc
    return "utf-8"

def clean_text(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\r", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def get_entete_fields(soup: BeautifulSoup) -> dict:
    spans = soup.select("span.enteteconcours")
    entete = [clean_text(sp.get_text(" ", strip=True)) for sp in spans if clean_text(sp.get_text(" ", strip=True))]

    bap = entete[0] if len(entete) >= 1 else ""
    grade = entete[1] if len(entete) >= 2 else ""
    concours_label = entete[2] if len(entete) >= 3 else ""

    concours_num = ""
    m = re.search(r"Concours\s*N[°o]\s*([0-9]+)", concours_label, flags=re.I)
    if m:
        concours_num = m.group(1)

    nb_postes = ""
    emploi_type = ""

    # table "Nbre de postes" / "Emploi-type"
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        k = clean_text(tds[0].get_text(" ", strip=True)).lower()
        v = clean_text(tds[1].get_text(" ", strip=True))
        if "nbre de postes" in k:
            nb_postes = v
        if "emploi-type" in k or "emploi type" in k:
            emploi_type = v

    return {
        "bap": bap,
        "grade": grade,
        "concours_label": concours_label,
        "concours_num": concours_num,
        "nb_postes": nb_postes,
        "emploi_type": emploi_type,
    }

def extract_section_from_block(block: BeautifulSoup, anchor: str) -> str:
    """
    Dans un bloc poste, la section est:
    <a name="mission"><b>Mission :</b></a> ... puis dans la même table :
    <td colspan="2"> ... texte ... </td>
    """
    a = block.find("a", attrs={"name": anchor})
    if not a:
        return ""
    table = a.find_parent("table")
    if not table:
        return ""
    td = table.find("td", attrs={"colspan": "2"})
    if not td:
        # fallback
        return clean_text(table.get_text("\n", strip=True))
    return clean_text(td.get_text("\n", strip=True))

def extract_kv_in_block(block: BeautifulSoup, key: str) -> str:
    # Ex: <b>Affectation :</b> puis valeur dans le td suivant de la même ligne
    key = key.lower()
    for tr in block.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        k = clean_text(tds[0].get_text(" ", strip=True)).lower()
        if key in k:
            return clean_text(tds[1].get_text(" ", strip=True))
    return ""

def build_poste_blocks(soup: BeautifulSoup) -> list[tuple[int, BeautifulSoup]]:
    headers = soup.select("td.soustitreprincipal")
    blocks = []

    for i, h in enumerate(headers):
        htxt = clean_text(h.get_text(" ", strip=True))
        m = re.search(r"(\d+)\s*(?:er|eme|ème)\s+poste", htxt, flags=re.I)
        if not m:
            continue
        poste_num = int(m.group(1))

        start_table = h.find_parent("table")
        end_table = headers[i + 1].find_parent("table") if i + 1 < len(headers) else None

        # collecte les éléments entre start_table et end_table (exclu)
        parts = []
        node = start_table
        while node:
            node = node.find_next_sibling()
            if not node:
                break
            if end_table and node == end_table:
                break
            parts.append(str(node))

        block_html = "\n".join(parts)
        block_soup = BeautifulSoup(block_html, "lxml")
        blocks.append((poste_num, block_soup))

    return blocks

def parse_postes(soup: BeautifulSoup) -> list[dict]:
    postes = []
    poste_blocks = build_poste_blocks(soup)

    for poste_num, block in poste_blocks:
        postes.append({
            "poste_num": poste_num,
            "affectation": extract_kv_in_block(block, "Affectation"),
            "groupe_fonction": extract_kv_in_block(block, "Groupe de fonction"),
            "mission": extract_section_from_block(block, "mission"),
            "activites": extract_section_from_block(block, "activites"),
            "competences": extract_section_from_block(block, "competences"),
            "contexte": extract_section_from_block(block, "contexte"),
        })

    # fallback si aucun header trouvé
    if not postes:
        postes.append({
            "poste_num": 1,
            "affectation": extract_kv_in_block(soup, "Affectation"),
            "groupe_fonction": extract_kv_in_block(soup, "Groupe de fonction"),
            "mission": extract_section_from_block(soup, "mission"),
            "activites": extract_section_from_block(soup, "activites"),
            "competences": extract_section_from_block(soup, "competences"),
            "contexte": extract_section_from_block(soup, "contexte"),
        })

    return postes

def main():
    in_dir = Path(".")
    html_files = sorted(in_dir.glob("page_*.html"))
    if not html_files:
        print("Aucun fichier page_*.html trouvé.")
        return

    out_dir = in_dir / "cleaned_json_full"
    out_dir.mkdir(exist_ok=True)

    for fp in html_files:
        raw_bytes = fp.read_bytes()
        enc = detect_encoding(raw_bytes)
        raw = raw_bytes.decode(enc, errors="replace")

        soup = BeautifulSoup(raw, "lxml")

        entete = get_entete_fields(soup)
        postes = parse_postes(soup)

        data = {
            "source_file": fp.name,
            **entete,
            "nb_postes_detectes": len(postes),
            "postes": postes
        }

        (out_dir / (fp.stem + ".json")).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"OK: {fp.name} -> cleaned_json_full/{fp.stem}.json")

    print("\nTerminé.")

if __name__ == "__main__":
    main()
