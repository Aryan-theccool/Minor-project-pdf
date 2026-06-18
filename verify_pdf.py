import fitz

doc = fitz.open(r"d:\minor report\ilovepdf_merged_fixed.pdf")

pages_to_check = {
    4: "PAGE 5 - Student Undertaking (batch year + typo)",
    5: "PAGE 6 - Acknowledgement (names + enrollment)",
    10: "PAGE 11 - List of Abbreviations",
    11: "PAGE 12 - Abstract",
}

for idx, label in pages_to_check.items():
    page = doc[idx]
    text = page.get_text()
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(text[:1500])
    print("...")

doc.close()
