from paddleocr import PaddleOCR
import easyocr
import time
from jiwer import wer

import os

IMAGE_PATH = "images/image copy 3.png" if os.path.exists("images/image copy 3.png") else "images/image copy.png"
GROUND_TRUTH_PATH = "data/text.txt" if os.path.exists("data/text.txt") else "text.txt"



def load_ground_truth(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def paddle(path):
    ocr = PaddleOCR(lang="en")

    start = time.perf_counter()

    result = ocr.predict(path)

    elapsed = time.perf_counter() - start

    texts = []
    scores = []

    for res in result:
        texts.extend(res["rec_texts"])
        scores.extend(res["rec_scores"])

    recognized_text = " ".join(texts)

    avg_confidence = (
        sum(scores) / len(scores)
        if scores else 0
    )

    return recognized_text, elapsed, avg_confidence

def easy(path):
    reader = easyocr.Reader(["en"])

    start = time.perf_counter()

    result = reader.readtext(path)

    elapsed = time.perf_counter() - start

    texts = []
    scores = []

    for bbox, text, confidence in result:
        texts.append(text)
        scores.append(confidence)

    recognized_text = " ".join(texts)

    avg_confidence = (
        sum(scores) / len(scores)
        if scores else 0
    )

    return recognized_text, elapsed, avg_confidence