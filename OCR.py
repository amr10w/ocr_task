from paddleocr import PaddleOCR
import easyocr
import time
import re
from jiwer import wer
import cv2
import numpy as np
import pandas as pd

import os

IMAGE_PATH = "images/image copy 3.png" if os.path.exists("images/image copy 3.png") else "image copy 3.png"
GROUND_TRUTH_PATH = "data/text.txt" if os.path.exists("data/text.txt") else "text.txt"


# --------------------------------------------------
# Preprocessing
# --------------------------------------------------

def load_image(path):
    return cv2.imread(path)  # BGR

def to_gray(img):
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def denoise(img):
    return cv2.fastNlMeansDenoising(to_gray(img), h=10,
                                    templateWindowSize=7, searchWindowSize=21)

def apply_clahe(img, clip_limit=2.0, tile=(8, 8)):
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile)
    return clahe.apply(to_gray(img))

def enhance_contrast_simple(img, alpha=1.5, beta=0):
    return cv2.convertScaleAbs(to_gray(img), alpha=alpha, beta=beta)

def binarize_otsu(img):
    _, b = cv2.threshold(to_gray(img), 0, 255,
                         cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return b

def binarize_adaptive(img):
    return cv2.adaptiveThreshold(to_gray(img), 255,
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, blockSize=31, C=15)

def deskew(img):
    gray = to_gray(img)
    # ink mask: ink = white (255) after inverted Otsu
    _, mask = cv2.threshold(gray, 0, 255,
                            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(mask > 0))
    if len(coords) < 100:
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    # normalize to (-45, 45]; convention differs across OpenCV versions
    if angle > 45:
        angle -= 90
    elif angle < -45:
        angle += 90
    h, w = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=255)

def upscale(img, scale=2.0):
    return cv2.resize(img, None, fx=scale, fy=scale,
                      interpolation=cv2.INTER_LANCZOS4)

STEP_FUNCS = {
    "gray": to_gray,
    "denoise": denoise,
    "clahe": apply_clahe,
    "contrast": enhance_contrast_simple,
    "otsu": binarize_otsu,
    "adaptive": binarize_adaptive,
    "deskew": deskew,
    "upscale": upscale,
}

def preprocess(img, steps):
    for s in steps:
        img = STEP_FUNCS[s](img)
    return img

def ensure_3ch(img):
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


# --------------------------------------------------
# Ground truth / normalization / metrics
# --------------------------------------------------

def load_ground_truth(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def edit_distance(a, b):
    rows, cols = len(a) + 1, len(b) + 1
    dp = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        dp[i][0] = i
    for j in range(cols):
        dp[0][j] = j
    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1,
                           dp[i][j - 1] + 1,
                           dp[i - 1][j - 1] + cost)
    return dp[-1][-1]

def cer(reference, prediction):
    if len(reference) == 0:
        return 0 if len(prediction) == 0 else 1
    return edit_distance(reference, prediction) / len(reference)


# --------------------------------------------------
# OCR engines (load once)
# --------------------------------------------------

print("Loading models...")
paddle_ocr = PaddleOCR(lang="en")
easy_reader = easyocr.Reader(["en"])

def run_paddle(img):
    img = ensure_3ch(img)
    start = time.perf_counter()
    result = paddle_ocr.predict(img)
    elapsed = time.perf_counter() - start
    texts, scores = [], []
    for res in result:
        texts.extend(res["rec_texts"])
        scores.extend(res["rec_scores"])
    conf = sum(scores) / len(scores) if scores else 0
    return " ".join(texts), elapsed, conf

def run_easy(img):
    start = time.perf_counter()
    result = easy_reader.readtext(img)
    elapsed = time.perf_counter() - start
    texts = [t for _, t, _ in result]
    scores = [c for _, _, c in result]
    conf = sum(scores) / len(scores) if scores else 0
    return " ".join(texts), elapsed, conf

ENGINES = {"paddle": run_paddle, "easy": run_easy}


# --------------------------------------------------
# Variants to test
# --------------------------------------------------

VARIANTS = {
    "raw":                    [],
    "gray":                   ["gray"],
    "denoise":                ["denoise"],
    "clahe":                  ["clahe"],
    "contrast_simple":        ["contrast"],
    "upscale_2x":             ["upscale"],
    "upscale_then_clahe":     ["upscale", "clahe"],
    "clahe_then_upscale":     ["clahe", "upscale"],
    "denoise_clahe":          ["denoise", "clahe"],
    "deskew_clahe":           ["deskew", "clahe"],
    "otsu":                   ["otsu"],
    "adaptive":               ["adaptive"],
    "full_adaptive":          ["denoise", "clahe", "deskew", "adaptive"],
}


# --------------------------------------------------
# Main sweep
# --------------------------------------------------

ground_truth = normalize_text(load_ground_truth(GROUND_TRUTH_PATH))
original = load_image(IMAGE_PATH)

# warm-up so first-call overhead doesn't pollute timings
print("Warming up...")
for fn in ENGINES.values():
    fn(original)

rows = []
for variant, steps in VARIANTS.items():
    t0 = time.perf_counter()
    img = preprocess(original, steps) if steps else original
    prep_time = time.perf_counter() - t0

    # optional: inspect what each variant looks like
    cv2.imwrite(f"debug_{variant}.png", img)

    for engine_name, fn in ENGINES.items():
        text, ocr_time, conf = fn(img)
        pred = normalize_text(text)
        rows.append({
            "variant": variant,
            "engine": engine_name,
            "cer": cer(ground_truth, pred),
            "wer": wer(ground_truth, pred),
            "conf": conf,
            "prep_s": prep_time,
            "ocr_s": ocr_time,
        })
        print(f"{variant:20s} {engine_name:7s} "
              f"CER={rows[-1]['cer']:.4f} WER={rows[-1]['wer']:.4f} "
              f"conf={conf:.4f} ocr={ocr_time:.1f}s")

df = pd.DataFrame(rows)
os.makedirs("results", exist_ok=True)
df.to_csv("results/preprocessing_results.csv", index=False)


print("\n=== Sorted by CER ===")
print(df.sort_values(["engine", "cer"]).to_string(index=False))

print("\n=== Best variant per engine ===")
print(df.loc[df.groupby("engine")["cer"].idxmin()].to_string(index=False))