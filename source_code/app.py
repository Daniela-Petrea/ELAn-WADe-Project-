from flask import Flask, request, render_template, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

sparql = SPARQLWrapper("http://localhost:3030/esolang/sparql")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/language/<lang_name>")
def language_details(lang_name):
    query = f"""
    PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
    SELECT ?property ?value WHERE {{
        esolang:{lang_name} ?property ?value.
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return render_template("language.html", results=results, lang_name=lang_name)

# @app.route("/tools/<tool_name>")
# def tool_details(tool_name):
#     query = f"""
#     PREFIX esolang: <http://example.org/ontology/esoteric_languages#>
#     SELECT ?property ?value WHERE {{
#         esolang:{tool_name} ?property ?value.
#     }}
#     """
#     sparql.setQuery(query)
#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()
#     return render_template("tool.html", results=results, tool_name=tool_name)

# @app.route("/sparql", methods=["GET", "POST"])
# def sparql_query():
#     if request.method == "POST":
#         user_query = request.form.get("query")
#         sparql.setQuery(user_query)
#         sparql.setReturnFormat(JSON)
#         results = sparql.query().convert()
#         return jsonify(results)
#     return render_template("sparql.html")

if __name__ == "__main__":
    app.run(debug=True)
