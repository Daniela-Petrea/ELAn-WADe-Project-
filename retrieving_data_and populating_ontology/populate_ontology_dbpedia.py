import rdflib
import re
from rdflib.namespace import RDF, XSD
from SPARQLWrapper import SPARQLWrapper, JSON

def view_abstract(graph, language_uri):
    # Query the graph for the abstract of the given language URI
    for _, _, abstract in graph.triples((language_uri, ESOLANG.abstract, None)):
        return abstract  # Return the first abstract found
    return None  # Return None if no abstract exists

def sanitize_uri_component(name):
    name = name.strip()
    if not name:
        return None
    if not re.match(r'^[A-Za-z0-9]', name[0]):
        return None
    if not re.match(r'^[A-Za-z0-9.=,!+?:()._~*/ \-]+$', name):
        return None
    name = name.replace(" ", "-")
    return name

# SPARQL query to DBpedia
endpoint_url = "http://dbpedia.org/sparql"
query = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dbc: <http://dbpedia.org/resource/Category:>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?language ?abstract ?designer 
WHERE {
  ?language a dbo:ProgrammingLanguage ;
            dbo:abstract ?abstract ;
            dbp:designer ?designer ;
            dcterms:subject dbc:Esoteric_programming_languages .
  FILTER (lang(?abstract) = "en")  # Filters abstracts in English
}
"""

# Query DBpedia
sparql = SPARQLWrapper(endpoint_url)
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

# Process DBpedia results
dbpedia_data = []
for result in results["results"]["bindings"]:
    language = result["language"]["value"]
    abstract = result["abstract"]["value"]
    designer = result["designer"]["value"]
    dbpedia_data.append((language, abstract, designer))

# Load the ontology
g = rdflib.Graph()
g.parse("populated_ontology_with_abstract_and_url.rdf", format="xml")
ESOLANG = rdflib.Namespace("http://example.org/ontology/esoteric_languages#")
g.bind("esolang", ESOLANG)

for language, abstract, designer in dbpedia_data:
    sanitized_language_name = sanitize_uri_component(language.split('/')[-1])
    if sanitized_language_name is None:
        print(f"Skipping invalid DBpedia language: {language}")
        continue

    language_uri = ESOLANG[sanitized_language_name]

    # Add or skip the abstract based on its existence
    current_abstract = view_abstract(g, language_uri)
    if current_abstract:
        print(f"Language '{sanitized_language_name}' already has an abstract: {current_abstract}")
    else:
        g.add((language_uri, ESOLANG.abstract, rdflib.Literal(abstract, datatype=XSD.string)))
        print(f"Abstract added for language: {sanitized_language_name}")

    # Add other fields unconditionally
    g.add((language_uri, ESOLANG.designer, rdflib.Literal(designer, datatype=XSD.string)))
    print(f"Designer added for language: {sanitized_language_name}")

# Save the updated ontology
g.serialize("updated_ontology_with_dbpedia.rdf", format="xml")
print("Ontology updated with DBpedia abstracts where missing and saved as 'updated_ontology_with_dbpedia.rdf'.")
