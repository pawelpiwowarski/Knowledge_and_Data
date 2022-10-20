

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

df = pd.read_csv('./Collections/Rijksmuseum_Collection/rijksmuseum_data.csv')
API_KEY = config('Rijks_Api_Key')


def normalize_name(name):
    return_val = name.rstrip()
    return return_val.lstrip().replace('(stad)', '').replace('(', '').replace(')', '').replace('-', '_')


row_list = []
for index, objNumber in (enumerate(tqdm(df['objectInventoryNumber'][0:10000]))):
    try:
        print(index)
        dict = {}
        url = 'https://www.rijksmuseum.nl/api/nl/collection/%s?key=%s' % (
            objNumber, API_KEY)

        response = requests.get(url).json()['artObject']
        title = (response['title'])
        image_url = ''
        if (response['webImage'] is not None):
            image_url = (response['webImage']['url'])

        if (len(response['materials']) > 0):
            material = (response['materials'][0])
        colors = response['normalized32Colors']

        if (len(response['dimensions']) > 0):
            dimensions = str(response['dimensions'][0]['value']) + \
                " x " + str(response['dimensions'][1]['value'])
        maker = (response['principalMaker'])

        dict.update({"title": title, "url": image_url, "material": material,
                    "colors": colors, "dimensions": dimensions, "artist": maker})

        row_list.append(dict)
    except:
        pass


expoort_data_frame = pd.DataFrame(row_list)


expoort_data_frame.to_csv(
    './Collections/Rijks_Collection/Final_Arwork_Data_Rijks.csv', index=False)
