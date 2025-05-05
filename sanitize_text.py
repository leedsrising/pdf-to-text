import os
import re
from pathlib import Path
from typing import List, Tuple

import numpy as np
import spacy
from sentence_transformers import SentenceTransformer


def load_models():
    # Load spaCy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        os.system("python -m spacy download en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    
    # Load small, efficient embedding model
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Only 80MB
    return nlp, embedding_model

class EntityDetector:
    def __init__(self, embedding_model, allowed_entities=None):
        self.model = embedding_model
        self.allowed_entities = set(allowed_entities or ["Mavik"])  # Default to only Mavik
        
    def is_entity_mention(self, text: str) -> bool:
        if any(allowed.lower() == text.lower() for allowed in self.allowed_entities):
            return False
        # Looser rules:
        # 1. Any word with an ampersand, hyphen, or period
        if re.search(r'[&\-.]', text):
            return True
        # 2. All uppercase or mostly uppercase (including with special chars)
        if len(text) > 1 and sum(1 for c in text if c.isupper()) / len(text) > 0.5:
            return True
        # 3. Any word with a mix of uppercase and lowercase (e.g., "Geneva")
        if any(c.isupper() for c in text) and any(c.islower() for c in text):
            return True
        # 4. Any capitalized word not at the start of a sentence
        if text and text[0].isupper() and text[1:].islower():
            return True
        # 5. Any word with a digit
        if re.search(r'\d', text):
            return True
        # 6. Multi-word phrase with all words capitalized
        if len(text.split()) > 1 and all(w and w[0].isupper() for w in text.split()):
            return True
        return False

def get_ngrams(doc, min_n=1, max_n=4):
    ngrams = []
    for n in range(min_n, max_n+1):
        for i in range(len(doc) - n + 1):
            span = doc[i:i+n]
            ngrams.append((span.start_char, span.end_char, span.text))
    return ngrams

def sanitize_text(text, nlp, entity_detector):
    doc = nlp(text)
    sanitized = text
    spans_to_replace = []

    print(f"Document length: {len(text)}")

    # NER-based replacements (as before)
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'GPE', 'FAC', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE', 'NORP']:
            if ent.text.strip().lower() != "mavik":
                print(f"NER: '{ent.text}' ({ent.start_char}-{ent.end_char}) [{ent.label_}]")
                spans_to_replace.append((ent.start_char, ent.end_char, '[ENTITY]'))
        elif ent.label_ in ['MONEY', 'CARDINAL', 'QUANTITY', 'PERCENT']:
            print(f"NER: '{ent.text}' ({ent.start_char}-{ent.end_char}) [{ent.label_}]")
            spans_to_replace.append((ent.start_char, ent.end_char, '[NUMBER]'))
        elif ent.label_ in ['DATE', 'TIME']:
            print(f"NER: '{ent.text}' ({ent.start_char}-{ent.end_char}) [{ent.label_}]")
            spans_to_replace.append((ent.start_char, ent.end_char, '[DATE]'))

    # N-gram based entity detection (looser, more robust)
    ngram_spans = get_ngrams(doc, 1, 4)
    for start, end, ngram_text in ngram_spans:
        if ngram_text.strip().lower() != "mavik" and entity_detector.is_entity_mention(ngram_text):
            print(f"N-gram: '{ngram_text}' ({start}-{end})")
            spans_to_replace.append((start, end, '[ENTITY]'))

    # Log all spans before filtering
    print("All spans to replace (before filtering):")
    for start, end, label in spans_to_replace:
        print(f"  Span: {start}-{end}, Label: {label}, Text: '{text[start:end]}'")

    # Remove overlapping spans (keep the largest)
    spans_to_replace = sorted(spans_to_replace, key=lambda x: (x[0], -x[1]))
    non_overlapping = []
    last_end = -1
    for start, end, label in spans_to_replace:
        if start >= last_end:
            non_overlapping.append((start, end, label))
            last_end = end

    print("Non-overlapping spans to replace:")
    for start, end, label in non_overlapping:
        print(f"  Span: {start}-{end}, Label: {label}, Text: '{text[start:end]}'")

    # Replace from the end to avoid messing up indices
    for start, end, label in reversed(non_overlapping):
        sanitized = sanitized[:start] + label + sanitized[end:]

    # Final step: remove all remaining digits
    sanitized = re.sub(r'[0-9]', '', sanitized)

    return sanitized

def process_files():
    print("Loading models...")
    nlp, embedding_model = load_models()
    entity_detector = EntityDetector(embedding_model, allowed_entities=["Mavik"])
    
    input_dir = Path('text_output')
    output_dir = Path('text_output_sanitized')
    output_dir.mkdir(exist_ok=True)
    
    for input_file in input_dir.glob('*.txt'):
        print(f"Processing {input_file.name}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        sanitized_text = sanitize_text(text, nlp, entity_detector)
        
        output_file = output_dir / f"sanitized_{input_file.name}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sanitized_text)
        
        print(f"Created sanitized version: {output_file.name}")

if __name__ == "__main__":
    print("Starting text sanitization process...")
    process_files()
    print("Sanitization complete!")
