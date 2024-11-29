from flask import Flask, render_template, request
from rdflib import Graph, Namespace

app = Flask(__name__)

# Load the ontology
g = Graph()
ontology_path = "train_ontology.owl"
g.parse(ontology_path, format="xml")

# Define namespaces
EX = Namespace("http://example.org/train#")
g.bind("ex", EX)

# Function to query the ontology
def search_ontology(search_type, search_value):
    if search_type == "train":
        query = f"""
        PREFIX ex: <http://example.org/train#>
        SELECT ?operator ?type ?capacity ?route
        WHERE {{
            ?train a ex:Train ;
                   ex:trainOperator ?operator ;
                   ex:trainType ?type ;
                   ex:hasTrainCapacity ?capacity ;
                   ex:operatesOnRoute ?route .
            FILTER regex(str(?train), "{search_value}", "i")
        }}
        """
    elif search_type == "route":
        query = f"""
        PREFIX ex: <http://example.org/train#>
        SELECT ?routeName ?departure ?arrival ?description ?startStation ?endStation
        WHERE {{
            ?route a ex:Route ;
                   ex:routeName ?routeName ;
                   ex:departureTime ?departure ;
                   ex:arrivalTime ?arrival ;
                   ex:routeDescription ?description ;
                   ex:hasStartStation ?startStation ;
                   ex:hasEndStation ?endStation .
            FILTER regex(?routeName, "{search_value}", "i")
        }}
        """
    elif search_type == "station":
        query = f"""
        PREFIX ex: <http://example.org/train#>
        SELECT ?stationName ?stationLocation ?servedTrain
        WHERE {{
            ?station a ex:Station ;
                     ex:stationName ?stationName ;
                     ex:stationLocation ?stationLocation ;
                     ex:servesTrain ?servedTrain .
            FILTER regex(?stationName, "{search_value}", "i")
        }}
        """
    else:
        return []
    
    results = g.query(query)
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    if request.method == "POST":
        search_type = request.form.get("search_type")
        search_value = request.form.get("search_value")
        results = search_ontology(search_type, search_value)
    return render_template("index.html", results=results, search_type=request.form.get("search_type", ""))

if __name__ == "__main__":
    app.run(debug=True)
