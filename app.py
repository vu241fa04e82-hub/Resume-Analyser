from flask import Flask, render_template, request
import os
import json

from utils.pdf_reader import extract_text
from utils.ai import analyze_resume


app = Flask(__name__)

# ---------------------------------------
# UPLOAD CONFIGURATION
# ---------------------------------------

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------
# HOME PAGE
# ---------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------
# RESUME UPLOAD + ANALYSIS
# ---------------------------------------

@app.route("/upload", methods=["POST"])
def upload():

    # Check whether a file was uploaded
    if "resume" not in request.files:
        return "Please upload a resume."

    file = request.files["resume"]

    # Check filename
    if file.filename == "":
        return "Please select a PDF file."

    # Only allow PDF files
    if not file.filename.lower().endswith(".pdf"):
        return "Please upload a PDF file only."

    # Save uploaded resume
    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    print("Resume saved:", filepath)


    # ---------------------------------------
    # EXTRACT TEXT FROM PDF
    # ---------------------------------------

    resume_text = extract_text(filepath)

    if not resume_text or not resume_text.strip():

        return """
        <h2>Could not read the resume.</h2>
        <p>Please make sure your PDF contains selectable text.</p>
        <a href="/">Go Back</a>
        """


    print("Resume text extracted successfully.")
    print("Characters extracted:", len(resume_text))


    # ---------------------------------------
    # GET JOB DESCRIPTION
    # ---------------------------------------

    job_description = request.form.get(
        "job_description",
        ""
    )

    print(
        "Job description received:",
        bool(job_description.strip())
    )


    # ---------------------------------------
    # SEND RESUME TO GEMINI
    # ---------------------------------------

    try:

        raw_analysis = analyze_resume(
            resume_text,
            job_description
        )

        print("AI analysis received.")


    except Exception as e:

        print("AI ERROR:", e)

        return f"""
        <h2>AI analysis failed.</h2>

        <p>
            Please check your Gemini API configuration.
        </p>

        <p>
            Error: {e}
        </p>

        <a href="/">Go Back</a>
        """


    # ---------------------------------------
    # CONVERT AI RESPONSE TO JSON
    # ---------------------------------------

    try:

        cleaned = raw_analysis.strip()

        # Gemini sometimes returns:
        #
        # ```json
        # {...}
        # ```
        #
        # Remove those markers.

        if cleaned.startswith("```json"):

            cleaned = cleaned[
                len("```json"):
            ]

        elif cleaned.startswith("```"):

            cleaned = cleaned[
                len("```"):
            ]


        if cleaned.endswith("```"):

            cleaned = cleaned[
                :-len("```")
            ]


        cleaned = cleaned.strip()


        # Convert JSON text into Python dictionary
        analysis = json.loads(cleaned)


        print("AI JSON parsed successfully.")


    except Exception as e:

        print("JSON ERROR:", e)
        print("RAW AI RESPONSE:")
        print(raw_analysis)


        return f"""
        <h2>AI response could not be processed.</h2>

        <p>
            The AI returned an unexpected format.
        </p>

        <p>
            Error: {e}
        </p>

        <details>

            <summary>
                Show AI response
            </summary>

            <pre>
{raw_analysis}
            </pre>

        </details>

        <br>

        <a href="/">
            Try Again
        </a>
        """


    # ---------------------------------------
    # MAKE SURE REQUIRED FIELDS EXIST
    # ---------------------------------------

    analysis.setdefault(
        "ats_score",
        0
    )

    analysis.setdefault(
        "job_match_score",
        0
    )

    analysis.setdefault(
        "summary",
        "No summary available."
    )

    analysis.setdefault(
        "strengths",
        []
    )

    analysis.setdefault(
        "skills",
        []
    )

    analysis.setdefault(
        "missing_skills",
        []
    )

    analysis.setdefault(
        "matched_keywords",
        []
    )

    analysis.setdefault(
        "missing_keywords",
        []
    )

    analysis.setdefault(
        "improvements",
        []
    )

    analysis.setdefault(
        "job_roles",
        []
    )

    analysis.setdefault(
        "career_advice",
        []
    )


    # ---------------------------------------
    # DISPLAY RESULT PAGE
    # ---------------------------------------

    return render_template(
        "result.html",
        analysis=analysis
    )


# ---------------------------------------
# RUN FLASK
# ---------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )