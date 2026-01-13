import tiktoken

# Default to OpenAI cl100k_base (used by GPT-3.5, GPT-4, embeddings)
enc = tiktoken.get_encoding("cl100k_base")

def get_token_count(text: str) -> int:
    if not text:
        return 0
    return len(enc.encode(text))
