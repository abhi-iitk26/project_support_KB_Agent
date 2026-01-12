import json
import os
from collections import defaultdict
from utils.token_counter import get_token_count


RAW_JSON_FOLDER = "data/raw_json"
OUTPUT_FILE = "data/semantic_chunks.json"


# =====================================================
# 1️⃣ Load & normalize all output_*.json files
# =====================================================
def load_blocks_from_folder(folder=RAW_JSON_FOLDER):
    print(f"📥 Loading JSON files from {folder}")

    all_blocks = []

    for fname in os.listdir(folder):
        if not fname.lower().endswith(".json"):
            continue
        if not fname.startswith("output_"):
            continue

        path = os.path.join(folder, fname)
        print(f"   → {fname}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Original PDF file name
        source_file = data.get("file", fname.replace("output_", "").replace(".json", ".pdf"))

        for item in data.get("content", []):
            text = (item.get("text") or "").strip()
            if not text:
                continue

            all_blocks.append({
                "text": text,
                "page": item.get("page"),
                "source_file": source_file
            })

    print(f"🧠 Total atomic blocks loaded: {len(all_blocks)}")
    return all_blocks


# =====================================================
# 2️⃣ Multi-PDF Semantic Chunking
# =====================================================
def create_semantic_chunks(
    blocks,
    min_tokens=400,
    max_tokens=500,
    overlap_ratio=0.25,
):
    """
    - Never mix different PDFs
    - Chunk by semantic token windows
    - Preserve page numbers
    - Keep overlap
    """

    files = defaultdict(list)
    for b in blocks:
        files[b["source_file"]].append(b)

    semantic_chunks = []
    overlap_tokens = int(max_tokens * overlap_ratio)

    for source_file, file_blocks in files.items():
        print(f"📄 Chunking {source_file}")

        current_text = []
        current_pages = set()

        def flush(force=False):
            nonlocal current_text, current_pages

            if not current_text:
                return

            combined = "\n".join(current_text).strip()
            tokens = get_token_count(combined)

            if not force and tokens < min_tokens:
                return

            # Trim if chunk too long
            while tokens > max_tokens and len(current_text) > 1:
                current_text.pop()
                combined = "\n".join(current_text).strip()
                tokens = get_token_count(combined)

            semantic_chunks.append({
                "content": combined,
                "content_type": "text",
                "token_count": tokens,
                "metadata": {
                    "source_file": source_file,
                    "pages": sorted(current_pages),
                }
            })

            # Build overlap
            overlap_buffer = []
            running = 0
            for part in reversed(current_text):
                t = get_token_count(part)
                if running + t > overlap_tokens:
                    break
                overlap_buffer.insert(0, part)
                running += t

            current_text = overlap_buffer
            current_pages = set()

        # Walk through blocks in reading order
        for block in file_blocks:
            text = block["text"]
            page = block.get("page")

            # Huge paragraph → internal split
            if get_token_count(text) > max_tokens:
                flush(force=True)

                words = text.split()
                chunk = []
                for w in words:
                    chunk.append(w)
                    if get_token_count(" ".join(chunk)) >= max_tokens:
                        semantic_chunks.append({
                            "content": " ".join(chunk),
                            "content_type": "text",
                            "token_count": get_token_count(" ".join(chunk)),
                            "metadata": {
                                "source_file": source_file,
                                "pages": [page] if page else [],
                            }
                        })
                        keep = int(len(chunk) * overlap_ratio)
                        chunk = chunk[-keep:]
                continue

            current_text.append(text)
            if page:
                current_pages.add(page)

            # Soft limit reached
            if get_token_count("\n".join(current_text)) >= max_tokens:
                flush()

        flush(force=True)

    print(f"✅ Created {len(semantic_chunks)} semantic chunks")
    return semantic_chunks


# =====================================================
# 3️⃣ Save
# =====================================================
def save_chunks(chunks, path=OUTPUT_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved → {path}")


# =====================================================
# 4️⃣ Run
# =====================================================
if __name__ == "__main__":
    blocks = load_blocks_from_folder(RAW_JSON_FOLDER)

    chunks = create_semantic_chunks(blocks)

    save_chunks(chunks)

    # Preview
    for c in chunks[:3]:
        print("\nFILE:", c["metadata"]["source_file"])
        print("PAGES:", c["metadata"]["pages"])
        print("TOKENS:", c["token_count"])
        print(c["content"][:200], "...")
