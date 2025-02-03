import requests
from bs4 import BeautifulSoup

# Read the language names from a text file with utf-8 encoding
with open('language_names_list.txt', 'r', encoding='utf-8') as file:
    languages = file.readlines()


# Dictionary to store language_name and description
language_descriptions = {}

for language in languages:
    language = language.strip()  # Clean up any surrounding whitespace
    url = f"https://esolangs.org/wiki/{language}"
    response = requests.get(url)
    print(url)
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div with the content
    content_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
    # Check if the div exists before attempting to extract content
    if content_div:
        first_paragraph = content_div.find('p')
        if first_paragraph:
            language_descriptions[language] = first_paragraph.text.strip()
        else:
            language_descriptions[language] = "No description available"
    else:
        language_descriptions[language] = "Content div not found"


# Output the dictionary with language names and their descriptions
print(language_descriptions)
