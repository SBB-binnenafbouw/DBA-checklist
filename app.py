import os
from datetime import UTC, datetime
from pathlib import Path

import json

from flask import Flask, render_template, request, send_file, flash
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "not-for-production")

# Basic translation dictionaries. The English copy can be used for official wording
# while the Dutch copy provides an accessible translation.
LANG_CONTENT = {
    "en": {
        "title": "Independent Contractor Checklist",
        "description": (
            "Complete this short checklist to document that the engagement does not "
            "constitute false self-employment. Keep the language simple and answer each "
            "question honestly."
        ),
        "contractor_details": "Contractor details",
        "client_details": "Client details",
        "project_details": "Assignment details",
        "contractor_name": "Contractor name",
        "contractor_company": "Business name (if applicable)",
        "client_name": "Client/agency name",
        "project_name": "Assignment or project",
        "language_label": "Language",
        "choose_language": "Choose language",
        "questions_intro": "Answer each question with Yes or No.",
        "questions": [
            {
                "id": "multiple_clients",
                "text": "Does the contractor work for multiple clients during the year?",
            },
            {
                "id": "controls_schedule",
                "text": "Does the contractor decide their own working hours?",
            },
            {
                "id": "provides_tools",
                "text": "Does the contractor use their own tools or equipment?",
            },
            {
                "id": "entrepreneurial_risk",
                "text": "Does the contractor carry financial or entrepreneurial risk?",
            },
            {
                "id": "can_substitute",
                "text": "Can the contractor send a qualified substitute to perform the work?",
            },
            {
                "id": "sets_rates",
                "text": "Does the contractor agree the rates and scope directly with the client?",
            },
        ],
        "additional_notes": "Additional notes",
        "declaration": "Declaration",
        "declaration_text": (
            "I confirm that the answers above are correct to the best of my knowledge."
        ),
        "date_label": "Date",
        "submit": "Generate PDF",
        "yes": "Yes",
        "no": "No",
        "success_message": "Checklist submitted. Your PDF download will begin shortly.",
        "language_notice": (
            "A copy of the original language submission and the Dutch translation will be saved."
        ),
    },
    "nl": {
        "title": "Checklist zelfstandige zonder schijnzelfstandigheid",
        "description": (
            "Vul deze korte checklist in om vast te leggen dat de opdracht geen "
            "schijnzelfstandigheid oplevert. Gebruik eenvoudige taal en beantwoord de "
            "vragen eerlijk."
        ),
        "contractor_details": "Gegevens opdrachtnemer",
        "client_details": "Gegevens opdrachtgever/bemiddelaar",
        "project_details": "Opdracht",
        "contractor_name": "Naam opdrachtnemer",
        "contractor_company": "Bedrijfsnaam (indien van toepassing)",
        "client_name": "Naam opdrachtgever/bureau",
        "project_name": "Naam opdracht of project",
        "language_label": "Taal",
        "choose_language": "Kies taal",
        "questions_intro": "Beantwoord elke vraag met Ja of Nee.",
        "questions": [
            {
                "id": "multiple_clients",
                "text": "Werkt de zzp'er in het jaar voor meerdere opdrachtgevers?",
            },
            {
                "id": "controls_schedule",
                "text": "Bepaalt de zzp'er zelf de werktijden?",
            },
            {
                "id": "provides_tools",
                "text": "Gebruikt de zzp'er eigen gereedschap of middelen?",
            },
            {
                "id": "entrepreneurial_risk",
                "text": "Draagt de zzp'er ondernemers- of financieel risico?",
            },
            {
                "id": "can_substitute",
                "text": "Kan de zzp'er zich laten vervangen door een gekwalificeerde vervanger?",
            },
            {
                "id": "sets_rates",
                "text": "Maakt de zzp'er zelf prijsafspraken over tarief en scope?",
            },
        ],
        "additional_notes": "Opmerkingen",
        "declaration": "Verklaring",
        "declaration_text": "Ik verklaar dat bovenstaande antwoorden naar waarheid zijn ingevuld.",
        "date_label": "Datum",
        "submit": "PDF maken",
        "yes": "Ja",
        "no": "Nee",
        "success_message": "Checklist verzonden. De PDF-download start direct.",
        "language_notice": (
            "Er wordt een kopie van de originele taal en de Nederlandse vertaling opgeslagen."
        ),
    },
}

DEFAULT_LANGUAGE = "nl"
SUPPORTED_LANGUAGES = LANG_CONTENT.keys()

SUBMISSION_DIR = Path(os.environ.get("SUBMISSION_DIR", "submissions"))
SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)


def get_language(lang_param: str | None) -> str:
    if lang_param and lang_param.lower() in SUPPORTED_LANGUAGES:
        return lang_param.lower()
    return DEFAULT_LANGUAGE


def generate_pdf(data: dict, language: str, file_path: Path) -> None:
    content = LANG_CONTENT[language]
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, content["title"])

    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 6, content["description"])
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, content["contractor_details"], ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, f"{content['contractor_name']}: {data['contractor_name']}")
    pdf.multi_cell(0, 6, f"{content['contractor_company']}: {data['contractor_company']}")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, content["client_details"], ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, f"{content['client_name']}: {data['client_name']}")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, content["project_details"], ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, f"{content['project_name']}: {data['project_name']}")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, content["questions_intro"], ln=True)
    pdf.set_font("Helvetica", size=11)
    for question in content["questions"]:
        raw_answer = data.get(question["id"], "")
        if raw_answer == "yes":
            answer = content["yes"]
        elif raw_answer == "no":
            answer = content["no"]
        else:
            answer = raw_answer
        pdf.multi_cell(0, 6, f"- {question['text']} : {answer}")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, content["additional_notes"], ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, data.get("notes", ""))
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, content["declaration"], ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, content["declaration_text"])
    pdf.multi_cell(0, 6, f"{content['date_label']}: {data['submitted_at']}")

    pdf.output(str(file_path))


def save_submission(data: dict, language: str) -> Path:
    now_utc = datetime.now(UTC)
    timestamp = now_utc.strftime("%Y%m%d_%H%M%S")
    safe_name = data.get("contractor_name", "anonymous").replace(" ", "_") or "anonymous"
    base_filename = f"{timestamp}_{safe_name}_{language}"
    pdf_path = SUBMISSION_DIR / f"{base_filename}.pdf"
    generate_pdf(data, language, pdf_path)

    # Optionally store the raw submission data alongside the PDF for quick reference.
    json_path = SUBMISSION_DIR / f"{base_filename}.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    if language != "nl":
        dutch_base = f"{timestamp}_{safe_name}_nl"
        dutch_path = SUBMISSION_DIR / f"{dutch_base}.pdf"
        dutch_data = {**data, "language": "nl"}
        generate_pdf(dutch_data, "nl", dutch_path)

    return pdf_path


@app.route("/", methods=["GET"])
def index():
    language = get_language(request.args.get("lang"))
    content = LANG_CONTENT[language]
    return render_template(
        "index.html",
        language=language,
        content=content,
        supported_languages=SUPPORTED_LANGUAGES,
        current_date=datetime.now(UTC).strftime("%Y-%m-%d"),
    )


@app.route("/submit", methods=["POST"])
def submit():
    language = get_language(request.form.get("language"))
    content = LANG_CONTENT[language]

    responses = {}
    for question in content["questions"]:
        responses[question["id"]] = request.form.get(question["id"], "")

    submission_data = {
        "contractor_name": request.form.get("contractor_name", "").strip(),
        "contractor_company": request.form.get("contractor_company", "").strip(),
        "client_name": request.form.get("client_name", "").strip(),
        "project_name": request.form.get("project_name", "").strip(),
        "notes": request.form.get("notes", "").strip(),
        "submitted_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "language": language,
    }
    submission_data.update(responses)

    pdf_path = save_submission(submission_data, language)

    flash(content["success_message"])
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"{pdf_path.stem}.pdf",
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
