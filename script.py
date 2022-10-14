import pandas as pd


from rdflib import Graph, RDF, RDFS, Namespace, Literal, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON


df = pd.read_csv('./Collections/Rijksmuseum_Collection/data.csv')


def invert_names(name):

    name = str(name)
    new_name = name.split(",")
    if len(new_name) > 1:
        return (new_name[1].lstrip() + "_" + new_name[0].lstrip()).replace(" ", "_")
    return 'anonymous'


names = list(filter(lambda x:  x != 'anonymous' and "(" not in x and '-' not in x and '.' not in x and "'" not in x, df['objectCreator[1]'].map(
    lambda x: str(invert_names(x))).tolist()))


# ask dbpedia for the person's nationality and birthdate
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
for name in names[0:1000]:
    print(name)
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    SELECT ?country 
    WHERE {
        dbr:%s dbo:birthPlace ?city .
        ?city dbo:country ?country .
    }
    """ % name

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        print(name)
        print(result)
