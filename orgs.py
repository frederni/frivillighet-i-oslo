import requests
import pandas as pd


POSTAL_CODES_URL = "https://www.erikbolstad.no/postnummer-koordinatar/txt/postnummer.csv"
BRREG_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"


def _load_oslo_postal_codes() -> pd.DataFrame:
    df = pd.read_csv(POSTAL_CODES_URL, sep="\t")
    return df[df["KOMMUNE"] == "Oslo"].copy()


def get_oslo_districts() -> list[str]:
    df = _load_oslo_postal_codes()
    return sorted(df["BYDEL"].dropna().unique().tolist())


def get_postal_codes_for_district(district: str) -> list[str]:
    df = _load_oslo_postal_codes()
    codes = df[df["BYDEL"] == district]["POSTNR"].tolist()
    return [str(c).zfill(4) for c in codes]


def fetch_organizations(postal_codes: list[str]) -> list[dict]:
    params = {
        "registrertIFrivillighetsregisteret": "true",
        "underTvangsavviklingEllerTvangsopplosning": "false",
        "underAvvikling": "false",
        "konkurs": "false",
        "postadresse.postnummer": ",".join(postal_codes),
        "size": 200,
        "page": 0,
    }
    all_orgs = []
    while True:
        resp = requests.get(BRREG_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        embedded = data.get("_embedded", {})
        orgs = embedded.get("enheter", [])
        all_orgs.extend(orgs)
        page_info = data.get("page", {})
        current = page_info.get("number", 0)
        total_pages = page_info.get("totalPages", 1)
        if current + 1 >= total_pages:
            break
        params["page"] = current + 1
    return all_orgs


def orgs_to_dataframe(orgs: list[dict], district: str) -> pd.DataFrame:
    rows = []
    for o in orgs:
        email = o.get("epostadresse")
        if not email:
            continue
        addr = o.get("postadresse") or {}
        rows.append({
            "organisasjonsnummer": o.get("organisasjonsnummer"),
            "navn": o.get("navn"),
            "epostadresse": email,
            "telefon": o.get("telefon") or o.get("mobil"),
            "hjemmeside": o.get("hjemmeside"),
            "organisasjonsform": (o.get("organisasjonsform") or {}).get("beskrivelse"),
            "naeringskode": (o.get("naeringskode1") or {}).get("beskrivelse"),
            "aktivitet": " ".join(o.get("aktivitet") or []),
            "stiftelsesdato": o.get("stiftelsesdato"),
            "postnummer": addr.get("postnummer"),
            "poststed": addr.get("poststed"),
            "bydel": district,
        })
    return pd.DataFrame(rows)


def get_district_orgs(district: str) -> pd.DataFrame:
    postal_codes = get_postal_codes_for_district(district)
    orgs = fetch_organizations(postal_codes)
    return orgs_to_dataframe(orgs, district)


def get_all_oslo_orgs() -> pd.DataFrame:
    frames = []
    for district in get_oslo_districts():
        print(f"Fetching {district}...")
        df = get_district_orgs(district)
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    combined.drop_duplicates(subset=["organisasjonsnummer"], inplace=True)
    return combined


def export_to_excel(df: pd.DataFrame, path: str = "oslo_orgs.xlsx") -> None:
    df.to_excel(path, index=False)
    print(f"Exported {len(df)} organizations to {path}")


def export_to_json(df: pd.DataFrame, path: str = "oslo_orgs.json") -> None:
    df.to_json(path, orient="records", force_ascii=False, indent=2)
    print(f"Exported {len(df)} organizations to {path}")


if __name__ == "__main__":
    df = get_all_oslo_orgs()
    print(f"Total organizations with email: {len(df)}")
    export_to_excel(df)
    export_to_json(df, "docs/oslo_orgs.json")
