import pickle
import pandas as pd
from get_news import scrap_rss

with open('companies.pkl', 'rb') as f:
    companies = pickle.load(f)

with open('urls.pkl', 'rb') as f:
    urls = pickle.load(f)

print(urls)


# def download_news(urls):
#     for url in urls.items():
#         scrap_rss(url[0], url[1])
#
#
with open('articles.csv', 'rb') as f:
    data = pd.read_csv(f)

print(data)
#
# download_news(urls)
