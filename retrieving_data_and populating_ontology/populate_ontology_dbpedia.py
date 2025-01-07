import rdflib
import re
from rdflib.namespace import RDF, XSD


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


from SPARQLWrapper import SPARQLWrapper, JSON

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

sparql = SPARQLWrapper(endpoint_url)
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
dbpedia_data = []
for result in results["results"]["bindings"]:
    language = result["language"]["value"]
    abstract = result["abstract"]["value"]
    designer = result["designer"]["value"]
    dbpedia_data.append((language, abstract, designer))

g = rdflib.Graph()
g.parse("populated_ontology.rdf", format="xml")
ESOLANG = rdflib.Namespace("http://example.org/ontology/esoteric_languages#")
g.bind("esolang", ESOLANG)
for language, abstract, designer in dbpedia_data:
    sanitized_language_name = sanitize_uri_component(
        language.split('/')[-1])
    if sanitized_language_name is None:
        print(f"Skipping invalid DBpedia language: {language}")
        continue
    language_uri = ESOLANG[sanitized_language_name]
    g.add((language_uri, RDF.type, ESOLANG.EsotericLanguage))
    g.add((language_uri, ESOLANG.abstract, rdflib.Literal(abstract, datatype=XSD.string)))
    g.add((language_uri, ESOLANG.designer, rdflib.Literal(designer, datatype=XSD.string)))

g.serialize("updated_ontology_with_dbpedia.rdf", format="xml")
print("Ontology enriched with DBpedia data and saved as 'updated_ontology_with_dbpedia.rdf'.")
