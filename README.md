# Frivillige organisasjoner i Oslo

Streamlit-app for å finne frivillige organisasjoner i Oslo, filtrert per bydel.

Data hentes fra [Brønnøysundregistrene](https://data.brreg.no) (Frivillighetsregisteret) og postnummerdata fra [erikbolstad.no](https://www.erikbolstad.no/postnummer-koordinatar/). Kun organisasjoner med registrert e-postadresse vises.

## Funksjoner

- Filtrer per bydel
- Fritekst-søk på navn, e-post og aktivitet
- Last ned resultat som Excel

## Kjør lokalt

For å kjøre lokalt må du ha [uv](https://docs.astral.sh/uv/getting-started/installation/) installert.

```bash
git clone https://github.com/frederni/frivillighet-i-oslo
cd frivillighet-i-oslo
uv sync
uv run streamlit run app.py
```
