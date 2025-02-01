import xml.etree.ElementTree as ET
import re

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
            print("Extracted language names:", language_names)
        break
if not language_names:
    print("No language names found in the 'Language List' page.")
else:
    language_categories = {}
    for page in root.findall('mw:page', namespace):
        title = page.find('mw:title', namespace).text
        if title in language_names:
            last_revision = page.findall('mw:revision', namespace)[-1]
            text_elem = last_revision.find('mw:text', namespace)
            if text_elem is not None and text_elem.text:
                content = text_elem.text
                print(content)
                categories = re.findall(r'\[\[Category:(.*?)]]', content)
                if categories:
                    language_categories[title] = categories
                    print(f"Categories for '{title}': {categories}")
    print("\nFinal dictionary of languages with categories:")
    print(language_categories)
