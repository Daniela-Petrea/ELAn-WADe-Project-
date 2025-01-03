from flask import Flask, request, render_template
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

sparql = SPARQLWrapper("http://localhost:3030/esolang/sparql")


@app.route("/")
def home():
    query = """
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?language WHERE {
        ?language rdf:type esolang:EsotericLanguage .
    }
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Extract language names and URL encode them
    languages = []
    for result in results["results"]["bindings"]:
        language_uri = result["language"]["value"]
        if language_uri.startswith("http://example.org/ontology/esoteric_languages#"):
            language_name = language_uri.split("#")[-1]
            languages.append(language_name)

    return render_template("index.html", languages=languages)



@app.route("/language/<path:lang_name>")
def language_details(lang_name):
    # Escape special characters with a backslash
    escaped_lang_name = escape_special_characters(lang_name)

    # Construct the SPARQL query using the escaped language name
    query = f"""
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?property ?value WHERE {{
        esolang:{escaped_lang_name} rdf:type esolang:EsotericLanguage .
        esolang:{escaped_lang_name} ?property ?value .
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Check if results exist
    if not results["results"]["bindings"]:
        return render_template("language_not_found.html", lang_name=lang_name), 404

    # Prepare results
    detailed_results = []
    for result in results["results"]["bindings"]:
        # Process property
        property_uri = result["property"]["value"]
        if property_uri.startswith("http://example.org/ontology/esoteric_languages#"):
            property_suffix = property_uri.split("#")[-1]
            property_data = {"display": property_suffix, "link": f"/ontology/{property_suffix}"}
        elif property_uri.startswith("http://www.w3.org/"):
            property_suffix = property_uri.split("#")[-1]
            property_data = {"display": property_suffix, "link": property_uri}
        else:
            property_data = {"display": property_uri, "link": None}

        # Process value
        value_uri = result["value"]["value"]
        if value_uri.startswith("http://example.org/ontology/esoteric_languages#"):
            value_suffix = value_uri.split("#")[-1]
            value_data = {"display": value_suffix, "link": f"/ontology/{value_suffix}"}
        elif value_uri.startswith("http://www.w3.org/"):
            value_suffix = value_uri.split("#")[-1]
            value_data = {"display": value_suffix, "link": value_uri}
        else:
            value_data = {"display": value_uri, "link": None}

        detailed_results.append({"property": property_data, "value": value_data})

    return render_template("language.html", results=detailed_results, lang_name=lang_name)


@app.route("/ontology/<value>")
def ontology_details(value):
    query = f"""
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?property ?value WHERE {{
        esolang:{value} rdf:type ?type .
        FILTER (?type != esolang:EsotericLanguage)
        esolang:{value} ?property ?value .
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Check if results exist
    if not results["results"]["bindings"]:
        return render_template("ontology_not_found.html", value=value), 404

    # Prepare results
    detailed_results = []
    for result in results["results"]["bindings"]:
        # Process property
        property_uri = result["property"]["value"]
        if property_uri.startswith("http://example.org/ontology/esoteric_languages#"):
            property_suffix = property_uri.split("#")[-1]
            property_data = {"display": property_suffix, "link": f"/ontology/{property_suffix}"}
        elif property_uri.startswith("http://www.w3.org/"):
            property_suffix = property_uri.split("#")[-1]
            property_data = {"display": property_suffix, "link": property_uri}
        else:
            property_data = {"display": property_uri, "link": None}

        # Process value
        value_uri = result["value"]["value"]
        if value_uri.startswith("http://example.org/ontology/esoteric_languages#"):
            value_suffix = value_uri.split("#")[-1]
            value_data = {"display": value_suffix, "link": f"/ontology/{value_suffix}"}
        elif value_uri.startswith("http://www.w3.org/"):
            value_suffix = value_uri.split("#")[-1]
            value_data = {"display": value_suffix, "link": value_uri}
        else:
            value_data = {"display": value_uri, "link": None}

        detailed_results.append({"property": property_data, "value": value_data})

    return render_template("ontology.html", results=detailed_results, value=value)


# Function to escape special characters with a backslash
def escape_special_characters(name):
    # List of characters to escape
    special_characters = ['+', '#', ':', '%', '/', '=', '?', '&', '!', ';', '.', ',', '(', ')']
    
    # Escape each special character by adding a backslash before it
    for char in special_characters:
        name = name.replace(char, f"\\{char}")
    return name

if __name__ == "__main__":
    app.run(debug=True)
