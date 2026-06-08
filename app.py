import io
import streamlit as st
from orgs import get_oslo_districts, get_district_orgs, get_all_oslo_orgs

st.set_page_config(page_title="Frivillige organisasjoner i Oslo", layout="wide")
st.title("Frivillige organisasjoner i Oslo")
st.caption("Kilde: Bronnoysundregistrene (Frivillighetsregisteret). Kun organisasjoner med e-postadresse.")

ALL = "Alle bydeler"
districts = get_oslo_districts() + [ALL]
selected = st.selectbox("Velg bydel", districts, index=districts.index("Alna"))

@st.cache_data(show_spinner="Henter data...")
def load_district(district):
    if district == ALL:
        return get_all_oslo_orgs()
    return get_district_orgs(district)

df = load_district(selected)

search = st.text_input("Sok", placeholder="Navn, e-post, aktivitet...")
if search:
    mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
    df = df[mask]

st.write(f"{len(df)} organisasjoner")

st.dataframe(
    df[["navn", "bydel", "epostadresse", "telefon", "hjemmeside", "organisasjonsform", "naeringskode", "aktivitet", "stiftelsesdato"]],
    use_container_width=True,
    hide_index=True,
)

buf = io.BytesIO()
df.to_excel(buf, index=False)
buf.seek(0)
filename = f"{selected.replace(' ', '_').lower()}_organisasjoner.xlsx"
st.download_button("Last ned Excel", data=buf, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
