## Overview

This document describes the process and requirements for "rehydrating" sanitized text documents. The goal is to take a text file where all sensitive entities (such as people, organizations, locations, and numbers) have been replaced with placeholders (e.g., [ENTITY], [NUMBER]), and generate a new version where each placeholder is replaced with plausible but fake data. The final output should closely mimic the structure, formatting, and (if possible) the layout of the original document, but with all sensitive information replaced.

## Goals

- Replace every [ENTITY], [NUMBER], and similar placeholders in sanitized text with realistic, non-sensitive fake data.
- Ensure that no real or famous names, numbers, or PII are used in the replacements.
- Preserve the structure, formatting, and (if possible) the layout of the original document.
- Enable the generation of a new PDF that visually resembles the original, but contains only anonymized, synthetic data.

## Core Requirements

- The rehydration process must use a local LLM or a deterministic fake data generator (e.g., Faker) to create replacements for each placeholder.
- The LLM or generator must be instructed to never use real or famous names, numbers, or organizations.
- The output must maintain the original document's structure, including paragraphs, tables, and section headings.
- No commentary, explanation, or "thoughts" from the LLM should be included in the output—only the rehydrated document content.
- The process should be efficient, ideally processing the entire document or large chunks at once, rather than one placeholder at a time.
- The final output should be suitable for conversion back into a PDF that matches the original's appearance as closely as possible, but with all sensitive data replaced.

## Reference Files

- `text_output_sanitized/` — Directory containing sanitized text files with placeholders for sensitive data.
- `hydrate_text.py` — Script that performs the rehydration process, calling a local LLM or fake data generator to replace placeholders.
- `text_output_rehydrated/` — Directory where the rehydrated text files are saved.
- `instructions/instructions-format.txt` — This file, which defines the required format for documentation in the instructions folder.
