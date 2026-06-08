from typing import Any

import pandas as pd
import requests

POSTAL_CODES_URL = "https://www.erikbolstad.no/postnummer-koordinatar/txt/postnummer.csv"
BRREG_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

_cache: dict[str, pd.DataFrame] = {}


def _load_oslo_postal_codes() -> pd.DataFrame:
    if "oslo" not in _cache:
        postal_df = pd.read_csv(POSTAL_CODES_URL, sep="\t")
        _cache["oslo"] = postal_df[postal_df["KOMMUNE"] == "Oslo"].copy()
    return _cache["oslo"]


def get_oslo_districts() -> list[str]:
    return sorted(_load_oslo_postal_codes()["BYDEL"].dropna().unique().tolist())


def get_postal_codes_for_district(district: str) -> list[str]:
    codes = _load_oslo_postal_codes()[_load_oslo_postal_codes()["BYDEL"] == district]["POSTNR"].tolist()
    return [str(c).zfill(4) for c in codes]


def fetch_organizations(postal_codes: list[str]) -> list[dict[str, Any]]:
    params: dict[str, str | int] = {
        "registrertIFrivillighetsregisteret": "true",
        "underTvangsavviklingEllerTvangsopplosning": "false",
        "underAvvikling": "false",
        "konkurs": "false",
        "postadresse.postnummer": ",".join(postal_codes),
        "size": 200,
        "page": 0,
    }
    all_orgs: list[dict[str, Any]] = []
    while True:
        resp = requests.get(BRREG_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        orgs = data.get("_embedded", {}).get("enheter", [])
        all_orgs.extend(orgs)
        page_info = data.get("page", {})
        if page_info.get("number", 0) + 1 >= page_info.get("totalPages", 1):
            break
        params["page"] = page_info["number"] + 1
    return all_orgs


def orgs_to_dataframe(orgs: list[dict[str, Any]], district: str) -> pd.DataFrame:
    rows = []
    for org in orgs:
        email = org.get("epostadresse")
        if not email:
            continue
        addr = org.get("postadresse") or {}
        rows.append({
            "organisasjonsnummer": org.get("organisasjonsnummer"),
            "navn": org.get("navn"),
            "epostadresse": email,
            "telefon": org.get("telefon") or org.get("mobil"),
            "hjemmeside": org.get("hjemmeside"),
            "organisasjonsform": (org.get("organisasjonsform") or {}).get("beskrivelse"),
            "naeringskode": (org.get("naeringskode1") or {}).get("beskrivelse"),
            "aktivitet": " ".join(org.get("aktivitet") or []),
            "stiftelsesdato": org.get("stiftelsesdato"),
            "postnummer": addr.get("postnummer"),
            "poststed": addr.get("poststed"),
            "bydel": district,
        })
    return pd.DataFrame(rows)


def get_district_orgs(district: str) -> pd.DataFrame:
    return orgs_to_dataframe(fetch_organizations(get_postal_codes_for_district(district)), district)


def get_all_oslo_orgs() -> pd.DataFrame:
    frames = []
    for district in get_oslo_districts():
        print(f"Fetching {district}...")
        frames.append(get_district_orgs(district))
    combined = pd.concat(frames, ignore_index=True)
    combined.drop_duplicates(subset=["organisasjonsnummer"], inplace=True)
    return combined
