# AI-Powered Sales CRM — Online Website

A Python + Streamlit CRM web app using Google Gemini to extract leads from meeting notes, recommend follow-ups, show sales pipeline charts, and draft customer emails.

**This folder is ready to deploy to Streamlit Community Cloud.** It is not a static HTML website. Streamlit hosts both its browser UI and Python code in one application.

## Deploy to a shareable URL (without using the terminal)

1. Sign into [GitHub](https://github.com/) and create a new repository, e.g. `ai-sales-crm-demo`.
2. Upload the **uncompressed contents of this folder** to the repository, preserving `app.py`, `requirements.txt`, `datastore/`, and `.streamlit/`. Do not upload this ZIP as a single file.
3. Visit [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
4. Select **Create app / Deploy**, choose your repository and branch, and set the **main file path** to `app.py`.
5. In **Advanced settings -> Secrets**, paste:
   ```toml
   GEMINI_API_KEY = "YOUR_ACTUAL_GEMINI_KEY"
   APP_PASSWORD = "YOUR_PRIVATE_DEMO_PASSWORD"
   ```
   The password is optional if you want a public, shared demonstration. The AI key is necessary for AI features. Never upload keys or passwords to GitHub.
6. If prompted, choose Python **3.11**. Click **Deploy** and then copy the generated `https://<your-subdomain>.streamlit.app` link.

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
