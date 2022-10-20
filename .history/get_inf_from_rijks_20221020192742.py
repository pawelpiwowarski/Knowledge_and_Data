from decouple import config
import requests
import pandas as pd
from time import sleep
from tqdm import tqdm
from SPARQLWrapper import SPARQLWrapper, JSON

API_KEY = config('Rijks_Api_Key')
df = pd.read_csv('./Collections/Rijksmuseum_Collection/rijksmuseum_data.csv')


def get_year_from_date(date):
    return date.split('-')[0]


def normalize_name(name):
    return_val = name.rstrip()
    return return_val.lstrip().replace('(stad)', '').replace('(', '').replace(')', '').replace('-', '_')


def get_country_from_dbpedia(city):
    try:
        print(normalize_name(city))

        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        query = """
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            SELECT ?country
            WHERE {
                dbr:%s dbo:country ?country .
            }
            """ % normalize_name(city)

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            return result['country']['value'].split('/')[-1]
    except:
        return None


rows_list = []


for index, objNumber in (enumerate(tqdm(df['objectInventoryNumber'][5000:10000]))):

    dict = {"name": '', "city": '', "birthDate": '', 'deathDate': '',
            'nationality': '', 'occupation': ''}
    url = 'https://www.rijksmuseum.nl/api/nl/collection/%s?key=%s' % (
        objNumber, API_KEY)
    print(url)
    try:
        response = requests.get(url).json()['artObject']
    except:
        pass

    try:
        if (len(response['principalMakers']) > 2):
            for data in response['principalMakers']:
                nationality = data['placeofBirth']
                dict.update({"name": data['name'], "city": data['placeOfBirth'], "occupation": data['occupation'],
                            "birthDate": get_year_from_date(data['dateOfBirth']), "deathDate": get_year_from_date(data['dateOfDeath'])})

        else:
            nationality = (get_country_from_dbpedia(
                response['principalMakers'][0]['placeOfBirth']))
            dict.update({"name": response['principalMakers'][0]['name'], 'occupation': response['principalMakers'][0]['occupation'][0], 'nationality': nationality, "city": response['principalMakers'][0]
                        ['placeOfBirth'], "birthDate": get_year_from_date(response['principalMakers'][0]['dateOfBirth']), "deathDate": get_year_from_date(response['principalMakers'][0]['dateOfDeath'])})
        rows_list.append(dict)
    except:
        pass
    # show progress bar
    sleep(0.1)


print(rows_list)

expoort_data_frame = pd.DataFrame(rows_list)

expoort_data_frame.to_csv('ArtistsDataFromRijs_5000_10000.csv', index=False)
