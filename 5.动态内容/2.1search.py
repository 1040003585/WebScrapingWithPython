# -*- coding: utf-8 -*-

import json
import string
import downloader

def main():
    #	template_url = 'http://example.webscraping.com/ajax/search.json?page={}&page_size=10&search_term={}'
    template_url = 'http://127.0.0.1:8000/places/ajax/search.json?&page={}&page_size=10&search_term={}'
    countries = set()
    download = downloader.Downloader()

    for letter in string.lowercase:
        page = 0
        while True:
            html = download(template_url.format(page, letter))
            try:
                ajax = json.loads(html)
            except ValueError as e:
                print e
                ajax = None
            else:
                for record in ajax['records']:
                    countries.add(record['country'])
            page += 1
            if ajax is None or page >= ajax['num_pages']:
                break    
    open('2.1countries.txt', 'w').write('\n'.join(sorted(countries)))

if __name__ == '__main__':
    main()
