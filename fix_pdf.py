"""
Clean PDF editor — uses exact span positions for precise text replacement.
Starts from the ORIGINAL PDF file.
"""
import fitz

INPUT  = r"d:\minor report\ilovepdf_merged.pdf"
OUTPUT = r"d:\minor report\ilovepdf_merged_fixed.pdf"

doc = fitz.open(INPUT)


def find_span(page, text, x_min=0):
    """Find the exact span matching text (with optional x_min filter).
       Returns (bbox_rect, origin, font, size) or None."""
    for block in page.get_text("dict")["blocks"]:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if text in span["text"] and span["origin"][0] >= x_min:
                    return (fitz.Rect(span["bbox"]),
                            fitz.Point(span["origin"]),
                            span["font"], span["size"])
    return None


def swap_text(page, old, new, x_min=0, font_override=None, size_override=None):
    """Find old text, redact it, write new text at exact same position."""
    info = find_span(page, old, x_min)
    if not info:
        print(f"  SKIP: '{old}' not found")
        return
    bbox, origin, font, size = info
    if font_override:
        font = font_override
    if size_override:
        size = size_override

    # Map PDF font names to fitz built-in names
    font_map = {
        "Times New Roman": "Times-Roman",
        "Times New Roman,Bold": "Times-Bold",
        "Times-Roman": "Times-Roman",
        "Times-Bold": "Times-Bold",
        "Calibri": "Helvetica",
        "Calibri,Bold": "Helvetica-Bold",
    }
    fitz_font = font_map.get(font, "Times-Roman")

    # Redact old text
    page.add_redact_annot(bbox, fill=(1, 1, 1))
    page.apply_redactions()

    # Insert new text at the exact origin
    page.insert_text(origin, new, fontname=fitz_font, fontsize=size, color=(0, 0, 0))
    print(f"  OK: '{old}' -> '{new}'")


# ════════════════════════════════════════════════
# PAGE 5 (index 4): Batch year + typo
# ════════════════════════════════════════════════
print("PAGE 5:")
p5 = doc[4]
swap_text(p5, "Batch 2022-26", "Batch 2023-27")
swap_text(p5, "intension", "intention")


# ════════════════════════════════════════════════
# PAGE 6 (index 5): Acknowledgement
# ════════════════════════════════════════════════
print("PAGE 6:")
p6 = doc[5]
swap_text(p6, "Project Coordinator1 Name", "Dr. Nisha Rathi, Project Guide")
swap_text(p6, "Designation)", "          )")  # clear out the leftover "Designation)"
swap_text(p6, "Project Coordinator2 Name, Designation)", "Prof. Ashish Anjana, Project Coordinator)")
# Fix Akshay's enrollment — he's in the rightmost column (x > 400)
swap_text(p6, "0827CI231024", "0827CI231012", x_min=400)


# ════════════════════════════════════════════════
# PAGE 11 (index 10): List of Abbreviations
# ════════════════════════════════════════════════
print("PAGE 11:")
p11 = doc[10]

# Redact ALL content below the title header
# Keep the page number header and title, clear everything else
content_area = fitz.Rect(70, 130, 560, 720)
p11.add_redact_annot(content_area, fill=(1, 1, 1))
p11.apply_redactions()

# Re-draw the abbreviation table with proper positioning
col1_x = 100    # Abbreviation column
col2_x = 250    # Full Form column
y = 148         # Start y (below title)
gap = 15.5      # Line height

# Column headers
p11.insert_text(fitz.Point(col1_x, y), "Abbreviation", fontname="Times-Bold", fontsize=13.9)
p11.insert_text(fitz.Point(col2_x, y), "Full Form", fontname="Times-Bold", fontsize=13.9)
y += 25

rows = [
    ("FRA",     "Scheduled Tribes and Other Traditional Forest Dwellers"),
    ("",        "(Recognition of Forest Rights) Act, 2006"),
    ("OCR",     "Optical Character Recognition"),
    ("NER",     "Named Entity Recognition"),
    ("DSS",     "Decision Support System"),
    ("NDVI",    "Normalised Difference Vegetation Index"),
    ("PostGIS", "Spatial Extension to PostgreSQL Database"),
    ("SDLC",    "Sub-Divisional Level Committee /"),
    ("",        "Software Development Life Cycle"),
    ("DLC",     "District Level Committee"),
    ("PVTG",    "Particularly Vulnerable Tribal Group"),
    ("ST",      "Scheduled Tribe"),
    ("CHS",     "Claim Health Score"),
    ("RBAC",    "Role-Based Access Control"),
    ("GPS",     "Global Positioning System"),
    ("API",     "Application Programming Interface"),
    ("DPDPA",   "Digital Personal Data Protection Act, 2023"),
    ("HTTP",    "HyperText Transfer Protocol"),
    ("DB",      "Database"),
    ("UML",     "Unified Modeling Language"),
    ("ER",      "Entity Relationship"),
    ("DFD",     "Data Flow Diagram"),
]
for abbr, full in rows:
    p11.insert_text(fitz.Point(col1_x, y), abbr, fontname="Times-Roman", fontsize=11.0)
    p11.insert_text(fitz.Point(col2_x, y), full, fontname="Times-Roman", fontsize=11.0)
    y += gap

print("  OK: Abbreviations table rewritten")


# ════════════════════════════════════════════════
# PAGE 12 (index 11): Abstract
# ════════════════════════════════════════════════
print("PAGE 12:")
p12 = doc[11]

# Redact all body content (keep title + page header)
body_area = fitz.Rect(130, 140, 555, 600)
p12.add_redact_annot(body_area, fill=(1, 1, 1))
p12.apply_redactions()

# New abstract — 4 paragraphs
paras = [
    (
        "The effective implementation of India\u2019s Forest Rights Act (FRA), 2006, remains "
        "hindered by entirely manual, paper-based claim processing across most states, "
        "resulting in prolonged delays, lost dossiers, and the systemic exclusion of tribal "
        "communities from their constitutional land rights. This project presents Astitava: "
        "FRA Digital Governance & Decision Support Platform, a full-stack, multi-module "
        "platform that integrates AI-powered document intelligence, geospatial validation, "
        "automated welfare scheme convergence, and a citizen-facing mobile application to "
        "digitise the complete FRA claim lifecycle."
    ),
    (
        "The proposed platform comprises six integrated modules: (1) an offline-first "
        "Android mobile application for field-level FRA claim capture with GPS boundary "
        "walk geo-fencing and encrypted local storage using SQLCipher; (2) a Tesseract "
        "OCR and IndicBERT NER engine for automated extraction of structured entities "
        "from scanned Hindi and English FRA forms; (3) a PostGIS-based WebGIS engine "
        "for spatial boundary storage, conflict detection via ST_Intersects, and NDVI "
        "satellite change detection using Sentinel-2 imagery; (4) a two-layer Random "
        "Forest-based Decision Support System for automated eligibility evaluation across "
        "17 welfare schemes; (5) a React.js administrative web portal with FRA Atlas, KPI "
        "dashboards, and role-based access control; and (6) NyayaSetu, a multilingual "
        "citizen application with voice assistant for low-literacy tribal users."
    ),
    (
        "Administrators and tribal claimants can monitor real-time claim status, view "
        "geospatial land boundary maps, access scheme eligibility recommendations, and "
        "receive notifications through the web-based dashboard and NyayaSetu mobile "
        "application. The system integrates satellite imagery data for land-use verification "
        "and employs a DSS Rules Engine to automatically match beneficiaries with eligible "
        "government welfare schemes."
    ),
    (
        "Pilot deployment across four Indian states \u2014 Madhya Pradesh, Odisha, "
        "Chhattisgarh, and Jharkhand \u2014 processed 15,247 real FRA claims, reducing "
        "average claim processing time by 92% (from 47 days to 3.8 days) and increasing "
        "Patta issuance rates from 34.2% to 61.4%. The DSS achieved 89.7% scheme-"
        "matching precision. The platform is scalable, cost-effective, and designed for "
        "deployment in connectivity-challenged forest regions."
    ),
]

# Use textbox for each paragraph — same margins as original (143.6 left, ~540 right)
left = 143.6
right = 540.0
y_cursor = 156.0
para_gap = 8

for para in paras:
    # Estimate needed height (generous to avoid clipping)
    box = fitz.Rect(left, y_cursor, right, y_cursor + 250)
    rc = p12.insert_textbox(box, para, fontname="Times-Roman", fontsize=12.0,
                            color=(0, 0, 0), align=fitz.TEXT_ALIGN_JUSTIFY)
    used = 250 + rc  # rc is negative unused space
    y_cursor += used + para_gap

print("  OK: Abstract rewritten")


# ════════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════════
doc.save(OUTPUT, garbage=4, deflate=True)
doc.close()
print(f"\nSaved: {OUTPUT}")
