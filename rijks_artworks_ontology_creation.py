
from curses import raw
from rdflib import Graph, RDF, RDFS, Namespace, Literal, URIRef, XSD
from SPARQLWrapper import SPARQLWrapper, JSON
import ast
import pandas as pd
# open ttl file


def normalize_name(name):

    return str(name).lstrip().rstrip().replace(" ", "_").replace('"', '').replace('`', '')


def serialize_graph(g):
    # g.serialize() returns a string
    print(g.serialize(format='turtle'))


g = Graph()
g.parse("./turtle_files/artist_rijks_ontology.ttl", format="turtle")


musuem_name = 'RijksMuseum'
ex = Namespace(
    "http://www.semanticweb.org/ontologies/2022/9/group_99#")

owl = Namespace("http://www.w3.org/2002/07/owl#")

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

dbr = Namespace("http://dbpedia.org/resource/")

dbo = Namespace("http://dbpedia.org/ontology/")
df = pd.read_csv(
    './Collections/Rijksmuseum_Collection/Final_Rijks_Data/Final_Artwork_Data_Rijks.csv')


for index, row in df.iterrows():

    title = row['title']
    artist = normalize_name(row['artist'])
    url = row['url']
    material = row['material']
    colors = ast.literal_eval(row['colors'])
    dimeensions = row['dimensions']

    artwork = URIRef(ex[normalize_name(title)])
    artist = URIRef(ex[artist])
    g.add((artwork, RDF.type, ex.artwork))
    g.add((artist, ex.made, artwork))
    g.add((artwork, ex.hasTitle, Literal(title)))
    g.add((artwork, ex.hasUrl, Literal(url)))
    g.add((artwork, ex.hasMaterial, Literal(material)))
    g.add((artwork, ex.hasDimensions, Literal(dimeensions)))
    g.add((artwork, ex.locatedIn, URIRef(ex[musuem_name])))
    if (len(colors) > 0):
        for color in colors:

            g.add((artwork, ex.hasColor, Literal(
                color['hex'] + " " + str(color['percentage']), datatype=XSD.string)))


serialize_graph(g)


g.serialize(
    destination='./turtle_files/final_rijks_ontology.ttl', format='turtle')
