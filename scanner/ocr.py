# -*- coding: utf-8 -*-

from PIL import Image
import pytesseract


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

# Tesseract is installed locally.
# We are using the direct path so that we do NOT need to
# modify the Windows system PATH.

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# ============================================================
# OCR FUNCTION
# ============================================================

def extract_text_from_image(image_source):
    """
    Extract text from an image.

    image_source can be:
    - a normal image file path
    - a Flask uploaded file object

    Returns:
        Extracted text as a string.
    """

    try:

        # ----------------------------------------------------
        # Open the image
        # ----------------------------------------------------

        image = Image.open(image_source)

        # ----------------------------------------------------
        # Convert image to RGB
        # ----------------------------------------------------

        image = image.convert("RGB")

        # ----------------------------------------------------
        # Extract text using Tesseract OCR
        # ----------------------------------------------------

        text = pytesseract.image_to_string(
            image,
            lang="eng"
        )

        # ----------------------------------------------------
        # Clean extracted text
        # ----------------------------------------------------

        text = text.strip()

        return text

    except Exception as e:

        print("OCR Error:", e)

        return ""


# ============================================================
# TEST OCR DIRECTLY
# ============================================================

if __name__ == "__main__":

    image_path = "test_scam.png"

    text = extract_text_from_image(image_path)

    print("\n========== OCR RESULT ==========\n")

    if text:
        print(text)
    else:
        print("No text could be detected.")

    print("\n================================")