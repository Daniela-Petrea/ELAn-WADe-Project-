import xml.etree.ElementTree as ET
import re
import csv


def normalize_category(category_name):
    normalized_name = category_name.strip().lower()
    if normalized_name.endswith("__"):
        print("here")
        normalized_name = normalized_name[:-2]
    if normalized_name.endswith("_"):
        normalized_name = normalized_name[:-1]
    return normalized_name


file_path = '../esolang.xml'
tree = ET.parse(file_path)
root = tree.getroot()
namespace = {'mw': 'http://www.mediawiki.org/xml/export-0.11/'}
target_page_title = "Language list"
language_names = []
for page in root.findall('mw:page', namespace):
    title = page.find('mw:title', namespace).text
    if title == target_page_title:
        last_revision = page.findall('mw:revision', namespace)[-1]
        text_elem = last_revision.find('mw:text', namespace)

        if text_elem is not None and text_elem.text:
            full_text = text_elem.text
            main_content = full_text.split("==See also==")[0]
            language_names = re.findall(r'\*\s*\[\[([^]|]+)', main_content)
            print(f"Extracted {len(language_names)} language names.")
        break

if not language_names:
    print("No language names found in the 'Language List' page.")
else:
    language_categories = {}
    unique_categories = set()
    for page in root.findall('mw:page', namespace):
        title = page.find('mw:title', namespace).text
        if title in language_names:
            last_revision = page.findall('mw:revision', namespace)[-1]
            text_elem = last_revision.find('mw:text', namespace)
            if text_elem is not None and text_elem.text:
                content = text_elem.text
                categories = re.findall(r'\[\[Category:(.*?)]]', content)
                if categories:
                    normalized_categories = [normalize_category(category) for category in categories]
                    language_categories[title] = normalized_categories
                    unique_categories.update(normalized_categories)
                    print(f"Categories for '{title}': {normalized_categories}")
    cleaned_categories = {category.replace("\u200e", "").replace("\u200f", "") for category in unique_categories}
    grouping = {
        "Released Year": [],
        "Programming Paradigm": [],
        "Computational Class": [],
        "Usability": [],
        "Technical Characteristics": [],
        "Specific Language Types or Features": []
    }
    year_pattern = re.compile(r'^\d{4}$')
    programming_paradigm_keywords = {'imperative', 'functional', 'declarative', 'object-oriented', 'prototype'}
    computational_class_keywords = {'turing', 'finite state', 'bounded', 'push-down', 'unknown computational'}
    usability_keywords = {'usability', 'unusable', 'implemented', 'educational', 'games', 'total', 'output only',
                          'non-interactive io', 'no io', 'examples', 'concepts', 'works-in-progress'}
    technical_characteristics_keywords = {'queue', 'stack', 'cell', 'deque', 'binary', 'matrix', 'multi-dimensional',
                                          'particle', 'graphical', 'tree', 'emoji', 'accumulator', 'steganography',
                                          'concurrent'}
    specific_language_types_keywords = {'brainfuck', 'joke', 'compressed', 'cjk', 'low-level', 'high-level',
                                        'turing complete', 'nope', 'quantum', 'bootstrapping', 'deadfish',
                                        'polish notation', 'meta', 'user edited', 'stubs', 'icfp', 'languages',
                                        'algorithmic information', 'alien', 'examples', 'proofs', 'golfing', 'thematic'}


    def classify_category(category):
        normalized_category = category.strip().lower()
        if year_pattern.match(normalized_category):
            return "Released Year"
        elif any(keyword in normalized_category for keyword in programming_paradigm_keywords):
            return "Programming Paradigm"
        elif any(keyword in normalized_category for keyword in computational_class_keywords):
            return "Computational Class"
        elif any(keyword in normalized_category for keyword in usability_keywords):
            return "Usability"
        elif any(keyword in normalized_category for keyword in technical_characteristics_keywords):
            return "Technical Characteristics"
        elif any(keyword in normalized_category for keyword in specific_language_types_keywords):
            return "Specific Language Types or Features"
        return None


    for language, categories in language_categories.items():
        grouped_categories = {group: [] for group in grouping.keys()}
        for category in categories:
            group = classify_category(category)
            if group:
                grouped_categories[group].append(category)
        language_categories[language] = grouped_categories
    output_csv_path = 'esoteric_languages.csv'
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Language"] + list(grouping.keys())
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        for language, grouped_categories in language_categories.items():
            row = {"Language": language}
            for group in grouping.keys():
                row[group] = "; ".join(grouped_categories[group])  # Join categories by group with semicolon
            csv_writer.writerow(row)
    print(f"\nCSV file '{output_csv_path}' created successfully with grouped categories for each language.")
