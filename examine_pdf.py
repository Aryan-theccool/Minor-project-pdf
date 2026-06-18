import fitz

doc = fitz.open(r"d:\minor report\ilovepdf_merged.pdf")

# Examine pages 5, 6, 9, 10, 11, 12 (0-indexed: 4, 5, 8, 9, 10, 11)
for pg_num in [4, 5, 8, 9, 10, 11]:
    page = doc[pg_num]
    print(f"\n{'='*60}")
    print(f"PAGE {pg_num+1} (index {pg_num}) — size: {page.rect}")
    print(f"{'='*60}")
    
    # Get text blocks with font info
    blocks = page.get_text("dict")["blocks"]
    for b_idx, block in enumerate(blocks):
        if "lines" in block:
            for l_idx, line in enumerate(block["lines"]):
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        print(f"  Font: {span['font']}, Size: {span['size']:.1f}, "
                              f"Color: {span['color']}, Origin: ({span['origin'][0]:.1f}, {span['origin'][1]:.1f}), "
                              f"Text: {text[:80]}")

doc.close()
