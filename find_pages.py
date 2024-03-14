from bs4 import BeautifulSoup
import requests
import os

def _make_soup(url, out_path):
    print(f'Writing soup from {url} to {out_path}')
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    with open(f'{out_path}', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    return soup

def _read_soup(path):
    print(f'Reading soup from {path}')
    with open(path, 'r', encoding='utf-8') as file:
        soup = file.read()
    soup = BeautifulSoup(soup, 'html.parser')
    return soup

def get_soup(url, out_path):
    if not os.path.exists(out_path):
       _make_soup(url, out_path)
    return _read_soup(out_path)

url = 'https://www.quiverquant.com/sources/wikipedia'
soup = get_soup(url, 'qq_wikipedia_soup.txt')

elements = soup.select("#myTable > tbody > tr > td:nth-child(1) > a:nth-child(1)")
symbol_list = [element.text for element in elements]
symbol_list = {symbol.replace('.A','').replace('.B','') for symbol in symbol_list}
print(f'Number of symbols on Quiver Quant: {len(symbol_list)}') # 1286 items

fmp_api_key = '8d3267e5e648c6e409dee93202f8e64f'
multiple_prices_endpoint = 'https://financialmodelingprep.com/api/v3/quote/'
query_string = ','.join(symbol_list)
query_url = f'{multiple_prices_endpoint}{query_string}?apikey={fmp_api_key}'
response = requests.get(query_url)
response_json = response.json()
symbol_dict = {item['symbol'] : {'name': item.get('name', None), 'url': None} for item in response_json}
print(len(symbol_dict)) # 1282 items

symbol_dict['CNVS'] = {'name': 'Cineverse Corp', 'url': None}
symbol_dict['MOG'] = {'name': 'Moog Inc', 'url': None}

# find wikipedia page via scraping
letters = [chr(i) for i in range(ord('A'), ord('Z')+1)]
letters.append('0-9')
for letter in letters:
    url = f'https://en.wikipedia.org/wiki/Companies_listed_on_the_New_York_Stock_Exchange_({letter})'
    file_path = f'company_lists/page_{letter}.txt'
    print(f'Getting soup for {letter} at {url}')
    soup = get_soup(url, file_path)

    table_rows = soup.select('.mw-content-ltr > table:nth-child(7) > tbody:nth-child(1) > tr')
    print(f'Found {len(table_rows)} table rows')
    for row in table_rows:
        name_cell = row.select_one('td:nth-of-type(1)')
        symbol_cell = row.select_one('td:nth-of-type(2)')
        if name_cell and symbol_cell:
            name = name_cell.text.strip()
            symbol = symbol_cell.text.strip()
            name_link = name_cell.select_one('a')
            url = name_link.get('href', None).strip() if name_link else None
            
            if symbol in symbol_dict:
                symbol_dict[symbol]['name'] = name
                symbol_dict[symbol]['url'] = url

symbols_with_url = [symbol for symbol, data in symbol_dict.items() if data['url']]
symbols_without_url = [symbol for symbol, data in symbol_dict.items() if not data['url']]
print(f'Symbols with url: {len(symbols_with_url)}')
print(f'Symbols without url: {len(symbols_without_url)}')

# scrape NASDAQ pages
def scrape_nasdaq_page(company_name: str):
    print(f'Getting soup for {company_name}')
    page_start = company_name.replace(' ', '+')
    url = f'https://en.wikipedia.org/w/index.php?title=Category:Companies_listed_on_the_Nasdaq&pagefrom={page_start}'
    soup = get_soup(url, f'nasdaq/{page_start}.txt')
    groups = soup.select('div.mw-content-ltr:nth-child(5) > div:nth-child(1) > div')
    if not groups: # for some reason, there's a different layout for some pages
        groups = soup.select('div.mw-content-ltr:nth-child(4) > div:nth-child(1) > div')
    company_dict = {}
    name = company_name
    print(f'Found {len(groups)} groups')
    for group in groups:
        group_name = group.select_one('h3').text.strip()
        company_list = group.select('ul > li')
        print(f'Found {len(company_list)} companies in group {group_name}')
        for company in company_list:
            name = company.text.strip()
            name_link = company.select_one('a').get('href', None)
            url = name_link.strip() if name_link else None
            company_dict[name] = url
    return company_dict, name

start_company = '1-800-Flowers.com, Inc.'
nasdaq_dict = {}
while True:
    new_dict, last_company = scrape_nasdaq_page(start_company)
    nasdaq_dict = {**nasdaq_dict, **new_dict}
    print(f'nasdaq_dict has {len(nasdaq_dict)} values')
    if start_company == last_company:
        break
    start_company = last_company

# combine nasdaq_dict with symbol_dict
for nasdaq_name, nasdaq_url in nasdaq_dict.items():
    for symbol, data in symbol_dict.items():
        if data['name'] and nasdaq_name.lower() in data['name'].lower():
            data['url'] = nasdaq_url

print('After NASDAQ')
symbols_with_url = [symbol for symbol, data in symbol_dict.items() if data['url']]
symbols_without_url = [symbol for symbol, data in symbol_dict.items() if not data['url']]
print(f'Symbols with url: {len(symbols_with_url)}')
print(f'Symbols without url: {len(symbols_without_url)}')

print({symbol: data for symbol, data in symbol_dict.items() if not data['url']})