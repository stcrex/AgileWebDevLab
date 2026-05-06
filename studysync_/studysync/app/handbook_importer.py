from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from .extensions import db
from .models import HandbookSubject

HANDBOOK_SEARCH_URL = "https://handbooks.uwa.edu.au/search/?searchtext={query}&type=units"
DEFAULT_PREFIXES = [
    "CITS", "MATH", "STAT", "DATA", "BUSN", "INMT", "ECON", "FINA",
    "ENSC", "GENG", "EART", "GEOG", "PUBH", "SSEH", "ENTR"
]


def upsert_subject(item: dict) -> bool:
    """Insert or update a HandbookSubject. Returns True only for new rows."""
    subject = HandbookSubject.query.filter_by(code=item["code"]).first()
    created = subject is None
    if created:
        subject = HandbookSubject(code=item["code"], title=item.get("title", item["code"]))
        db.session.add(subject)
    subject.title = item.get("title", subject.title)
    subject.credit_points = int(item.get("credit_points") or 6)
    subject.coordinator = item.get("coordinator", subject.coordinator or "")
    subject.level_of_study = item.get("level_of_study", subject.level_of_study or "")
    subject.school = item.get("school", subject.school or "")
    subject.field_of_education = item.get("field_of_education", subject.field_of_education or "")
    subject.availability = item.get("availability", subject.availability or "")
    subject.location = item.get("location", subject.location or "")
    subject.description = item.get("description", subject.description or "")
    subject.handbook_url = item.get("handbook_url") or f"https://handbooks.uwa.edu.au/unitdetails?code={subject.code}"
    subject.source_year = int(item.get("source_year") or 2026)
    return created


def load_seed_units() -> int:
    """Load bundled seed data. Useful when the network is unavailable."""
    data_path = Path(__file__).parent / "data" / "uwa_handbook_units_2026_seed.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    inserted = sum(1 for item in data if upsert_subject(item))
    db.session.commit()
    return inserted


def fetch_search_page(query: str) -> str:
    url = HANDBOOK_SEARCH_URL.format(query=quote_plus(query))
    request = Request(url, headers={"User-Agent": "StudySync UWA Handbook importer"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def strip_tags(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    return re.sub(r"\s+", " ", text)


def parse_units_from_html(html: str) -> list[dict]:
    """Parse the Handbook search result page into unit dictionaries.

    The UWA search page is public HTML rather than a JSON API, so this parser
    extracts common fields from text patterns. Unknown fields are left blank.
    """
    text = strip_tags(html)
    pattern = re.compile(
        r"(?P<title>[A-Z][^\[]+?)\s*\[(?P<code>[A-Z]{4}\d{4})\]\s*Type:\s*Units\s*"
        r"Credit points:\s*(?P<credit>\d+)?\s*"
        r"(?:Coordinator\(s\)::?\s*(?P<coord>.*?))?\s*"
        r"Level of study:\s*(?P<level>.*?)\s*School:\s*(?P<school>.*?)\s*"
        r"Field of Education\s*(?P<field>.*?)\s*Availability:\s*(?P<avail>.*?)\s*Location:\s*(?P<loc>.*?)(?=\s+[A-Z][^\[]+\s*\[[A-Z]{4}\d{4}\]|\s+Handbook 2026|$)",
        re.I,
    )
    units = []
    seen = set()
    for match in pattern.finditer(text):
        code = match.group("code").upper()
        if code in seen:
            continue
        seen.add(code)
        units.append({
            "code": code,
            "title": match.group("title").strip(" -"),
            "credit_points": int(match.group("credit") or 6),
            "coordinator": (match.group("coord") or "").strip(),
            "level_of_study": match.group("level").strip(),
            "school": match.group("school").strip(),
            "field_of_education": match.group("field").strip(),
            "availability": match.group("avail").strip(),
            "location": match.group("loc").strip(),
            "handbook_url": f"https://handbooks.uwa.edu.au/unitdetails?code={code}",
            "source_year": 2026,
        })
    return units


def import_handbook_units(prefixes: list[str] | None = None) -> tuple[int, int]:
    """Download UWA Handbook unit search pages and import matching subjects.

    Returns (downloaded_count, inserted_count). If the download fails, bundled
    seed data is still loaded so the app continues to work during demos.
    """
    prefixes = prefixes or DEFAULT_PREFIXES
    downloaded = 0
    inserted = 0
    try:
        for prefix in prefixes:
            units = parse_units_from_html(fetch_search_page(prefix))
            downloaded += len(units)
            for unit in units:
                inserted += 1 if upsert_subject(unit) else 0
        db.session.commit()
    except Exception:
        inserted += load_seed_units()
    return downloaded, inserted
