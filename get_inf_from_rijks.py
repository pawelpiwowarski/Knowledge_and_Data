from decouple import config
import requests
import pandas as pd
from time import sleep
from tqdm import tqdm

API_KEY = config('Rijks_Api_Key')
df = pd.read_csv('./Collections/Rijksmuseum_Collection/rijksmuseum_data.csv')


def get_year_from_date(date):
    return date.split('-')[0]


rows_list = []


for index, objNumber in (enumerate(tqdm(df['objectInventoryNumber'][0:10000]))):

    dict = {"name": '', "country": '', "birthDate": '', 'url': ''}
    url = 'https://www.rijksmuseum.nl/api/nl/collection/%s?key=%s' % (
        objNumber, API_KEY)
    try:
        response = requests.get(url).json()['artObject']
    except:
        pass

    try:
        if (len(response['principalMakers']) > 2):
            for data in response['principalMakers']:

                dict.update({"name": data['name'], "country": data['placeOfBirth'],
                            "birthDate": get_year_from_date(data['dateOfBirth'])})

        else:
            dict.update({"name": response['principalMakers'][0]['name'], "country": response['principalMakers'][0]
                        ['placeOfBirth'], "birthDate": get_year_from_date(response['principalMakers'][0]['dateOfBirth'])})
        rows_list.append(dict)
    except:
        pass
    # show progress bar
    sleep(0.1)


print(rows_list)

expoort_data_frame = pd.DataFrame(rows_list)

expoort_data_frame.to_csv('ArtistsDataFromRijks.csv', index=False)
