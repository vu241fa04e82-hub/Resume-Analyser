import pymupdf


def extract_text(pdf_path):

    text = ""

    try:

        document = pymupdf.open(pdf_path)

        for page in document:

            text += page.get_text()

        document.close()

    except Exception as e:

        print("PDF reading error:", e)

        return ""

    return text