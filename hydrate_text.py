import os
import re
from pathlib import Path

from faker import Faker

fake = Faker()

def fake_entity():
    # Randomly choose a type of entity to fake
    entity_type = fake.random_element(elements=('company', 'name', 'city'))
    if entity_type == 'company':
        return fake.company()
    elif entity_type == 'name':
        return fake.name()
    else:
        return fake.city()

def fake_number():
    # Generate a plausible fake number (int or float)
    if fake.boolean():
        return str(fake.random_int(min=1, max=10000))
    else:
        return "{:.2f}".format(fake.pyfloat(left_digits=2, right_digits=2, positive=True))

def rehydrate_text(text):
    # Replace [ENTITY] and [NUMBER] with fake data
    def replacer(match):
        placeholder = match.group(0)
        if placeholder == '[ENTITY]':
            return fake_entity()
        elif placeholder == '[NUMBER]':
            return fake_number()
        else:
            return placeholder  # In case of other placeholders
    return re.sub(r'\[ENTITY\]|\[NUMBER\]', replacer, text)

def process_files():
    input_dir = Path('text_output_sanitized')
    output_dir = Path('text_output_rehydrated')
    output_dir.mkdir(exist_ok=True)

    for input_file in input_dir.glob('*.txt'):
        print(f"Processing file: {input_file.name}")
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        hydrated_text = rehydrate_text(text)
        output_file = output_dir / input_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(hydrated_text)
        print(f"Created rehydrated version: {output_file.name}")

if __name__ == "__main__":
    process_files()
