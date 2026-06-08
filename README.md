# Frivillige organisasjoner i Oslo

[![Streamlit App](https://img.shields.io/badge/streamlit-app-FF4B4B?logo=streamlit&logoColor=white)](https://frivillighet-i-oslo.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![pylint](https://img.shields.io/badge/pylint-10.00-brightgreen)](https://pylint.pycqa.org/)

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
