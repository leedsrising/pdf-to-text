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
    def __init__(self, embedding_model):
        self.model = embedding_model
        
        # Create embeddings for entity-like concepts
        self.entity_concepts = [
            "business name",
            "company name",
            "organization name",
            "real estate property",
            "investment firm",
            "development project",
            "financial institution",
            "property manager",
            "real estate fund",
            "market location",
            "business entity"
        ]
        self.entity_embeddings = self.model.encode(self.entity_concepts)
    
    def is_likely_entity(self, text: str, context: str = "") -> Tuple[bool, float]:
        # Combine text with context if available
        text_to_analyze = f"{context} {text}" if context else text
        
        # Get embedding for the text
        text_embedding = self.model.encode([text_to_analyze])[0]
        
        # Calculate similarity with entity concepts
        similarities = np.dot(self.entity_embeddings, text_embedding) / (
            np.linalg.norm(self.entity_embeddings, axis=1) * np.linalg.norm(text_embedding)
        )
        
        max_similarity = np.max(similarities)
        
        # Consider additional structural features
        structural_indicators = [
            text[0].isupper(),  # Starts with capital letter
            any(word[0].isupper() for word in text.split()),  # Contains capitalized words
            bool(re.search(r'\b(?:LLC|LP|Inc|Corp|Partners|Group)\b', text)),  # Common business suffixes
            len(text.split()) >= 2  # Multiple words
        ]
        
        structural_score = sum(structural_indicators) / len(structural_indicators)
        
        # Combine semantic and structural scores
        combined_score = 0.7 * max_similarity + 0.3 * structural_score
        
        return combined_score > 0.6, combined_score

def sanitize_text(text: str, nlp, entity_detector: EntityDetector) -> str:
    doc = nlp(text)
    sanitized = text
    spans_to_replace = []

    # First pass: Process named entities from spaCy
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'GPE', 'FAC', 'LOC']:
            spans_to_replace.append((ent.start_char, ent.end_char, '[ENTITY]'))
        elif ent.label_ in ['MONEY', 'CARDINAL', 'QUANTITY', 'PERCENT']:
            spans_to_replace.append((ent.start_char, ent.end_char, '[NUMBER]'))
        elif ent.label_ in ['DATE', 'TIME']:
            spans_to_replace.append((ent.start_char, ent.end_char, '[DATE]'))

    # Second pass: Use embedding-based entity detection on noun chunks
    for chunk in doc.noun_chunks:
        # Skip if already part of a named entity
        if any(chunk.start_char >= span[0] and chunk.end_char <= span[1] 
               for span in spans_to_replace):
            continue
        
        # Get context (surrounding text)
        context_start = max(0, chunk.start_char - 50)
        context_end = min(len(text), chunk.end_char + 50)
        context = text[context_start:context_end]
        
        is_entity, confidence = entity_detector.is_likely_entity(chunk.text, context)
        if is_entity:
            spans_to_replace.append((chunk.start_char, chunk.end_char, '[ENTITY]'))

    # Additional patterns for specific information types
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
    entity_detector = EntityDetector(embedding_model)
    
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
