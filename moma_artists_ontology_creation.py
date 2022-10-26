
from asyncore import read
from pickletools import read_decimalnl_long
from rdflib import Graph, RDF, RDFS, Namespace, Literal, URIRef, XSD
from SPARQLWrapper import SPARQLWrapper, JSON
import csv
import pandas as pd
from pycountry import countries
from tqdm import tqdm
from time import sleep
import math


def check_if_string_is_a_country_name(string):
    for country in list(countries):
        if country.name == string:
            return True
    return False


reader = csv.reader(open('nationalites.csv', 'r'))
nationalites = {}
for row in reader:
    k, v = row
    nationalites[k] = v


def get_abstract_of_the_artist_from_dbedpia(artist_name):
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        query = """
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            SELECT ?abstract
            WHERE {
                dbr:%s dbo:abstract ?abstract .
            }
            """ % normalize_name(artist_name)

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            return result['abstract']['value']
    except:
        return 'None'


def get_city_of_birth_from_dbpedia(artist_name):
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        query = """
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            SELECT ?city
            WHERE {
                dbr:%s dbo:birthPlace ?city .
            }
            """ % normalize_name(artist_name)

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            return result['city']['value'].split('/')[-1]
    except:
        return 'None'


def convert_nationality_to_country_name(nationality):
    try:
        return nationalites[nationality]
    except:
        return 'None'


def normalize_name(name):

    return str(name).lstrip().rstrip().replace(" ", "_").replace('"', '')


def serialize_graph(g):
    # g.serialize() returns a string
    print(g.serialize(format='turtle'))


g = Graph()

g.parse("./turtle_files/base.ttl", format="turtle")

ex = Namespace(
    "http://www.semanticweb.org/ontologies/2022/9/group_99#")

owl = Namespace("http://www.w3.org/2002/07/owl#")

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

dbr = Namespace("http://dbpedia.org/resource/")

df = pd.read_csv(
    './Collections/Moma_Collection/artists.csv')
start = 3000
end = 4000

for index, row in tqdm(df[start:end].iterrows(), total=df.shape[0]):
    name = normalize_name(row['Name'])
    nationality = URIRef(
        dbr[normalize_name(convert_nationality_to_country_name(row['Nationality']))])

    abstract = get_abstract_of_the_artist_from_dbedpia(name)
    gender = row['Gender']
    birth_year = row['Birth Year']
    death_year = row['Death Year']

    city = 'None'
    if (abstract is not None):
        if ("artist" in abstract):
            city = get_city_of_birth_from_dbpedia(name)
            if (check_if_string_is_a_country_name(city)):
                city = 'None'

    artist = URIRef(ex[normalize_name(name)])
    city = URIRef(dbr[normalize_name(city)])

    if (city != 'None'):
        g.add((artist, ex.bornIn, city))

    if (math.isnan(birth_year) == False):
        g.add((artist, ex.bornAt, Literal(
            int(birth_year), datatype=XSD.nonNegativeInteger)))
    if (math.isnan(death_year) == False):
        g.add((artist, ex.diedAt, Literal(
            int(death_year), datatype=XSD.nonNegativeInteger)))

    g.add((artist, ex.hasGender, Literal(str(gender))))
    g.add((artist, ex.hasName, Literal(str(row['Name']).replace('"', ''))))
    g.add((artist, ex.hasNationality, nationality))


serialize_graph(g)


# save graph in turtle format
g.serialize(destination='./turtle_files/moma_artists_' +
            str(start) + '_' + str(end) + '.ttl', format='turtle')
