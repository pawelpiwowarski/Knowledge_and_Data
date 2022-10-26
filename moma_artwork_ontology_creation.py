
from re import S
from turtle import title
from rdflib import Graph, RDF, RDFS, Namespace, Literal, URIRef, XSD
from SPARQLWrapper import SPARQLWrapper, JSON
import csv
import pandas as pd
from pycountry import countries
from tqdm import tqdm
from time import sleep
import math
from decouple import config
import requests


def normalize_name(name):
    # replace \ and / with _

    return str(name).lstrip().rstrip().replace(" ", "_").replace('"', '').replace('`', '').replace('|', '').replace(',', '').replace('\\', '')


def serialize_graph(g):
    # g.serialize() returns a string
    print(g.serialize(format='turtle'))


g = Graph()
g.parse("./turtle_files/base.ttl", format="turtle")


musuem_name = 'Moma'

ex = Namespace(
    "http://www.semanticweb.org/ontologies/2022/9/group_99#")

owl = Namespace("http://www.w3.org/2002/07/owl#")

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

dbr = Namespace("http://dbpedia.org/resource/")

dbo = Namespace("http://dbpedia.org/ontology/")


df = pd.read_csv('./Collections/Moma_Collection/artworks.csv')


for index, row in df[0:9000].iterrows():

    index = normalize_name(str(index))
    artist = normalize_name(row['Name'])
    title = (row['Title'])
    material = row['Medium']
    dimensions = str(row['Height (cm)']) + ' x ' + str(row['Width (cm)'])

    artwork = URIRef(ex[index])
    artist = URIRef(ex[artist])
    g.add((artwork, RDF.type, ex.artwork))
    g.add((artist, ex.made, artwork))
    g.add((artwork, ex.hasTitle, Literal((title))))
    g.add((artwork, ex.hasMaterial, Literal(material)))
    g.add((artwork, ex.hasDimensions, Literal(dimensions)))
    g.add((artwork, ex.locatedIn, URIRef(ex[musuem_name])))


serialize_graph(g)


g.serialize(
    destination='./turtle_files/moma_artworks.ttl', format='turtle')
