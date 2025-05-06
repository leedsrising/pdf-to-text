import os
import re
from pathlib import Path

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
LLM_API_BASE = os.getenv("LLM_API_BASE", "http://localhost:1234/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "lm-studio")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-r1-distill-qwen-7b")

client = openai.OpenAI(
    base_url=LLM_API_BASE,
    api_key=LLM_API_KEY,
)

def generate_fake_entity(entity_text, entity_type):
    prompt = (
        f"Replace the following {entity_type} with a plausible but fake example of that entity type. "
        f"Only return the fake {entity_type}, nothing else."
    )
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
        temperature=0.9,
    )
    return response.choices[0].message.content.strip()

def rehydrate_text(text):
    # Replace [ENTITY] and [NUMBER] with LLM-generated fakes
    def replacer(match):
        placeholder = match.group(0)
        # Optionally, you can pass some context (e.g., surrounding text)
        return generate_fake_entity(placeholder, "entity")
    return re.sub(r'\[ENTITY\]|\[NUMBER\]', replacer, text)

def rehydrate_full_document(text):
    print(f"Splitting text into chunks (length: {len(text)} chars)...")
    chunks = chunk_text(text, max_tokens=3000)
    print(f"Chunking complete. Number of chunks: {len(chunks)}")
    hydrated_chunks = []
    print(f"Total chunks to process: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Processing chunk {i+1}/{len(chunks)} ---")
        print(f"Chunk length: {len(chunk)} characters")
        print(f"Chunk preview: {repr(chunk[:200])}...")  # Show first 200 chars
        prompt = (
            f"Replace every [ENTITY] and [NUMBER] in the following document with plausible but fake"
            f"values. Do not use any real or famous names or numbers. Return ONLY the fully"
            f"rehydrated document, preserving the structure and formatting."
            f"Do not include any explanation, commentary, or thoughts.\n\n"
            f"Document:\n"
            f"{chunk}"
        )
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.9,
            )
            hydrated = response.choices[0].message.content.strip()
            print(f"Chunk {i+1} processed successfully. Output length: {len(hydrated)} characters")
            hydrated_chunks.append(hydrated)
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")
            hydrated_chunks.append("[ERROR IN CHUNK]")
    return "\n".join(hydrated_chunks)

def chunk_text(text, max_tokens=3000):
    chunks = []
    iteration = 0
    while len(text) > max_tokens:
        iteration += 1
        print(f"  [chunk_text] Iteration {iteration}, remaining text: {len(text)} chars")
        split_at = text.rfind('\n', 0, max_tokens)
        if split_at <= 0:
            split_at = max_tokens
        chunks.append(text[:split_at])
        text = text[split_at:]
    if text:
        chunks.append(text)
    print(f"Chunking complete. Number of chunks: {len(chunks)}")
    return chunks

def process_files():
    input_dir = Path('text_output_sanitized')
    output_dir = Path('text_output_rehydrated')
    output_dir.mkdir(exist_ok=True)

    for input_file in input_dir.glob('*.txt'):
        print(f"\n=== Processing file: {input_file.name} ===")
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        hydrated_text = rehydrate_full_document(text)
        output_file = output_dir / input_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(hydrated_text)
        print(f"Created rehydrated version: {output_file.name}")

if __name__ == "__main__":
    process_files()
