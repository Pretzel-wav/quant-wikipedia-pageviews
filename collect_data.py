import requests
import csv
import os

def read_company_urls(file_path):
    urls = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            urls.append(row[2]) 
    return urls

def get_pageviews(title):
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageviews&titles={title}"
    response = requests.get(url)
    data = response.json()
    if 'query' not in data or 'pages' not in data['query']:
        return None
    page_id = list(data['query']['pages'].keys())[0]
    pageviews = data['query']['pages'][page_id]['pageviews']
    return pageviews

def save_pageviews(company_name, pageviews):
    file_path = f'pageviews/{company_name}.csv'
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Pageviews'])
        for date, views in pageviews.items():
            writer.writerow([date, views])

file_path = 'company_info.csv'  
urls = read_company_urls(file_path)

for url in urls:
    print(f'Getting pageviews for {url}')
    title = url.split('/')[-1]  # Extract the page title from the URL
    if not title:
        print(f'No title found for {url}. Likely a result of not having a URL.')
        continue
    if os.path.exists(f'pageviews/{title}.csv'):
        print(f'Already exists: {title}.csv')
        continue
    pageviews = get_pageviews(title)
    if not pageviews:
        print(f'No pageviews found for {title}')
        continue
    save_pageviews(title, pageviews)