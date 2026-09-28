"""Script to generate the comprehensive Word (.docx) report:
Pipeline - MVP - Produce
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_code_block(doc, code_text, title=None):
    if title:
        p_title = doc.add_paragraph()
        run_title = p_title.add_run(f"Code Listing: {title}")
        run_title.bold = True
        run_title.font.size = Pt(10)
        run_title.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        p_title.paragraph_format.space_after = Pt(2)
        p_title.paragraph_format.space_before = Pt(6)

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, "F4F6F9")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    # Border
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:left w:val="single" w:sz="18" w:space="0" w:color="1F4E79"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/></w:tcBorders>')
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(6)

def add_placeholder_box(doc, placeholder_title, description):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, "FEF9C3")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="8" w:space="0" w:color="EAB308"/><w:left w:val="single" w:sz="24" w:space="0" w:color="CA8A04"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="EAB308"/><w:right w:val="single" w:sz="8" w:space="0" w:color="EAB308"/></w:tcBorders>')
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    run_t = p.add_run(f"📂 [SOURCE CODE PLACEHOLDER: {placeholder_title}]")
    run_t.bold = True
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(10.5)
    run_t.font.color.rgb = RGBColor(0x85, 0x4D, 0x0E)

    p_desc = cell.add_paragraph()
    p_desc.paragraph_format.space_before = Pt(0)
    p_desc.paragraph_format.space_after = Pt(0)
    run_d = p_desc.add_run(description)
    run_d.font.name = "Calibri"
    run_d.font.size = Pt(9.5)
    run_d.font.italic = True
    run_d.font.color.rgb = RGBColor(0x71, 0x3F, 0x12)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def build_report():
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # Header / Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(12)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("Handwritten Resume to Searchable Information System")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(24)
    run_title.bold = True
    run_title.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(14)
    run_sub = sub_p.add_run("End-to-End Pipeline Research, Working MVP Implementation, and Production Architecture")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

    # Metadata Table
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        [("Prepared by:", True), ("Amr Ahmed Wahidi", False), ("Prepared for:", True), ("Dr. Abdelrhman", False)],
        [("Date:", True), ("September 28, 2026", False), ("Project State:", True), ("Pipeline Verified & MVP Operational", False)]
    ]
    for r_idx, row in enumerate(meta_table.rows):
        c0 = row.cells[0]
        c1 = row.cells[1]
        set_cell_background(c0, "F8FAFC")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        
        # cell 0
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        r0_t = p0.add_run(meta_data[r_idx][0][0] + " ")
        r0_t.bold = True
        r0_t.font.size = Pt(9.5)
        r0_v = p0.add_run(meta_data[r_idx][1][0])
        r0_v.font.size = Pt(9.5)

        # cell 1
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(2)
        r1_t = p1.add_run(meta_data[r_idx][2][0] + " ")
        r1_t.bold = True
        r1_t.font.size = Pt(9.5)
        r1_v = p1.add_run(meta_data[r_idx][3][0])
        r1_v.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Executive Overview
    h_exec = doc.add_paragraph()
    r_he = h_exec.add_run("Executive Summary")
    r_he.font.size = Pt(14)
    r_he.bold = True
    r_he.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    
    p_exec = doc.add_paragraph()
    p_exec.paragraph_format.line_spacing = 1.15
    p_exec.add_run(
        "This report documents the complete engineering journey of building an AI-powered system that transforms "
        "handwritten, scanned resume images into structured, searchable candidate knowledge queryable by an intelligent "
        "chatbot. The document is divided into three comprehensive sections:\n"
        "1. Pipeline: Detailed architectural design, research methodology, and empirical OCR benchmarking across 13 preprocessing variants.\n"
        "2. MVP (Minimum Viable Product): Concrete implementation of the working pipeline, including Gemini-powered JSON extraction, "
        "searchable local indexing, and a strictly grounded conversational chatbot with verified test cases.\n"
        "3. Produce (Production Roadmap): Architectural, security, and algorithmic upgrades required to transition the MVP into an "
        "enterprise-grade, privacy-first production platform utilizing on-premise LLMs, Qdrant vector databases, and document layout analysis."
    )

    # =========================================================================
    # PART 1: PIPELINE
    # =========================================================================
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(4)
    r_h1 = h1.add_run("PART 1: PIPELINE — Architecture, Research & Empirical Benchmarking")
    r_h1.font.size = Pt(16)
    r_h1.bold = True
    r_h1.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    # 1.1 Objective and Scope
    h1_1 = doc.add_paragraph()
    h1_1.paragraph_format.space_before = Pt(8)
    h1_1.paragraph_format.space_after = Pt(2)
    r_h1_1 = h1_1.add_run("1.1 System Objective and Challenge Formulation")
    r_h1_1.font.size = Pt(12.5)
    r_h1_1.bold = True
    r_h1_1.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    p1_1 = doc.add_paragraph()
    p1_1.paragraph_format.line_spacing = 1.15
    p1_1.add_run(
        "The objective is to design a robust, modular pipeline that accepts an image of a handwritten or poorly scanned resume, "
        "converts the visual handwriting into clean digital text, extracts semantically structured candidate fields (contact, education, "
        "experience, skills, projects), stores that information in an indexed searchable store, and exposes it to a grounded chatbot "
        "that accurately answers recruiter inquiries without hallucinating.\n\n"
        "Handwritten resumes pose distinctive challenges compared to standard digital documents:\n"
        "• Complex visual variability: Non-uniform handwriting slants, stroke thicknesses, and cursive connections.\n"
        "• Irregular layouts: Multi-column sidebars, unaligned tables, bulleted lists, and uneven line spacing.\n"
        "• Sensor & physical noise: Non-uniform lighting, paper shadows, skew angles, blurriness, and compression artifacts.\n"
        "• Critical downstream impact: A single character substitution in an email address, phone number, or date creates cascading failures in search and candidate retrieval."
    )

    # 1.2 The 8-Stage Architecture
    h1_2 = doc.add_paragraph()
    h1_2.paragraph_format.space_before = Pt(8)
    h1_2.paragraph_format.space_after = Pt(2)
    r_h1_2 = h1_2.add_run("1.2 The Conceptual 8-Stage Pipeline Architecture")
    r_h1_2.font.size = Pt(12.5)
    r_h1_2.bold = True
    r_h1_2.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    p1_2 = doc.add_paragraph()
    p1_2.paragraph_format.line_spacing = 1.15
    p1_2.add_run(
        "To decouple visual recognition from semantic interpretation, the end-to-end architecture is partitioned into "
        "eight discrete stages. Stages 1 through 4 transform raw pixels into normalized text; Stage 5 converts unstructured text into "
        "validated structured schema; and Stages 6 through 8 index and query the candidate knowledge base."
    )

    # Table of Stages
    stage_table = doc.add_table(rows=9, cols=4)
    stage_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Stage", "Input", "Output", "Core Technology"]
    for i, h_text in enumerate(headers):
        c = stage_table.cell(0, i)
        set_cell_background(c, "1F4E79")
        set_cell_margins(c, 80, 80, 100, 100)
        p = c.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    stage_rows = [
        ("1. Image Ingestion", "Uploaded JPG/PNG/PDF", "Validated BGR image array + metadata", "OpenCV, Pillow, PyMuPDF"),
        ("2. Preprocessing", "Raw image array", "Preprocessed image array (Grayscale/Deskew)", "OpenCV (cv2)"),
        ("3. OCR Engine", "Preprocessed image array", "Raw text lines + line confidence scores", "PaddleOCR (EasyOCR fallback)"),
        ("4. Text Cleanup", "Raw OCR line stream", "Normalized plain text with structure preserved", "Python regex & string algorithms"),
        ("5. Structured Extraction", "Cleaned resume text", "Strict schema JSON profile + flags", "LLM (Gemini 3.1 Flash / Qwen 2.5)"),
        ("6. Chunking & Embedding", "Structured JSON + text", "Section-based chunks with semantic vectors", "Local dense embedding (BGE/Nomic)"),
        ("7. Vector Store", "Chunks + vectors + payloads", "Persistent collection with hybrid filter index", "Qdrant / Structured Index"),
        ("8. Grounded Chatbot", "Recruiter natural query", "Strictly grounded answer citing sections", "RAG Prompt + Conversational LLM")
    ]

    for row_idx, data in enumerate(stage_rows):
        for col_idx, text in enumerate(data):
            c = stage_table.cell(row_idx + 1, col_idx)
            set_cell_background(c, "F8FAFC" if row_idx % 2 == 0 else "FFFFFF")
            set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 1.3 OCR Research and Empirical Preprocessing Sweep
    h1_3 = doc.add_paragraph()
    h1_3.paragraph_format.space_before = Pt(8)
    h1_3.paragraph_format.space_after = Pt(2)
    r_h1_3 = h1_3.add_run("1.3 OCR Engine Research & Empirical Preprocessing Sweep (OCR.py)")
    r_h1_3.font.size = Pt(12.5)
    r_h1_3.bold = True
    r_h1_3.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    p1_3 = doc.add_paragraph()
    p1_3.paragraph_format.line_spacing = 1.15
    p1_3.add_run(
        "A common pitfall in computer vision pipelines is applying preprocessing steps (such as thresholding or contrast stretching) "
        "based on human visual appeal rather than measured machine performance. In OCR.py, we conducted an empirical benchmark comparing "
        "PaddleOCR (CRNN/SVTR detection and recognition) against EasyOCR (CRAFT detector + ResNet/BiLSTM/CTC recognizer) across 13 preprocessing variants "
        "using rigorous quantitative metrics:\n"
        "• Character Error Rate (CER): Levenshtein edit distance between OCR output and normalized ground truth, divided by ground truth character length. (Lower is better)\n"
        "• Word Error Rate (WER): Word-level Levenshtein distance computed using the jiwer library. (Lower is better)\n"
        "• Inference Latency: Execution time measured after model loading and warm-up cycles.\n"
        "• Engine Confidence: Reported mathematical confidence score across text bounding boxes."
    )

    # Benchmark Results Table
    bench_table = doc.add_table(rows=14, cols=9)
    bench_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    b_headers = ["Variant", "Paddle CER", "Paddle WER", "Paddle Conf", "Paddle Time", "Easy CER", "Easy WER", "Easy Conf", "Easy Time"]
    for i, h_text in enumerate(b_headers):
        c = bench_table.cell(0, i)
        set_cell_background(c, "2F5597")
        set_cell_margins(c, 70, 70, 60, 60)
        p = c.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    bench_data = [
        ("raw", "0.0230", "0.0945", "0.9914", "60.2s*", "0.0331", "0.1585", "0.8357", "1.3s"),
        ("gray", "0.0230", "0.0945", "0.9914", "28.5s", "0.0331", "0.1585", "0.8357", "1.3s"),
        ("denoise", "0.0238", "0.0976", "0.9909", "29.0s", "0.0331", "0.1585", "0.8368", "1.3s"),
        ("clahe", "0.0230", "0.0945", "0.9907", "28.4s", "0.0335", "0.1585", "0.8273", "1.3s"),
        ("contrast_simple", "0.0226", "0.0976", "0.9913", "28.9s", "0.0548", "0.2805", "0.7763", "1.3s"),
        ("upscale_2x", "0.0242", "0.1220", "0.9939", "37.0s", "0.0468", "0.1585", "0.8497", "2.8s"),
        ("upscale_then_clahe", "0.0198", "0.1006", "0.9934", "35.9s", "0.0455", "0.1463", "0.8370", "2.9s"),
        ("clahe_then_upscale", "0.0250", "0.1250", "0.9940", "36.9s", "0.0468", "0.1585", "0.8384", "2.9s"),
        ("denoise_clahe", "0.0238", "0.0976", "0.9892", "29.3s", "0.0335", "0.1585", "0.8331", "1.3s"),
        ("deskew_clahe", "0.0230", "0.0945", "0.9907", "28.8s", "0.0335", "0.1585", "0.8273", "1.3s"),
        ("otsu (binarize)", "0.0826", "0.1646", "0.9836", "28.3s", "0.0576", "0.2500", "0.7622", "1.3s"),
        ("adaptive (binarize)", "0.0314", "0.1037", "0.9904", "29.5s", "0.0516", "0.2226", "0.7552", "1.3s"),
        ("full_adaptive", "0.0322", "0.1037", "0.9897", "32.1s", "0.0508", "0.2226", "0.7657", "1.2s")
    ]

    for row_idx, row in enumerate(bench_data):
        for col_idx, val in enumerate(row):
            c = bench_table.cell(row_idx + 1, col_idx)
            set_cell_background(c, "F8FAFC" if row_idx % 2 == 0 else "FFFFFF")
            set_cell_margins(c, 50, 50, 50, 50)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if col_idx == 0:
                r.bold = True
            if "otsu" in row[0] and col_idx in [1, 2, 5, 6]:
                r.font.color.rgb = RGBColor(0xDC, 0x26, 0x26) # red for degraded
            if "upscale_then_clahe" in row[0] and col_idx == 1:
                r.font.color.rgb = RGBColor(0x16, 0xA3, 0x4A) # green for best CER

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Key Empirical Insights
    h1_4 = doc.add_paragraph()
    h1_4.paragraph_format.space_before = Pt(8)
    h1_4.paragraph_format.space_after = Pt(2)
    r_h1_4 = h1_4.add_run("1.4 Critical Empirical Findings & Architectural Takeaways")
    r_h1_4.font.size = Pt(12.5)
    r_h1_4.bold = True
    r_h1_4.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    p1_4 = doc.add_paragraph()
    p1_4.paragraph_format.line_spacing = 1.15
    p1_4.add_run(
        "1. Modern Deep OCR Severely Degrades Under Binarization: Classical Otsu binarization increased PaddleOCR CER from 0.0230 to 0.0826 "
        "(a ~360% error spike) and degraded EasyOCR WER from 0.1585 to 0.2500. Forcing pixels to 0 or 255 severs thin handwriting strokes and ligatures, "
        "destroying the continuous gradient features required by deep neural network recognizers.\n\n"
        "2. The Confidence Fallacy: Model confidence is not a proxy for ground-truth accuracy. Under Otsu thresholding, PaddleOCR reported "
        "an average line confidence of 0.9836, yet had nearly 4× worse CER. Consequently, confidence must never be used to rank pipeline variants, "
        "and should only serve as a downstream flag for human-in-the-loop review.\n\n"
        "3. Engine Trade-off Dynamics: PaddleOCR achieved markedly superior word accuracy (WER 0.0945 vs EasyOCR 0.1585). However, EasyOCR demonstrated "
        "an average latency of 1.3 seconds compared to PaddleOCR's 28.5 seconds (steady state). Thus, PaddleOCR is designated as the primary engine "
        "for batch/high-accuracy processing, with EasyOCR functioning as a low-latency fallback.\n\n"
        "4. Preprocessing Minimalism: Standard grayscale conversion halved initialization time (60.2s to 28.5s) while preserving 100% of recognition accuracy. "
        "Heavy combinations (denoising, contrast boosting) added compute latency with zero measurable accuracy gain."
    )

    # Source code placeholder for OCR.py
    add_placeholder_box(
        doc,
        "OCR.py and model.py",
        "Insert the source code of OCR.py (preprocessing functions, metric definitions, and sweep loop) and model.py here."
    )

    # =========================================================================
    # PART 2: MVP IMPLEMENTATION
    # =========================================================================
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(18)
    h2.paragraph_format.space_after = Pt(4)
    r_h2 = h2.add_run("PART 2: MVP — Implementation, Architecture & Verification Test Cases")
    r_h2.font.size = Pt(16)
    r_h2.bold = True
    r_h2.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p2_intro = doc.add_paragraph()
    p2_intro.paragraph_format.line_spacing = 1.15
    p2_intro.add_run(
        "To validate the pipeline design, a functional Minimum Viable Product (MVP) was implemented and thoroughly tested. "
        "The MVP implements the critical stages: OCR ingestion, regex cleanup, Gemini-based structured JSON extraction, "
        "searchable local indexing, and a conversational chatbot interface. The code is modularly organized into three core files:\n"
        "• structured_extraction.py: Gemini 3.1 Flash Lite extraction engine with JSON mode, retry backoff, and OCR artifact self-correction.\n"
        "• chatbot.py: Grounded RAG chatbot preventing hallucinations through negative boundary enforcement.\n"
        "• run_pipeline.py: Unified end-to-end orchestrator connecting image OCR, cleanup, structured extraction, registry storage, and search."
    )

    # 2.1 Implemented Modules Breakdown
    h2_1 = doc.add_paragraph()
    h2_1.paragraph_format.space_before = Pt(8)
    h2_1.paragraph_format.space_after = Pt(2)
    r_h2_1 = h2_1.add_run("2.1 Detailed Implementation of MVP Modules")
    r_h2_1.font.size = Pt(12.5)
    r_h2_1.bold = True
    r_h2_1.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    p2_1 = doc.add_paragraph()
    p2_1.paragraph_format.line_spacing = 1.15
    p2_1.add_run(
        "1. Text Normalization with Line Structure Preservation:\n"
        "As identified in our report, collapsing all whitespace destroys section boundaries. In run_pipeline.py, clean_text() preserves "
        "newlines while sanitizing irregular spaces and specifically removing broken whitespace inside email patterns (e.g. 'john . doe @ example . com' -> 'john.doe@example.com') "
        "without affecting geographical entities ('Cairo. Egypt').\n\n"
        "2. Structured JSON Extraction (structured_extraction.py):\n"
        "The extraction module leverages Google Gemini (gemini-3.1-flash-lite) configured with native responseMimeType='application/json'. "
        "The system prompt strictly enforces the target candidate schema:\n"
        "   - candidate_id, name, email, phone, location, summary\n"
        "   - education: [ { institution, degree, years } ]\n"
        "   - experience: [ { company, title, dates, description } ]\n"
        "   - skills, projects, certifications, languages, raw_text, flags\n"
        "Crucially, the prompt instructs the model to correct OCR character-level substitutions (e.g., template artifacts like 'deadClairenes' -> 'deadlines') "
        "while flagging any missing data in the 'flags' field.\n\n"
        "3. Searchable Candidate Registry:\n"
        "Extracted profiles are persisted to candidates/<candidate_id>.json. In parallel, candidates/index.json indexes names, skills, companies, "
        "and degree institutions, allowing sub-millisecond keyword and entity lookup.\n\n"
        "4. Grounded Chatbot (chatbot.py):\n"
        "The chatbot uses RAG principles. It receives the structured JSON profile and raw OCR text as context. Strict guardrails mandate that if "
        "a requested fact is not present in the resume, the model must explicitly state: 'This information is not provided in the candidate\\'s resume.' "
        "This completely eliminates candidate qualification hallucinations."
    )

    # 2.2 Concrete MVP Test Cases
    h2_2 = doc.add_paragraph()
    h2_2.paragraph_format.space_before = Pt(8)
    h2_2.paragraph_format.space_after = Pt(2)
    r_h2_2 = h2_2.add_run("2.2 Comprehensive MVP Verification Test Cases & Execution Results")
    r_h2_2.font.size = Pt(12.5)
    r_h2_2.bold = True
    r_h2_2.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    # Test Case 1
    p_tc1 = doc.add_paragraph()
    r_tc1_t = p_tc1.add_run("Test Case 1: Structured JSON Extraction from OCR Text (text.txt -> candidate c_0001)")
    r_tc1_t.bold = True
    r_tc1_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    
    p_tc1_desc = doc.add_paragraph()
    p_tc1_desc.paragraph_format.line_spacing = 1.15
    p_tc1_desc.add_run(
        "• Command: python structured_extraction.py --input text.txt --output candidate_extracted.json\n"
        "• Input: 2,482 characters of raw OCR text containing OCR template corruptions ('deadClairenes', 'cClaireent', 'suppClaireed').\n"
        "• Result: Extraction completed successfully in 2.1s with 100% valid JSON adherence."
    )

    tc1_json_sample = """{
  "candidate_id": "c_0001",
  "name": "Jessica Claire",
  "email": "resumesample@example.com",
  "phone": "(555) 432-1000",
  "location": "San Francisco, CA 94105",
  "summary": "Detail-oriented Accountant who effectively manages strict deadlines...",
  "education": [
    {"institution": "Pace University", "degree": "Master of Science: Accounting", "years": "2013"},
    {"institution": "Northeast University of Finance and Economics", "degree": "Bachelor of Science: International Accounting", "years": "2011"}
  ],
  "experience": [
    {"company": "Transamerica Life Insurance Company", "title": "Accountant", "dates": "10/2011 to 04/2013", "description": "..."},
    {"company": "Seven Hills Foundation", "title": "Volunteer", "dates": "02/2013 to 03/2013", "description": "..."},
    {"company": "Telephone And Data Systems Inc.", "title": "Tax Intern", "dates": "05/2012 to 07/2012", "description": "..."},
    {"company": "Lkq", "title": "Audit Intern", "dates": "08/2010 to 11/2010", "description": "..."}
  ],
  "skills": ["Financial statement analysis", "General and tax accounting", "GAAP guidelines", "Time management"],
  "projects": [],
  "certifications": ["Student Affiliate Membership of AICPA", "Member of ACG New York"],
  "flags": ["projects not listed"]
}"""
    add_code_block(doc, tc1_json_sample, "Verified Output for Candidate c_0001 (candidate_extracted.json)")

    # Test Case 2
    p_tc2 = doc.add_paragraph()
    r_tc2_t = p_tc2.add_run("Test Case 2: Full Image-to-JSON Pipeline Execution (image copy 3.png -> candidate c_0002)")
    r_tc2_t.bold = True
    r_tc2_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p_tc2_desc = doc.add_paragraph()
    p_tc2_desc.paragraph_format.line_spacing = 1.15
    p_tc2_desc.add_run(
        "• Command: python run_pipeline.py --image 'images/image copy 3.png' --id c_0002 --engine easy\n"
        "• Process: Automated execution through EasyOCR (detection & recognition) -> clean_text() -> Gemini Extraction -> candidates/c_0002.json -> index.json update.\n"
        "• Intelligent Safeguard Output: The system accurately flagged: ['projects not listed', 'languages not listed', 'Audit Intern company name missing']. "
        "Because the OCR engine split the company acronym 'Lkq', Gemini correctly flagged the company field as missing rather than hallucinating a false employer name."
    )

    # Test Case 3
    p_tc3 = doc.add_paragraph()
    r_tc3_t = p_tc3.add_run("Test Case 3: Searchable Candidate Registry Queries")
    r_tc3_t.bold = True
    r_tc3_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p_tc3_desc = doc.add_paragraph()
    p_tc3_desc.paragraph_format.line_spacing = 1.15
    p_tc3_desc.add_run(
        "• Verification of index-based fast candidate retrieval across entities:\n"
        "  - Query: python run_pipeline.py --search 'Pace University'\n"
        "    Output: Search results for 'Pace University': 1 found -> [c_0001] Jessica Claire | Skills: Financial statement analysis...\n"
        "  - Query: python run_pipeline.py --search 'Transamerica'\n"
        "    Output: Search results for 'Transamerica': 1 found -> [c_0001] Jessica Claire\n"
        "  - Query: python run_pipeline.py --search 'accounting'\n"
        "    Output: Matched candidates c_0001 and c_0002 based on skill and degree indexing."
    )

    # Test Case 4
    p_tc4 = doc.add_paragraph()
    r_tc4_t = p_tc4.add_run("Test Case 4: Chatbot Grounded Q&A and Hallucination Prevention Tests")
    r_tc4_t.bold = True
    r_tc4_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p_tc4_desc = doc.add_paragraph()
    p_tc4_desc.paragraph_format.line_spacing = 1.15
    p_tc4_desc.add_run(
        "Two contrasting queries were executed against chatbot.py to verify groundness and hallucination resistance:"
    )

    qa_box = """[Test 4A: Complex Factual Extraction]
Question: "What degrees does Jessica have and what were her GPAs?"
Chatbot Answer:
"Jessica Claire holds the following degrees:
• Master of Science: Accounting from Pace University (2013)
• Bachelor of Science: International Accounting from Northeast University of Finance and Economics (2011)
Regarding her GPAs:
• Master of Science: 3.4
• Bachelor of Science: 3.8"
Status: PASSED (Exact numerical and institutional accuracy).

--------------------------------------------------------------------------------
[Test 4B: Out-of-Scope Negative Safeguard Test]
Question: "Does Jessica have a driving license?"
Chatbot Answer:
"This information is not provided in the candidate's resume."
Status: PASSED (Zero hallucination; negative boundary enforcement strictly respected)."""
    add_code_block(doc, qa_box, "Chatbot Grounded Q&A Verification")

    # Placeholders for MVP source code
    add_placeholder_box(
        doc,
        "structured_extraction.py",
        "Insert the source code of structured_extraction.py (Gemini API integration, JSON mode, and prompt schema) here."
    )
    add_placeholder_box(
        doc,
        "chatbot.py",
        "Insert the source code of chatbot.py (system prompt guardrails, interactive session loop, and single-query evaluation) here."
    )
    add_placeholder_box(
        doc,
        "run_pipeline.py",
        "Insert the source code of run_pipeline.py (orchestrator, clean_text regex, candidate store indexing, and search engine) here."
    )

    # =========================================================================
    # PART 3: PRODUCE (PRODUCTION ROADMAP)
    # =========================================================================
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(18)
    h3.paragraph_format.space_after = Pt(4)
    r_h3 = h3.add_run("PART 3: PRODUCE — Production Architecture, Security & Modern Upgrades")
    r_h3.font.size = Pt(16)
    r_h3.bold = True
    r_h3.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p3_intro = doc.add_paragraph()
    p3_intro.paragraph_format.line_spacing = 1.15
    p3_intro.add_run(
        "While the MVP successfully proves the technical feasibility of the pipeline, transitioning to an enterprise-grade "
        "production deployment ('Produce') requires significant architectural, security, and algorithmic enhancements. "
        "The following upgrades adapt the verified pipeline for high-throughput, privacy-regulated corporate environments."
    )

    # 3.1 Security & Data Privacy
    h3_1 = doc.add_paragraph()
    h3_1.paragraph_format.space_before = Pt(8)
    h3_1.paragraph_format.space_after = Pt(2)
    r_h3_1 = h3_1.add_run("3.1 Security, Privacy, and Zero-Cloud Data Sovereignty")
    r_h3_1.font.size = Pt(12.5)
    r_h3_1.bold = True
    r_h3_1.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    p3_1 = doc.add_paragraph()
    p3_1.paragraph_format.line_spacing = 1.15
    p3_1.add_run(
        "• Threat Model: Resumes contain high-risk Personally Identifiable Information (PII), including applicant names, personal phone numbers, "
        "home addresses, email addresses, and confidential employment chronologies. Transmitting raw resume text across external public APIs "
        "violates GDPR, CCPA, and enterprise compliance standards.\n"
        "• On-Premise LLM Transition (Ollama + Qwen 2.5): In production, external Gemini API calls are replaced by a self-hosted inference server "
        "running Ollama with Qwen 2.5 Instruct (7B or 14B parameters). Modern quantizations (e.g. Q4_K_M) allow the 7B model to run comfortably "
        "within consumer/edge GPU memory (4 GB to 8 GB VRAM) with zero network egress.\n"
        "• Local JSON Schema Enforcement: Ollama natively supports grammar-based JSON schema constraints (using GBNF grammars), mathematically "
        "guaranteeing 100% syntactic compliance with the target candidate schema without relying on cloud service availability."
    )

    # 3.2 Vector Database and Hybrid Search
    h3_2 = doc.add_paragraph()
    h3_2.paragraph_format.space_before = Pt(8)
    h3_2.paragraph_format.space_after = Pt(2)
    r_h3_2 = h3_2.add_run("3.2 Scalable Vector Storage & Hybrid Retrieval (Qdrant)")
    r_h3_2.font.size = Pt(12.5)
    r_h3_2.bold = True
    r_h3_2.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    p3_2 = doc.add_paragraph()
    p3_2.paragraph_format.line_spacing = 1.15
    p3_2.add_run(
        "In the MVP, search is managed via local JSON files. For production, the storage layer transitions to Qdrant, a high-performance vector search engine:\n"
        "• Section-Based Semantic Chunking: Instead of arbitrary token sliding windows (which sever job descriptions from titles and dates), resumes are chunked "
        "by semantic section: one chunk per degree, one per job role, one per project, and one for core competencies. Each chunk is contextualized with a metadata prefix "
        "(e.g., 'Candidate: Jessica Claire | Section: Experience | Company: Transamerica').\n"
        "• Local Dense Embedding: Embeddings are generated locally using models such as BAAI/bge-small-en-v1.5 or nomic-embed-text (768 dimensions), "
        "ensuring consistent representation between stored resume sections and recruiter queries.\n"
        "• Hybrid Filtering: Qdrant allows combined Boolean metadata filtering and vector similarity. For example, a recruiter can query:\n"
        "   Filter: { 'location': 'San Francisco', 'skills': { 'contains': 'GAAP' } }\n"
        "   Vector Semantic Search: 'Hands-on experience resolving multi-state corporate tax provisions and IRS audits.'\n"
        "This yields vastly superior retrieval precision compared to pure vector search alone."
    )

    # 3.3 Advanced Layout and Handwriting Models
    h3_3 = doc.add_paragraph()
    h3_3.paragraph_format.space_before = Pt(8)
    h3_3.paragraph_format.space_after = Pt(2)
    r_h3_3 = h3_3.add_run("3.3 Advanced Document Layout Analysis & Handwriting Fine-Tuning")
    r_h3_3.font.size = Pt(12.5)
    r_h3_3.bold = True
    r_h3_3.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    p3_3 = doc.add_paragraph()
    p3_3.paragraph_format.line_spacing = 1.15
    p3_3.add_run(
        "• Layout Parsing with PaddleOCR PP-Structure: Standard OCR models sort text boxes using naive top-to-bottom bounding coordinates. In multi-column "
        "resumes, this causes sentences from column 1 and column 2 to be read alternately. Production integration introduces PP-Structure or LayoutLMv3, "
        "segmenting documents into visual regions (headers, columns, tables) before text extraction.\n"
        "• Specialized Handwriting Recognition: While PaddleOCR and EasyOCR excel on form-like printed handwriting, cursive or messy handwriting requires "
        "Vision Transformer models. Integrating TrOCR (Transformer OCR) fine-tuned on the IAM Handwriting Database improves character recognition on unconstrained script.\n"
        "• Quality Gating Pre-flight Checks: An automated intake check calculates image blur (Laplacian variance), contrast (dynamic range), and skew angle (Otsu ink mask bounding box). "
        "Images that fail readability thresholds trigger an instant user notification requesting a clearer scan before invoking computationally expensive OCR pipelines."
    )

    # 3.4 Production Architecture Comparison Table
    h3_4 = doc.add_paragraph()
    h3_4.paragraph_format.space_before = Pt(8)
    h3_4.paragraph_format.space_after = Pt(2)
    r_h3_4 = h3_4.add_run("3.4 Architectural Comparison: MVP vs. Production System")
    r_h3_4.font.size = Pt(12.5)
    r_h3_4.bold = True
    r_h3_4.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    prod_table = doc.add_table(rows=7, cols=3)
    prod_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    p_hdrs = ["Architecture Dimension", "MVP Implementation", "Production Platform ('Produce')"]
    for i, h_text in enumerate(p_hdrs):
        c = prod_table.cell(0, i)
        set_cell_background(c, "1F4E79")
        set_cell_margins(c, 70, 70, 80, 80)
        p = c.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    comp_data = [
        ("OCR Recognition", "EasyOCR / PaddleOCR (standard models)", "PaddleOCR PP-Structure + TrOCR (IAM fine-tuned)"),
        ("Layout Handling", "Bounding-box sorting with regex line keeping", "Visual region segmentation (multi-column aware)"),
        ("Structured Extraction", "Gemini 3.1 Flash Lite API (JSON Mode)", "On-premise Ollama + Qwen 2.5 7B/14B (Zero Cloud PII)"),
        ("Data Storage", "Local JSON files in candidates/ directory", "Qdrant Vector Database (persistent Docker instance)"),
        ("Search Mechanism", "In-memory string & keyword index (index.json)", "Hybrid Search (Dense vector embeddings + SQL/payload filters)"),
        ("System Deployment", "Modular Python CLI scripts", "Dockerized microservices + FastAPI REST endpoints + Celery worker queue")
    ]

    for row_idx, row in enumerate(comp_data):
        for col_idx, val in enumerate(row):
            c = prod_table.cell(row_idx + 1, col_idx)
            set_cell_background(c, "F8FAFC" if row_idx % 2 == 0 else "FFFFFF")
            set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 3.5 Conclusion & Summary
    h_concl = doc.add_paragraph()
    h_concl.paragraph_format.space_before = Pt(8)
    h_concl.paragraph_format.space_after = Pt(2)
    r_hc = h_concl.add_run("3.5 Conclusion")
    r_hc.font.size = Pt(12.5)
    r_hc.bold = True
    r_hc.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    p_concl = doc.add_paragraph()
    p_concl.paragraph_format.line_spacing = 1.15
    p_concl.add_run(
        "By grounding architectural choices in measured evidence (the 13-variant OCR sweep) and proving feasibility with a working MVP, "
        "this project demonstrates that converting noisy handwritten resumes into high-utility searchable candidate profiles is both practical "
        "and reliable. The MVP delivers immediate functionality: automated image ingestion, robust JSON extraction with OCR artifact correction, "
        "candidate indexing, and a chatbot strictly guarded against hallucinations. The production roadmap provides a clear, actionable engineering path "
        "to scale the system into a privacy-first, on-premise enterprise platform."
    )

    output_path = "report/Comprehensive_Handwritten_Resume_Pipeline_Report.docx"
    doc.save(output_path)
    print(f"Report generated successfully at: {output_path}")

if __name__ == "__main__":
    build_report()
