"""Chatbot for querying candidate resumes using structured profile data and Gemini.

Answers questions strictly grounded in the candidate's extracted profile.
"""

import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMENI_APY_KEY")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
FALLBACK_MODEL = "gemini-3.5-flash-lite"

CHATBOT_SYSTEM_PROMPT = """You are a helpful and precise HR assistant answering questions about a job candidate.
You are given the candidate's structured profile (in JSON) and the raw OCR text of their resume.

Guidelines:
1. Answer the question accurately using ONLY the provided candidate data.
2. If the information is not present or cannot be determined from the resume, clearly state: "This information is not provided in the candidate's resume."
3. Do not invent, assume, or hallucinate qualifications, contact details, or dates.
4. Keep your answers concise, professional, and directly to the point.
"""


def call_gemini(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Send prompt to Gemini model and return text response."""
    if not API_KEY:
        raise ValueError("Gemini API key not found in .env or environment variables.")

    models_to_try = [model]
    for alt in ["gemini-3.8-flash", "gemini-3.5-flash-lite"]:
        if alt not in models_to_try:
            models_to_try.append(alt)

    import time
    for m in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={API_KEY}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }
        for _ in range(2):
            try:
                r = requests.post(url, json=payload, timeout=30)
                if r.status_code == 200:
                    data = r.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                elif r.status_code == 503:
                    time.sleep(1.5)
            except Exception:
                time.sleep(1.0)


    raise RuntimeError("Failed to get response from Gemini API.")


def answer_candidate_question(candidate_data: dict, question: str, model: str = DEFAULT_MODEL) -> str:
    """Answer a user question regarding a specific candidate profile.

    Args:
        candidate_data: Structured candidate JSON dictionary.
        question: User query string.
        model: Gemini model name.

    Returns:
        Grounded answer string.
    """
    candidate_summary = json.dumps({
        k: v for k, v in candidate_data.items() if k != "raw_text"
    }, indent=2)

    prompt = f"""{CHATBOT_SYSTEM_PROMPT}

Candidate Profile (JSON):
```json
{candidate_summary}
```

Raw Resume Text:
\"\"\"{candidate_data.get('raw_text', '')}\"\"\"

User Question: {question}

Answer:"""

    return call_gemini(prompt, model=model)


def interactive_chat(candidate_data: dict):
    """Launch interactive CLI chat session for a candidate."""
    name = candidate_data.get("name") or candidate_data.get("candidate_id", "Unknown Candidate")
    print("\n" + "=" * 60)
    print(f" Chatbot ready for: {name} ({candidate_data.get('candidate_id', 'ID: N/A')})")
    print(" Type your question and press Enter. (Type 'exit' or 'quit' to stop)")
    print("=" * 60 + "\n")

    while True:
        try:
            query = input("Ask a question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat.")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            print("Session ended.")
            break

        print("\nThinking...")
        try:
            answer = answer_candidate_question(candidate_data, query)
            print(f"\n[Answer]:\n{answer}\n")
            print("-" * 60)
        except Exception as e:
            print(f"\n[Error]: Could not retrieve answer: {e}\n")


if __name__ == "__main__":
    default_file = (
        "candidates/c_0001.json" if os.path.exists("candidates/c_0001.json")
        else ("outputs/candidate_extracted.json" if os.path.exists("outputs/candidate_extracted.json")
        else "candidate_extracted.json")
    )
    parser = argparse.ArgumentParser(description="Candidate Resume Chatbot")
    parser.add_argument("--file", "-f", default=default_file, help=f"Path to candidate JSON file (default: {default_file})")
    parser.add_argument("--question", "-q", help="Optional single question to ask non-interactively")

    args = parser.parse_args()

    target_file = args.file
    if not os.path.exists(target_file):
        for candidate_dir in ["candidates", "outputs"]:
            alt = os.path.join(candidate_dir, target_file)
            if os.path.exists(alt):
                target_file = alt
                break
            if not target_file.endswith(".json"):
                alt_json = os.path.join(candidate_dir, f"{target_file}.json")
                if os.path.exists(alt_json):
                    target_file = alt_json
                    break

    if not os.path.exists(target_file):
        print(f"Error: Candidate file '{args.file}' not found.")
        sys.exit(1)

    with open(target_file, "r", encoding="utf-8") as f:
        candidate = json.load(f)


    if args.question:
        ans = answer_candidate_question(candidate, args.question)
        print(f"Question: {args.question}")
        print(f"Answer: {ans}")
    else:
        interactive_chat(candidate)
