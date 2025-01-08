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

# Configure AllegroGraph SPARQL endpoint
SPARQL_ENDPOINT = "http://172.178.135.123:10035/repositories/elan"
USERNAME = "admin"
PASSWORD = "b4XsZwmj0x0uE720"


# Helper function to execute SPARQL queries
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
    # Execute the SPARQL query using the helper function
    results = execute_sparql(query)
    if not results["results"]["bindings"]:
        return render_template("language_not_found.html", lang_name=lang_name), 404
    detailed_results = []
    for result in results["results"]["bindings"]:
        property_uri = result["property"]["value"]
        if property_uri.startswith("http://example.org/ontology/esoteric_languages#"):
            property_suffix = property_uri.split("#")[-1]
            property_data = {"display": property_suffix, "link": f"/ontology/{property_suffix}"}
        elif property_uri.startswith("http://www.w3.org/"):
            property_suffix = property_uri.split("#")[-1]
            property_data = {"display": property_suffix, "link": property_uri}
        else:
            property_data = {"display": property_uri, "link": None}
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
    given_language = f'http://example.org/ontology/esoteric_languages#{lang_name}'
    data = {"given_language": given_language}
    headers = {'Content-Type': 'application/json'}
    # Obtain similar languages
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
    # Check if pkl file exists
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
