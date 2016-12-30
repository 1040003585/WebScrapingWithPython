# -*- coding: utf-8 -*-

import json
import csv
from downloader import Downloader


def main():
    D = Downloader()
    url = 'https://c2b-services.bmw.com/c2b-localsearch/services/api/v3/clients/BMWDIGITAL_DLO/DE/pois?country=DE&category=BM&maxResults=%d&language=en&lat=52.507537768880056&lng=13.425269635701511'
    jsonp = D(url % 1000)
    pure_json = jsonp[jsonp.index('(') + 1 : jsonp.rindex(')')]
    dealers = json.loads(pure_json)
    with open('bmw.csv', 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(['Name', 'Latitude', 'Longitude'])
        for dealer in dealers['data']['pois']:
            name = dealer['name'].encode('utf-8')
            lat, lng = dealer['lat'], dealer['lng']
            writer.writerow([name, lat, lng])

    
if __name__ == '__main__':
    main() 
