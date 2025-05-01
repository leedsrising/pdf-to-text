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
        """More aggressive entity detection"""
        # Check if it's an allowed entity first
        if any(allowed.lower() == text.lower() for allowed in self.allowed_entities):
            return False
            
        # Consider it an entity if:
        conditions = [
            text[0].isupper(),  # Starts with capital
            len(text.split()) > 1 and all(word[0].isupper() for word in text.split()),  # All words capitalized
            bool(re.search(r'\b(?:LLC|LP|Inc|Corp|Fund|Capital|Partners|Group|Market|Properties)\b', text)),  # Business terms
            bool(re.search(r'[A-Z]{2,}', text)),  # Acronyms
            bool(re.search(r'\b(?:North|South|East|West|New|Old)\s+[A-Z]', text)),  # Directional names
            any(char.isupper() for char in text[1:])  # Contains capitals after first char
        ]
        
        # More aggressive: consider it an entity if any condition is met
        return any(conditions)

def sanitize_text(text: str, nlp, entity_detector: EntityDetector) -> str:
    doc = nlp(text)
    sanitized = text
    spans_to_replace = []

    # First pass: Process multi-token spans
    for sent in doc.sents:
        for i in range(len(sent)):
            for j in range(i + 1, len(sent) + 1):
                span = sent[i:j]
                if len(span.text.split()) > 1:  # Multi-token span
                    if entity_detector.is_entity_mention(span.text):
                        spans_to_replace.append((span.start_char, span.end_char, '[ENTITY]'))

    # Second pass: Individual tokens and named entities
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'GPE', 'FAC', 'LOC', 'PRODUCT', 'EVENT']:
            text_to_check = ent.text.strip()
            if not any(allowed.lower() == text_to_check.lower() 
                      for allowed in entity_detector.allowed_entities):
                spans_to_replace.append((ent.start_char, ent.end_char, '[ENTITY]'))
        elif ent.label_ in ['MONEY', 'CARDINAL', 'QUANTITY', 'PERCENT']:
            spans_to_replace.append((ent.start_char, ent.end_char, '[NUMBER]'))
        elif ent.label_ in ['DATE', 'TIME']:
            spans_to_replace.append((ent.start_char, ent.end_char, '[DATE]'))

    # Third pass: Check individual tokens
    for token in doc:
        if entity_detector.is_entity_mention(token.text):
            # Skip if already part of a larger span
            if not any(span[0] <= token.idx and token.idx + len(token.text) <= span[1] 
                      for span in spans_to_replace):
                spans_to_replace.append((token.idx, token.idx + len(token.text), '[ENTITY]'))

    # Additional patterns for specific information
    patterns = [
        (r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]'),
        (r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[PHONE]'),
        (r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:million|billion|trillion))?', '[AMOUNT]'),
        (r'\d+(?:\.\d+)?%', '[PERCENTAGE]'),
        (r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:sq\.?\s*ft\.?|SF|square\s*feet)\b', '[AREA]'),
        (r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:acres?)\b', '[AREA]'),
        (r'\b(?:Suite|Ste|Unit|Apt|Building|Bldg|Floor|Fl)\s*#?\s*[A-Za-z0-9-]+\b', '[UNIT]'),
        (r'\b\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b', '[ADDRESS]'),
    ]
    
    for pattern, replacement in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            spans_to_replace.append((match.start(), match.end(), replacement))

    # Sort spans in reverse order to preserve indices during replacement
    spans_to_replace.sort(key=lambda x: x[0], reverse=True)
    
    # Apply replacements
    for start, end, replacement in spans_to_replace:
        sanitized = sanitized[:start] + replacement + sanitized[end:]

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
