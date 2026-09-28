"""End-to-End Pipeline for Handwritten/Scanned Resumes.

Workflow:
1. Ingest image (or text file)
2. Perform OCR (PaddleOCR or EasyOCR) & Text Cleanup
3. Extract structured JSON via Gemini (gemini-3.1-flash-lite)
4. Store in searchable candidate registry
5. Query via grounded chatbot
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

# Local module imports
from structured_extraction import extract_candidate_info
from chatbot import answer_candidate_question, interactive_chat

CANDIDATES_DIR = Path("candidates")
CANDIDATES_DIR.mkdir(exist_ok=True)
INDEX_FILE = CANDIDATES_DIR / "index.json"

EMAIL_RE = re.compile(r"[\w.\-]+\s*@\s*[\w\-]+(?:\s*\.\s*[a-z0-9\-]+)+")


def clean_text(text: str) -> str:
    """Clean OCR text while preserving line and section structure."""
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    # Remove accidental spaces within email addresses
    text = EMAIL_RE.sub(lambda m: re.sub(r"\s+", "", m.group(0)), text)
    return text.strip()


def run_ocr(image_path: str, engine: str = "easy") -> str:
    """Run OCR on the given image path using PaddleOCR or EasyOCR."""
    print(f"[Stage 1-3] Running {engine.upper()} on: {image_path}")

    if engine.lower() == "paddle":
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(lang="en")
            result = ocr.predict(image_path)
            lines = []
            for res in result:
                lines.extend(res.get("rec_texts", []))
            return "\n".join(lines)
        except Exception as e:
            print(f"[!] PaddleOCR error ({e}), falling back to EasyOCR...")

    try:
        import easyocr
        reader = easyocr.Reader(["en"])
        result = reader.readtext(image_path)
        lines = [text for _, text, _ in result]
        return "\n".join(lines)
    except Exception as e:
        raise RuntimeError(f"OCR execution failed: {e}")


def save_candidate_to_store(candidate: dict) -> Path:
    """Save candidate JSON to candidates/ directory and update index."""
    candidate_id = candidate.get("candidate_id", "c_unknown")
    file_path = CANDIDATES_DIR / f"{candidate_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(candidate, f, indent=2, ensure_ascii=False)

    # Update index
    index = {}
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                index = json.load(f)
        except Exception:
            index = {}

    index[candidate_id] = {
        "file": str(file_path),
        "name": candidate.get("name"),
        "email": candidate.get("email"),
        "phone": candidate.get("phone"),
        "location": candidate.get("location"),
        "skills": candidate.get("skills", []),
        "education": [
            f"{e.get('degree', '')} at {e.get('institution', '')}"
            for e in candidate.get("education", [])
        ],
        "companies": [c.get("company", "") for c in candidate.get("experience", [])],
    }

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"[+] Candidate saved to searchable store: {file_path}")
    return file_path


def search_candidate_store(query: str):
    """Search stored candidates by name, skill, company, education, or keyword."""
    if not INDEX_FILE.exists():
        print("Candidate index is empty.")
        return []

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index = json.load(f)

    q = query.lower()
    matches = []

    for cid, record in index.items():
        score = 0
        name = (record.get("name") or "").lower()
        skills = [s.lower() for s in record.get("skills", [])]
        companies = [c.lower() for c in record.get("companies", [])]
        education = [e.lower() for e in record.get("education", [])]

        if q in name:
            score += 4
        if any(q in s for s in skills):
            score += 3
        if any(q in c for c in companies):
            score += 2
        if any(q in e for e in education):
            score += 2

        # Check full candidate file if available
        if score == 0 and os.path.exists(record.get("file", "")):
            try:
                with open(record["file"], "r", encoding="utf-8") as cf:
                    full_text = cf.read().lower()
                    if q in full_text:
                        score += 1
            except Exception:
                pass

        if score > 0:
            matches.append((cid, record))

    return matches



def run_pipeline(image_path: str = None, text_path: str = None, candidate_id: str = "c_0001",
                 engine: str = "easy", start_chat: bool = False):
    """Execute end-to-end pipeline."""
    print("=" * 60)
    print(" Starting End-to-End Handwritten Resume Pipeline")
    print("=" * 60)

    # Step 1: Text acquisition
    if image_path:
        raw_text = run_ocr(image_path, engine=engine)
    elif text_path:
        print(f"[Stage 1] Loading OCR text directly from: {text_path}")
        with open(text_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    else:
        raise ValueError("Must provide either --image or --text path.")

    # Step 2: Cleanup
    print("[Stage 4] Cleaning text and preserving structure...")
    cleaned = clean_text(raw_text)

    # Step 3: Structured Extraction
    print(f"[Stage 5] Extracting structured JSON via Gemini for candidate '{candidate_id}'...")
    candidate_data = extract_candidate_info(cleaned, candidate_id=candidate_id)

    # Step 4: Storage
    print("[Stage 6-7] Saving to searchable candidate store...")
    save_candidate_to_store(candidate_data)

    print("\n[+] Extraction Summary:")
    print(f"    Name:     {candidate_data.get('name')}")
    print(f"    Email:    {candidate_data.get('email')}")
    print(f"    Phone:    {candidate_data.get('phone')}")
    print(f"    Skills:   {', '.join(candidate_data.get('skills', []))}")
    print(f"    Flags:    {candidate_data.get('flags', [])}")

    # Step 5: Chatbot Q&A
    if start_chat:
        interactive_chat(candidate_data)

    return candidate_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-End Handwritten Resume Pipeline")
    default_text = "data/text.txt" if os.path.exists("data/text.txt") else "text.txt"
    parser.add_argument("--image", "-i", help="Path to resume image")
    parser.add_argument("--text", "-t", default=default_text, help=f"Path to OCR text file (default: {default_text})")
    parser.add_argument("--id", default="c_0001", help="Candidate ID (default: c_0001)")
    parser.add_argument("--engine", choices=["easy", "paddle"], default="easy", help="OCR Engine to use")
    parser.add_argument("--chat", "-c", action="store_true", help="Launch interactive chatbot after extraction")
    parser.add_argument("--search", "-s", help="Search the candidate database by keyword")

    args = parser.parse_args()

    if args.search:
        results = search_candidate_store(args.search)
        print(f"\nSearch results for '{args.search}': {len(results)} found")
        for cid, rec in results:
            print(f"- [{cid}] {rec.get('name')} | Skills: {', '.join(rec.get('skills', []))} | File: {rec.get('file')}")
        sys.exit(0)

    target_image = args.image
    target_text = None
    if not args.image:
        target_text = args.text
        if not os.path.exists(target_text):
            alt = os.path.join("data", target_text)
            if os.path.exists(alt):
                target_text = alt

    run_pipeline(
        image_path=target_image,
        text_path=target_text,
        candidate_id=args.id,
        engine=args.engine,
        start_chat=args.chat
    )

