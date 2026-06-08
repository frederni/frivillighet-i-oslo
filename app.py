import io

import pandas as pd
import streamlit as st

from orgs import get_all_oslo_orgs, get_district_orgs, get_oslo_districts

st.set_page_config(page_title="Frivillige organisasjoner i Oslo", layout="wide")
st.title("Frivillige organisasjoner i Oslo")
st.write(
    "Denne siden bruker åpne APIer for å hente navn- og kontaktinfo til frivillige organisasjoner "
    "i ulike bydeler av Oslo. Målet med siden er å lette på programarbeidet til lokalvalg, "
    "og å enkelt få oversikt over lokale aktører i sin bydel."
)
st.caption("Kilde: Brønnøysundregistrene (Frivillighetsregisteret). Kun organisasjoner med e-postadresse.")

ALL = "Alle bydeler"
districts = get_oslo_districts() + [ALL]
selected = st.selectbox("Velg bydel", districts, index=districts.index("Alna"))


@st.cache_data(show_spinner="Henter data...")
def load_district(district: str) -> pd.DataFrame:
    if district == ALL:
        return get_all_oslo_orgs()
    return get_district_orgs(district)


df = load_district(selected)

search = st.text_input("Sok", placeholder="Navn, e-post, aktivitet...")
if search:
    mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
    df = df[mask]

st.write(f"{len(df)} organisasjoner")

COLUMNS = [
    "navn", "bydel", "epostadresse", "telefon", "hjemmeside",
    "organisasjonsform", "naeringskode", "aktivitet", "stiftelsesdato",
]
st.dataframe(df[COLUMNS], use_container_width=True, hide_index=True)

buf = io.BytesIO()
df.to_excel(buf, index=False)
buf.seek(0)
export_filename = f"{selected.replace(' ', '_').lower()}_organisasjoner.xlsx"
st.download_button(
    "Last ned Excel",
    icon=":material/download:",
    data=buf,
    file_name=export_filename,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.divider()
st.caption(
    "Feil eller forslag? "
    "[Opprett en sak på GitHub](https://github.com/frederni/frivillighet-i-oslo/issues)."
)
