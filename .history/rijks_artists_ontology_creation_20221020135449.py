
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
g.parse("./turtle_files/base.ttl", format="turtle")


ex = Namespace(
    "http://www.semanticweb.org/ontologies/2022/9/group_99#")

owl = Namespace("http://www.w3.org/2002/07/owl#")

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

dbr = Namespace("http://dbpedia.org/resource/")
df = pd.read_csv(
    './Collections/Rijksmuseum_Collection/Final_Rijks_Data/Final_Artist_Data_Rijks.csv')


for index, row in df.iterrows():

    name = row['name']
    city = row['city']
    birthDate = row['birthDate']
    deathDate = row['deathDate']
    occupation = row['occupation']
    country = row['nationality']
    # create a new artist
    artist = URIRef(ex[normalize_name(name)])
    city = URIRef(dbr[normalize_name(city)])

    g.add((artist, ex.bornIn, city))
    g.add((artist, ex.bornAt, Literal(str(birthDate), datatype=XSD.nonNegativeInteger)))
    g.add((artist, ex.diedAt, Literal(str(deathDate), datatype=XSD.nonNegativeInteger)))
    g.add((artist, ex.hasName, Literal(name)))
    g.add((artist, ex.hasNationality, URIRef(dbr[normalize_name(country)])))


serialize_graph(g)


# save graph in turtle format
g.serialize(
    destination='./turtle_files/rijks_artists_final.ttl', format='turtle')
