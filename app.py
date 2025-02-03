import pickle

import numpy as np
import requests
from flask import Flask, request, jsonify, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from flasgger import Swagger, swag_from

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)
# openapi documentation at http://localhost:5000/apidocs
# SPARQL_ENDPOINT = "http://localhost:3030/esolang/sparql"
# Configure AllegroGraph SPARQL endpoint
SPARQL_ENDPOINT = "http://104.42.227.77:10035/repositories/elan"
USERNAME = "admin"
PASSWORD = "ZASvqUl72zRDtyQu"


def execute_sparql(query):
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setCredentials(USERNAME, PASSWORD)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return results
    except Exception as e:
        return {"error": str(e)}


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/languages/<path:lang_name>", methods=['GET'])
@swag_from({
    "parameters": [
        {
            "name": "lang_name",
            "in": "path",
            "type": "string",
            "required": True,
            "description": "The name of the language to fetch details about"
        }
    ],
    "responses": {
        200: {
            "description": "Details of the specified language",
            "examples": {
                "application/json": {"property": "value"}
            }
        },
        404: {
            "description": "Language not found"
        }
    }
})
def language_details(lang_name):
    escaped_lang_name = escape_special_characters(lang_name)
    query = f"""
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?property ?value WHERE {{
        esolang:{escaped_lang_name} rdf:type esolang:EsotericLanguage .
        esolang:{escaped_lang_name} ?property ?value .
    }}
    """
    results = execute_sparql(query)
    print(results)

    if not results["results"]["bindings"]:
        return render_template("language_not_found.html", lang_name=lang_name), 404

    detailed_results = []

    for result in results["results"]["bindings"]:
        property_uri = result["property"]["value"]
        if property_uri.startswith("http://example.org/ontology/esoteric_languages#"):
            property_suffix = property_uri.split("#")[-1]
            property_data = {"display": property_suffix, "link": None}
        elif property_uri.startswith("http://www.w3.org/"):
            property_suffix = property_uri.split("#")[-1]
            property_data = {"display": property_suffix, "link": None}
        else:
            property_data = {"display": property_uri, "link": None}

        value_uri = result["value"]["value"]
        if value_uri.startswith("http://example.org/ontology/esoteric_languages#"):
            value_suffix = value_uri.split("#")[-1]
            value_data = {"display": value_suffix, "link": f"/ontology/{value_suffix}"}
        elif value_uri.startswith("http://www.w3.org/"):
            value_suffix = value_uri.split("#")[-1]
            value_data = {"display": value_suffix, "link": value_uri}
        elif value_uri.startswith("https://esolangs.org/wiki/"):
            value_data = {"display": value_uri, "link": value_uri}
        else:
            value_data = {"display": value_uri, "link": None}

        detailed_results.append({"property": property_data, "value": value_data})
    detailed_results.sort(key=lambda x: x["property"]["display"].lower())  # Case-insensitive sorting

    # Obtain similar languages
    given_language = f'http://example.org/ontology/esoteric_languages#{lang_name}'
    data = {"given_language": given_language}
    headers = {'Content-Type': 'application/json'}

    r = requests.post(url="http://127.0.0.1:5000/get_similar_languages", json=data, headers=headers)
    if r.status_code == 200:
        similar_languages_response = r.json()
    else:
        similar_languages_response = {"similar_languages": []}

    similar_languages = similar_languages_response.get("similar_languages", [])
    similar_languages = [
        {
            "language": lang[0].split("#")[-1] if "#" in lang[0] and lang[0].split("#")[-1] else lang[0],
            "score": lang[1]
        }
        for lang in similar_languages
        if "#" in lang[0] and lang[0].split("#")[-1]  # Exclude invalid or incomplete URLs
    ]

    return render_template("language.html", results=detailed_results, lang_name=lang_name,
                           similar_languages=similar_languages)


@app.route('/languages/search', methods=['GET'])
@swag_from({
    "parameters": [
        {
            "name": "name",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Search term for the language name"
        },
        {
            "name": "page",
            "in": "query",
            "type": "integer",
            "required": False,
            "description": "Page number for pagination"
        },
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "required": False,
            "description": "Number of results per page"
        }
    ],
    "responses": {
        200: {
            "description": "Search results for languages",
            "examples": {
                "application/json": {
                    "data": [{"languageName": "Brainfuck", "releasedYear": "1993"}],
                    "pagination": {"page": 1, "limit": 12}
                }
            }
        }
    }
})
def search_languages():
    search_term = request.args.get('name', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 12))  #
    offset = (page - 1) * limit
    query = f"""
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    SELECT
      (STRAFTER(STR(?language), "http://example.org/ontology/esoteric_languages#") AS ?languageName)
      ?releasedYear
      ?designer
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?computationalClass), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?computationalClasses)

      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?paradigm), "http://example.org/ontology/esoteric_languages#"); 
      separator=", ") AS ?paradigms)

      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?usability), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?usabilities)

      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?technicalCharacteristic), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?technicalCharacteristics)
    WHERE {{
      ?language a esolang:EsotericLanguage .
      FILTER(CONTAINS(LCASE(STRAFTER(STR(?language), "http://example.org/ontology/esoteric_languages#")), LCASE("{search_term}"))) .
      OPTIONAL {{ ?language esolang:releasedYear ?releasedYear . }}
      OPTIONAL {{ ?language esolang:designer ?designer . }}
      OPTIONAL {{ ?language esolang:hasComputationalClass ?computationalClass . }}
      OPTIONAL {{ ?language esolang:hasParadigm ?paradigm . }}
      OPTIONAL {{ ?language esolang:hasUsability ?usability . }}
      OPTIONAL {{ ?language esolang:hasTechnicalCharacteristic ?technicalCharacteristic . }}
    }}
    GROUP BY ?language ?releasedYear ?designer
    ORDER BY ?languageName
    LIMIT {limit} OFFSET {offset}
    """
    results = execute_sparql(query)
    if "error" in results:
        print("Error executing query:", results["error"])
        return jsonify({"error": results["error"]}), 500
    processed_results = []
    for result in results["results"]["bindings"]:
        processed_results.append({
            "languageName": result["languageName"]["value"],
            "releasedYear": result.get("releasedYear", {}).get("value"),
            "designer": result.get("designer", {}).get("value"),
            "computationalClasses": result.get("computationalClasses", {}).get("value", "").split(", "),
            "paradigms": result.get("paradigms", {}).get("value", "").split(", "),
            "usabilities": result.get("usabilities", {}).get("value", "").split(", "),
            "technicalCharacteristics": result.get("technicalCharacteristics", {}).get("value", "").split(", "),
        })
    response = {
        "data": processed_results,
        "pagination": {
            "page": page,
            "limit": limit
        }
    }
    return jsonify(response)


@app.route('/languages/years', methods=['GET'])
@swag_from({
    'tags': ['Languages'],
    'summary': 'Get unique release years of esoteric languages',
    'description': 'Fetch a list of unique years in which esoteric programming languages were released.',
    'responses': {
        200: {
            'description': 'A list of unique release years',
            'schema': {
                'type': 'object',
                'properties': {
                    'years': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_unique_years():
    query = """
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    SELECT DISTINCT ?year
    WHERE {
      ?language a esolang:EsotericLanguage .
      OPTIONAL { ?language esolang:releasedYear ?year . }
    }
    ORDER BY ?year
    """
    results = execute_sparql(query)
    if "error" in results:
        return jsonify({"error": results["error"]}), 500
    # Extract years from the query response
    years = [binding.get('year', {}).get('value') for binding in results["results"]["bindings"] if 'year' in binding]
    return jsonify({"years": years})


@app.route('/languages/designers', methods=['GET'])
@swag_from({
    'tags': ['Languages'],
    'summary': 'Get unique designers of esoteric languages',
    'description': 'Fetch a list of unique designers of esoteric programming languages.',
    'responses': {
        200: {
            'description': 'A list of unique designers',
            'schema': {
                'type': 'object',
                'properties': {
                    'designers': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_unique_designers():
    query = """
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    SELECT DISTINCT ?designer
    WHERE {
      ?language a esolang:EsotericLanguage .
      OPTIONAL { ?language esolang:designer ?designer . }
    }
    ORDER BY ?designer
    """
    results = execute_sparql(query)
    if "error" in results:
        return jsonify({"error": results["error"]}), 500
    # Extract designers from the query response
    designers = [binding.get('designer', {}).get('value') for binding in results["results"]["bindings"] if
                 'designer' in binding]
    return jsonify({"designers": designers})


@app.route('/languages/details', methods=['GET'])
@swag_from({
    'tags': ['Languages'],
    'summary': 'Get detailed information about esoteric languages',
    'description': (
            'Fetch detailed information about esoteric programming languages based on '
            'optional filters like release year and designer. Supports pagination.'
    ),
    'parameters': [
        {
            'name': 'year',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by release year'
        },
        {
            'name': 'designer',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by designer'
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 1,
            'description': 'Page number for pagination'
        },
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 12,
            'description': 'Number of results per page'
        }
    ],
    'responses': {
        200: {
            'description': 'Detailed information about esoteric languages',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'languageName': {'type': 'string'},
                                'releasedYear': {'type': 'string'},
                                'designer': {'type': 'string'},
                                'computationalClasses': {
                                    'type': 'array',
                                    'items': {'type': 'string'}
                                },
                                'paradigms': {
                                    'type': 'array',
                                    'items': {'type': 'string'}
                                },
                                'usabilities': {
                                    'type': 'array',
                                    'items': {'type': 'string'}
                                },
                                'technicalCharacteristics': {
                                    'type': 'array',
                                    'items': {'type': 'string'}
                                }
                            }
                        }
                    },
                    'pagination': {
                        'type': 'object',
                        'properties': {
                            'page': {'type': 'integer'},
                            'limit': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_language_details():
    year = request.args.get('year', None)
    designer = request.args.get('designer', None)
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 12))
    offset = (page - 1) * limit
    query = f"""
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    SELECT
      (STRAFTER(STR(?language), "http://example.org/ontology/esoteric_languages#") AS ?languageName)
      ?releasedYear
      ?designer
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?computationalClass), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?computationalClasses)
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?paradigm), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?paradigms)
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?usability), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?usabilities)
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?technicalCharacteristic), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?technicalCharacteristics)
    WHERE {{
      ?language a esolang:EsotericLanguage .
      OPTIONAL {{ ?language esolang:releasedYear ?releasedYear . }}
      OPTIONAL {{ ?language esolang:designer ?designer . }}
      OPTIONAL {{ ?language esolang:hasComputationalClass ?computationalClass . }}
      OPTIONAL {{ ?language esolang:hasParadigm ?paradigm . }}
      OPTIONAL {{ ?language esolang:hasUsability ?usability . }}
      OPTIONAL {{ ?language esolang:hasTechnicalCharacteristic ?technicalCharacteristic . }}
    """
    if year:
        query += f'FILTER(CONTAINS(?releasedYear, "{year}")) .\n'
    if designer:
        query += f'FILTER(CONTAINS(?designer, "{designer}")) .\n'
    query += f"}} GROUP BY ?language ?releasedYear ?designer ORDER BY ?languageName LIMIT {limit} OFFSET {offset}"
    results = execute_sparql(query)
    if "error" in results:
        return jsonify({"error": results["error"]}), 500
    response_data = []
    for result in results["results"]["bindings"]:
        response_data.append({
            "languageName": result["languageName"]["value"],
            "releasedYear": result.get("releasedYear", {}).get("value"),
            "designer": result.get("designer", {}).get("value"),
            "computationalClasses": result.get("computationalClasses", {}).get("value", "").split(", "),
            "paradigms": result.get("paradigms", {}).get("value", "").split(", "),
            "usabilities": result.get("usabilities", {}).get("value", "").split(", "),
            "technicalCharacteristics": result.get("technicalCharacteristics", {}).get("value", "").split(", "),
        })
    response = {
        "data": response_data,
        "pagination": {
            "page": page,
            "limit": limit,
        }
    }
    return jsonify(response)


@app.route("/language/<path:lang_name>", methods=['GET'])
@swag_from({
    "parameters": [
        {
            "name": "lang_name",
            "in": "path",
            "type": "string",
            "required": True,
            "description": "The name of the language to fetch details about"
        }
    ],
    "responses": {
        200: {
            "description": "Details of the specified language",
            "examples": {
                "application/json": {"property": "value"}
            }
        },
        404: {
            "description": "Language not found"
        }
    }
})
def language_details_specific_language(lang_name):
    escaped_lang_name = escape_special_characters(lang_name)
    query = f"""
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT 
      (STRAFTER(STR(?language), "http://example.org/ontology/esoteric_languages#") AS ?languageName)
      ?releasedYear
      ?designer
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?computationalClass), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?computationalClasses)
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?paradigm), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?paradigms)
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?usability), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?usabilities)
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?technicalCharacteristic), "http://example.org/ontology/esoteric_languages#"); separator=", ") AS ?technicalCharacteristics)
    WHERE {{
      BIND(esolang:{escaped_lang_name} AS ?language)

      ?language rdf:type esolang:EsotericLanguage .

      OPTIONAL {{ ?language esolang:releasedYear ?releasedYear . }}
      OPTIONAL {{ ?language esolang:designer ?designer . }}
      OPTIONAL {{ ?language esolang:hasComputationalClass ?computationalClass . }}
      OPTIONAL {{ ?language esolang:hasParadigm ?paradigm . }}
      OPTIONAL {{ ?language esolang:hasUsability ?usability . }}
      OPTIONAL {{ ?language esolang:hasTechnicalCharacteristic ?technicalCharacteristic . }}
    }}
    GROUP BY ?language ?releasedYear ?designer
    """

    results = execute_sparql(query)
    print(results)

    if "error" in results:
        return jsonify({"error": results["error"]}), 500

    response_data = []
    for result in results["results"]["bindings"]:
        response_data.append({
            "languageName": result["languageName"]["value"],
            "releasedYear": result.get("releasedYear", {}).get("value"),
            "designer": result.get("designer", {}).get("value"),
            "computationalClasses": result.get("computationalClasses", {}).get("value", "").split(", "),
            "paradigms": result.get("paradigms", {}).get("value", "").split(", "),
            "usabilities": result.get("usabilities", {}).get("value", "").split(", "),
            "technicalCharacteristics": result.get("technicalCharacteristics", {}).get("value", "").split(", "),
        })

    response = {"data": response_data}
    return jsonify(response)


def get_sparql_results():
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setCredentials(USERNAME, PASSWORD)
    sparql.setQuery("""
        SELECT ?s ?p ?o WHERE {
            ?s ?p ?o.
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results


# Function to calculate entity embeddings
def calculate_entity_embeddings(results):
    triples = [" ".join([binding["s"]["value"], binding["p"]["value"], binding["o"]["value"]])
               for binding in results["results"]["bindings"]]
    entities = list(set(binding["s"]["value"] for binding in results["results"]["bindings"]))
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(triples)
    entity_embeddings = {}
    for entity in entities:
        entity_triples = [embedding for triple, embedding in zip(triples, embeddings) if entity in triple]
        if entity_triples:
            entity_embeddings[entity] = np.mean(entity_triples, axis=0)
    with open("entity_embeddings.pkl", "wb") as f:
        pickle.dump(entity_embeddings, f)

    return entity_embeddings


def load_entity_embeddings():
    try:
        with open("entity_embeddings.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


@app.route('/compute_embeddings', methods=['GET'])
@swag_from({
    'tags': ['Embeddings'],
    'summary': 'Compute or load entity embeddings',
    'description': (
            'Compute embeddings for all entities in the SPARQL dataset, or load '
            'precomputed embeddings if they already exist.'
    ),
    'responses': {
        200: {
            'description': 'Embeddings computed or loaded successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def compute_embeddings():
    results = get_sparql_results()
    embeddings = load_entity_embeddings()
    if embeddings is None:
        embeddings = calculate_entity_embeddings(results)
    return jsonify({"message": "Embeddings computed or loaded successfully!"})


@app.route('/get_similar_languages', methods=['POST'])
@swag_from({
    'tags': ['Embeddings'],
    'summary': 'Get similar esoteric languages',
    'description': (
            'Given the name of an esoteric language, compute and return the top '
            'similar languages based on precomputed entity embeddings.'
    ),
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'given_language': {
                        'type': 'string',
                        'description': 'The name of the esoteric language to find similar languages for'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'A list of similar languages',
            'schema': {
                'type': 'object',
                'properties': {
                    'given_language': {'type': 'string'},
                    'similar_languages': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'language': {'type': 'string'},
                                'similarity_score': {'type': 'number'}
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request, missing or invalid input'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_similar_languages():
    data = request.get_json()
    given_language = data.get("given_language", None)
    if not given_language:
        return jsonify({"error": "Please provide a valid 'given_language' in the request!"}), 400
    # Load the precomputed entity embeddings
    entity_embeddings = load_entity_embeddings()
    if not entity_embeddings:
        return jsonify({"error": "Embeddings not found! Please compute them first."}), 400
    if given_language not in entity_embeddings:
        return jsonify({"error": f"Entity {given_language} not found in the embeddings!"}), 400
    # Get the embedding for the given language
    given_language_embedding = entity_embeddings[given_language]
    # Compute cosine similarity
    similarities = {
        entity: cosine_similarity([given_language_embedding], [embedding])[0][0]
        for entity, embedding in entity_embeddings.items()
        if entity != given_language
    }
    similarities = {entity: float(score) for entity, score in similarities.items()}
    similar_languages = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:15]
    return jsonify({
        "given_language": given_language,
        "similar_languages": similar_languages
    })


def escape_special_characters(name):
    special_characters = ['+', '#', ':', '%', '/', '=', '?', '&', '!', ';', '.', ',', '(', ')']
    for char in special_characters:
        name = name.replace(char, f"\\{char}")
    return name


@app.route('/compare_languages', methods=['POST'])
@swag_from({
    'tags': ['Comparison'],
    'summary': 'Compare a given language with a similar language',
    'description': 'Fetch detailed information for both the given language and one of its similar languages, then compare them.',
    'parameters': [
        {
            'name': 'given_language',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'given_language': {'type': 'string'}
                }
            }
        },
        {
            'name': 'similar_language',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'similar_language': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Comparison results between the given language and the similar language',
            'schema': {
                'type': 'object',
                'properties': {
                    'comparison': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'property': {'type': 'string'},
                                'given_language_value': {'type': 'string'},
                                'similar_language_value': {'type': 'string'},
                                'similarity': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        },
        400: {'description': 'Bad request'},
        500: {'description': 'Internal server error'}
    }
})
def compare_languages():
    data = request.get_json()
    print(data)

    given_language = data.get('given_language')
    similar_language = data.get('similar_language')

    if not given_language or not similar_language:
        return jsonify({"error": "Both 'given_language' and 'similar_language' must be provided!"}), 400

    print(given_language)
    print(similar_language)
    given_lang_response = language_details_specific_language(given_language)
    similar_lang_response = language_details_specific_language(similar_language)
    given_lang_details = given_lang_response.get_json()
    similar_lang_details = similar_lang_response.get_json()
    print(given_lang_details)
    print(similar_lang_details)
    if "data" not in given_lang_details or "data" not in similar_lang_details:
        return jsonify({"error": "Failed to retrieve language details"}), 500

    given_lang_data = given_lang_details["data"][0] if given_lang_details["data"] else {}
    similar_lang_data = similar_lang_details["data"][0] if similar_lang_details["data"] else {}

    # Extract key details for comparison
    properties = [
        'releasedYear', 'designer', 'computationalClasses', 'paradigms',
        'usabilities', 'technicalCharacteristics'
    ]
    comparison = []
    for prop in properties:
        given_value = given_lang_data.get(prop, 'Not Available')
        similar_value = similar_lang_data.get(prop, 'Not Available')
        if given_value is None or given_value == '' or (isinstance(given_value, list) and not given_value[0]):
            given_value = 'N/A'
        if similar_value is None or similar_value == '' or (isinstance(similar_value, list) and not similar_value[0]):
            similar_value = 'N/A'
        # Determine similarity based on values
        similarity = 'Similar' if given_value == similar_value else 'Different'
        comparison.append({
            'property': prop,
            'given_language_value': given_value,
            'similar_language_value': similar_value,
            'similarity': similarity
        })

    return jsonify({'comparison': comparison})

@app.route("/ontology/<value>")
@swag_from({
    "summary": "Retrieve ontology details",
    "description": "Fetches detailed ontology properties and values for a given esoteric language entity.",
    "parameters": [
        {
            "name": "value",
            "in": "path",
            "type": "string",
            "required": True,
            "description": "The ontology entity to retrieve details for."
        }
    ],
    "responses": {
        200: {
            "description": "Successful response with ontology details.",
            "content": {
                "text/html": {
                    "example": "<html>Ontology details page</html>"
                }
            }
        },
        404: {
            "description": "Ontology entity not found.",
            "content": {
                "text/html": {
                    "example": "<html>Not found</html>"
                }
            }
        }
    }
})
def ontology_details(value):
    query = f"""
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?property ?value WHERE {{
        esolang:{value} rdf:type ?type .
        FILTER (?type != esolang:EsotericLanguage)
        esolang:{value} ?property ?value .
    }}
    """
    results = execute_sparql(query)

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



if __name__ == '__main__':
    app.run()
