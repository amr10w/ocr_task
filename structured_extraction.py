import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Support both GEMINI_API_KEY and GEMENI_APY_KEY (common typo in .env)
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMENI_APY_KEY")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
FALLBACK_MODEL = "gemini-3.5-flash-lite"

PROMPT_TEMPLATE = """You are an expert HR data parsing assistant.
Your task is to take the following OCR text extracted from a resume (which may contain OCR typos, noise, or formatting quirks) and convert it into clean, accurate, and searchable structured JSON.

Target JSON Schema:
{{
  "candidate_id": "{candidate_id}",
  "name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "location": "string or null",
  "summary": "string or null",
  "education": [
    {{
      "institution": "string",
      "degree": "string",
      "years": "string"
    }}
  ],
  "experience": [
    {{
      "company": "string",
      "title": "string",
      "dates": "string",
      "description": "string"
    }}
  ],
  "skills": ["string"],
  "projects": [
    {{
      "name": "string",
      "description": "string"
    }}
  ],
  "certifications": ["string"],
  "languages": ["string"],
  "raw_text": "string",
  "flags": ["string"]
}}

Instructions:
1. Fix obvious OCR errors (for instance, unintended character substitutions or merged words).
2. If a field is not present in the text, use null (or empty list [] for array fields).
3. In "flags", note any key missing information (e.g. "phone not found", "projects not listed", "unclear graduation date").
4. Return ONLY the valid JSON object adhering strictly to the schema.

OCR Text to parse:
---
{ocr_text}
---
"""


def call_gemini(prompt: str, model: str = DEFAULT_MODEL, api_key: str = None) -> str:
    """Send prompt to Gemini generateContent endpoint requesting JSON output."""
    key = api_key or API_KEY
    if not key:
        raise ValueError(
            "Gemini API key not found. Please set GEMINI_API_KEY in your .env file or environment."
        )

    models_to_try = [model]
    for alt in ["gemini-3.8-flash", "gemini-3.5-flash-lite"]:
        if alt not in models_to_try:
            models_to_try.append(alt)

    import time
    last_error = None
    for m in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1
            }
        }

        for attempt in range(2):
            try:
                response = requests.post(url, json=payload, timeout=45)
                if response.status_code == 200:
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                elif response.status_code == 503:
                    time.sleep(1.5)
                    continue
                else:
                    last_error = f"Model {m} returned {response.status_code}: {response.text}"
                    break
            except Exception as e:
                last_error = f"Request to model {m} failed: {e}"
                time.sleep(1.0)

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")



def extract_candidate_info(ocr_text: str, candidate_id: str = "c_0001", model: str = DEFAULT_MODEL) -> dict:
    """Extract structured candidate info from OCR text using Gemini.
    
    Args:
        ocr_text: Raw OCR text from resume.
        candidate_id: Identifier for the candidate record.
        model: Gemini model name.

    Returns:
        Structured candidate dictionary.
    """
    prompt = PROMPT_TEMPLATE.format(
        candidate_id=candidate_id,
        ocr_text=ocr_text.strip()
    )

    response_text = call_gemini(prompt, model=model)
    data = json.loads(response_text)

    # Ensure required top-level keys exist and raw_text / candidate_id are set
    data["candidate_id"] = candidate_id
    if not data.get("raw_text"):
        data["raw_text"] = ocr_text.strip()

    return data


def extract_from_file(input_file: str, candidate_id: str = "c_0001", output_file: str = None) -> dict:
    """Read OCR text from a file and save structured JSON output."""
    with open(input_file, "r", encoding="utf-8") as f:
        ocr_text = f.read()

    print(f"[*] Processing OCR text from: {input_file} ({len(ocr_text)} chars)")
    result = extract_candidate_info(ocr_text, candidate_id=candidate_id)

    if output_file:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[+] Structured JSON saved to: {output_file}")

    return result


if __name__ == "__main__":
    default_input = "data/text.txt" if os.path.exists("data/text.txt") else "text.txt"
    parser = argparse.ArgumentParser(description="Extract structured candidate JSON from resume OCR text using Gemini.")
    parser.add_argument("--input", "-i", default=default_input, help=f"Path to OCR text file (default: {default_input})")
    parser.add_argument("--output", "-o", default="outputs/candidate_extracted.json", help="Path to save JSON output (default: outputs/candidate_extracted.json)")
    parser.add_argument("--id", default="c_0001", help="Candidate ID (default: c_0001)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Gemini model (default: {DEFAULT_MODEL})")

    args = parser.parse_args()

    # Check fallback for input path
    input_path = args.input
    if not os.path.exists(input_path):
        alt = os.path.join("data", input_path)
        if os.path.exists(alt):
            input_path = alt
        else:
            print(f"Error: Input file '{args.input}' not found.")
            sys.exit(1)

    structured_data = extract_from_file(
        input_file=input_path,
        candidate_id=args.id,
        output_file=args.output
    )


    print("\n=== Extracted Structured JSON ===")
    print(json.dumps(structured_data, indent=2))
