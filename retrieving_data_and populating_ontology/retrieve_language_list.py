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
        revisions = page.findall('mw:revision', namespace)
        if revisions:
            last_revision = revisions[-1]
            text_elem = last_revision.find('mw:text', namespace)
            if text_elem is not None and text_elem.text:
                main_content = text_elem.text.split("==See also==")[0]
                language_names = re.findall(r'\*\s*\[\[([^]|]+)', main_content)
        break
print(language_names)
with open('language_names_list.txt', 'w', encoding='utf-8') as file:
    for name in language_names:
        file.write(name + '\n')
print("Language names saved to 'language_names_list.txt'.")
