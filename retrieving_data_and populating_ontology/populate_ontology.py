import rdflib
import csv
import re

g = rdflib.Graph()
g.parse("ELAN.rdf", format="xml")
base_uri = "http://example.org/ontology/esoteric_languages#"
ESOLANG = rdflib.Namespace(base_uri)
OWL = rdflib.OWL
XSD = rdflib.XSD


def sanitize_uri_component(name):
    name = name.strip()
    if not name:
        return None
    if not re.match(r'^[A-Za-z0-9]', name[0]):
        return None  # Skip the language
    if not re.match(r'^[A-Za-z0-9.=,!+?:()._~*/ \-]+$', name):
        return None
    name = name.replace(" ", "-")
    name = name.replace("_", "-")
    return name


def create_individual(graph, class_uri, individual_uri):
    graph.add((individual_uri, rdflib.RDF.type, class_uri))


with open("esoteric_languages.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        language_name = row['Language'].replace(" ", "")
        sanitized_language_name = sanitize_uri_component(language_name)

        if sanitized_language_name is None:
            print(f"Skipping invalid language: {language_name}")
            continue

        language_uri = ESOLANG[sanitized_language_name]

        g.add((language_uri, rdflib.RDF.type, ESOLANG.EsotericLanguage))

        if 'Released Year' in row and row['Released Year']:
            g.add((language_uri, ESOLANG.releasedYear, rdflib.Literal(row['Released Year'], datatype=XSD.string)))

        if 'Computational Class' in row and row['Computational Class']:
            computational_classes = row['Computational Class'].split(";")
            for cclass in computational_classes:
                cclass_uri = ESOLANG[sanitize_uri_component(cclass.strip())]
                if cclass_uri is not None:
                    g.add((language_uri, ESOLANG.hasComputationalClass, cclass_uri))
                    create_individual(g, ESOLANG.ComputationalClass, cclass_uri)

        if 'Programming Paradigm' in row and row['Programming Paradigm']:
            paradigms = row['Programming Paradigm'].split(";")
            for paradigm in paradigms:
                paradigm_uri = ESOLANG[sanitize_uri_component(paradigm.strip())]
                if paradigm_uri:
                    g.add((language_uri, ESOLANG.hasParadigm, paradigm_uri))
                    create_individual(g, ESOLANG.Paradigm, paradigm_uri)

        if 'Usability' in row and row['Usability']:
            usabilities = row['Usability'].split(";")
            for usability in usabilities:
                usability_uri = ESOLANG[sanitize_uri_component(usability.strip())]
                if usability_uri is not None:
                    g.add((language_uri, ESOLANG.hasUsability, usability_uri))
                    create_individual(g, ESOLANG.Usability, usability_uri)

        if 'Technical Characteristics' in row and row['Technical Characteristics']:
            tech_chars = row['Technical Characteristics'].split(";")
            for tech in tech_chars:
                tech_uri = ESOLANG[sanitize_uri_component(tech.strip())]
                if tech_uri is not None:
                    g.add((language_uri, ESOLANG.hasTechnicalCharacteristic, tech_uri))
                    create_individual(g, ESOLANG.TechnicalCharacteristic, tech_uri)

        if 'Specific Language Types or Features' in row and row['Specific Language Types or Features']:
            features = row['Specific Language Types or Features'].split(";")
            for feature in features:
                feature_uri = ESOLANG[sanitize_uri_component(feature.strip())]
                if feature_uri is not None:
                    g.add((language_uri, ESOLANG.hasSpecificTypeOrFeature, feature_uri))
                    create_individual(g, ESOLANG.SpecificTypeOrFeature, feature_uri)

g.serialize("populated_ontology.rdf", format="xml")
print("Ontology populated and saved as 'populated_ontology.rdf'")
