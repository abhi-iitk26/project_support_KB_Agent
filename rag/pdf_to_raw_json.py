import json
import os
from unstructured.partition.pdf import partition_pdf

PDF_FOLDER = "data/pdfs"
OUTPUT_FOLDER = "data/raw_json"

# Get all PDF files from the folder
pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]

print(f"📁 Found {len(pdf_files)} PDF files in {PDF_FOLDER}")

for pdf_file in pdf_files:
    PDF_PATH = os.path.join(PDF_FOLDER, pdf_file)
    OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"output_{os.path.splitext(pdf_file)[0]}.json")

    print(f"\n📄 Loading PDF: {pdf_file}...")

    elements = partition_pdf(
        filename=PDF_PATH,
        strategy="hi_res",
        infer_table_structure=False,
        extract_image_block_types=[],     # Ignore images
        extract_image_block_to_payload=False,
        chunking_strategy=None
    )

    print("📑 Extracting structured text...")

    final_chunks = []
    current_section = "Front Matter"

    for el in elements:

        # Detect chapter / section titles
        if el.category == "Title":
            title = el.text.strip()

            # Filter noisy titles (page numbers, headers, etc.)
            if 3 < len(title) < 80:
                current_section = title

        # Keep only real text
        elif el.category in ["NarrativeText", "ListItem"]:
            meta = el.metadata.to_dict() if el.metadata else {}

            final_chunks.append({
                "chapter": current_section,
                "page": meta.get("page_number"),
                "text": el.text.strip()
            })

    print(f"🧠 Total text chunks: {len(final_chunks)}")

    final_json = {
        "source": os.path.splitext(pdf_file)[0],
        "file": pdf_file,
        "content": final_chunks
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON saved as: {OUTPUT_FILE}")

print(f"\n🎉 All {len(pdf_files)} PDFs processed!")