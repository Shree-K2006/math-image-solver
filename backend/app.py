from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import pytesseract
import numexpr as ne

# --------------------------
# SETUP FASTAPI
# --------------------------
app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --------------------------
# TESSERACT CONFIG
# --------------------------
# Replace with your correct Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --------------------------
# IMAGE PREPROCESSING
# --------------------------
def preprocess_image(image_bytes):
    # Convert bytes to numpy array
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Median blur to remove noise
    gray = cv2.medianBlur(gray, 3)

    # Thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # TODO: add rotation/skew correction if needed

    return thresh

# --------------------------
# OCR EXTRACTION
# --------------------------
def extract_expression(img):
    # OCR with Tesseract
    text = pytesseract.image_to_string(img, config='--psm 6')

    # Clean text: remove spaces, newlines, unwanted chars
    expr = text.replace(" ", "").replace("\n", "")
    expr = expr.replace("×", "*").replace("÷", "/")

    # Keep only valid characters for safe evaluation
    allowed_chars = "0123456789+-*/()."
    expr = "".join([c for c in expr if c in allowed_chars])

    return expr

# --------------------------
# ROUTE TO COMPUTE MATH
# --------------------------
@app.post("/compute")
async def compute_math(file: UploadFile = File(...)):
    try:
        # Read image bytes
        img_bytes = await file.read()

        # Preprocess image
        preprocessed = preprocess_image(img_bytes)

        # Extract arithmetic expression
        expr = extract_expression(preprocessed)

        if not expr:
            return {"error": "No valid arithmetic expression found."}

        # Safe evaluation
        result = ne.evaluate(expr)

        return {"expression": expr, "result": float(result)}

    except Exception as e:
        return {"error": str(e)}