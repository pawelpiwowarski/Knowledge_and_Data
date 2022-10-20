
from curses import raw
from rdflib import Graph, RDF, RDFS, Namespace, Literal, URIRef, XSD
from SPARQLWrapper import SPARQLWrapper, JSON

import pandas as pd
# open ttl file


# a function to normalize names to be used as dbpedia resource
def normalize_name(name):

    return str(name).lstrip().rstrip().replace(" ", "_")


def invert_names(name):
    name = str(name)
    new_name = name.split(",")
    if len(new_name) > 1:
        return (new_name[1].lstrip() + "_" + new_name[0].lstrip()).replace(" ", "_")
    return 'anonymous'


def serialize_graph(g):
    # g.serialize() returns a string
    print(g.serialize(format='turtle'))


g = Graph()
g.parse("./turtle_files/export.ttl", format="turtle")


ex = Namespace(
    "http://www.semanticweb.org/K&D_Group_99/")

owl = Namespace("http://www.w3.org/2002/07/owl#")

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

dbr = Namespace("http://dbpedia.org/resource/")
df = pd.read_csv(
    './Collections/Rijksmuseum_Collection/ArtistsDataFromRijks.csv')


for index, row in df.iterrows():

    print(row.keys())
    name = row['name']
    city = row['city']
    birthDate = row['birthDate']

    # create a new artist
    artist = URIRef(ex[normalize_name(name)])
    city = URIRef(dbr[normalize_name(city)])

    g.add((city, RDF.type, ex.City))
    g.add((artist, RDF.type, ex.Artist))
    g.add((artist, ex.born_in, city))

    g.add((artist, ex.born_at, Literal(birthDate, datatype=XSD.date)))

    g.add((artist, ex.named, Literal(name)))


serialize_graph(g)


# save graph in turtle format
g.serialize(destination='./turtle_files/rijks_artists.ttl', format='turtle')
