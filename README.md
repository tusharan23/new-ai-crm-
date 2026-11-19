# AI-Powered Sales CRM — Online Website

A Python + Streamlit CRM web app using Google Gemini to extract leads from meeting notes, recommend follow-ups, show sales pipeline charts, and draft customer emails.

### Getting the Gemini key

Generate a key through [Google AI Studio](https://aistudio.google.com/apikey). API usage may have quota or billing limitations.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set GEMINI_API_KEY inside .env
streamlit run app.py
```

Open the localhost URL shown in the terminal.

## What changed for cloud deployment

- The app accepts `GEMINI_API_KEY` and optional `APP_PASSWORD` from secure cloud secrets or local `.env`.
- The CRM dashboard stays usable even before an API key is configured; AI features show as unavailable.
- An optional password gate prevents casual access to a shared CRM demo.
- Writable CSV files now go into `runtime_data/`, which is excluded from GitHub to avoid accidentally committing customer information.
- The original app's dashboard, lead extraction, analytics, email generation, and demo-data action remain available.
- Searches use literal text rather than a regular expression; largest-deal ranking uses numeric values.

## Important limitations

**This deployment is appropriate for a demo or portfolio project, not a production CRM.**

- **Data is not persistent:** Streamlit Community Cloud does not guarantee local file storage after restarts, redeployments, or app moves. Use a hosted database (for example, Postgres/Supabase) for permanent lead records.
- **One shared dataset:** all people who access this app see/edit the same CRM. It does not have separate user accounts or private customer workspaces.
- **Privacy:** meeting notes are sent to Google's Gemini API for processing. Do not submit real confidential customer information without appropriate permissions, access controls, and a privacy review.
- **API quotas:** Gemini can stop responding if the account exceeds quota/billing limits.
- **Auth:** the optional single-password gate is for demos, not a replacement for robust production authentication.

## Main files

- `app.py`: web UI + Gemini features
- `main.py`: demo-data seeding and activity logging
- `datastore/database.py`: simple CSV storage
- `requirements.txt`: Python dependencies
- `.streamlit/config.toml`: appearance
- `.streamlit/secrets.toml.example`: example hosting secrets; contains placeholders only
