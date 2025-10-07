# DBA Checklist prototype

This repository contains a lightweight prototype for a DBA/ZZP checklist that records the key indicators for false self-employment and produces a signed PDF copy for both the contractor and your organisation.

## Features

- Single-page checklist with simple yes/no questions written in clear language.
- Dutch and English language support with instant language switching.
- PDF generation using the wording of the selected language while saving a server-side copy.
- Automatic Dutch translation stored alongside every submission so the organisation always has a Dutch version for the Belastingdienst.
- Stores submissions (PDF + raw data) under `submissions/` so the organisation always receives the same document downloaded by the user.

## Getting started

1. Create a virtual environment and install the dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the Flask development server:

   ```bash
   flask --app app run
   ```

3. Open the app in your browser at <http://localhost:5000>.

## Customisation

- Add extra languages by extending the `LANG_CONTENT` dictionary in `app.py`. The English copy can hold the official legal phrasing, while the Dutch entry can remain accessible for lower literacy levels.
- Adjust the questions or styling by editing `app.py` and the template in `templates/index.html`.
- Configure the storage location by setting the `SUBMISSION_DIR` environment variable.
- Provide a secure `FLASK_SECRET_KEY` in production to protect form feedback messages.

## PDF storage

When a checklist is submitted the server writes:

- `submissions/<timestamp>_<contractor>_<lang>.pdf` – the PDF downloaded by the user.
- `submissions/<timestamp>_<contractor>_<lang>.json` – a quick reference snapshot of the submission data.
- `submissions/<timestamp>_<contractor>_nl.pdf` – automatic Dutch translation when the user completes the form in another language.

These files allow you to archive the evidence required by the Belastingdienst while giving contractors instant proof of their submission.
