import csv
import requests
from bs4 import BeautifulSoup
import feedparser


def save_data(article_list):
    with open('articles.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=article_list[0])
        writer.writeheader()
        writer.writerows(article_list)


def scrap_text(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.text, features='lxml')
    div = soup.find('div', {'class': 'WYSIWYG articlePage'})
    paragraphs = div.findAll('p')
    article_text = ""

    for paragraph in paragraphs:
        article_text += paragraph.text
    index_start = article_text.find('\n')
    index_finish = article_text.find("Читайте оригинальную статью")
    return article_text[index_start + 1:index_finish]


def scrap_rss(url):
    article_list = []

    try:
        feed = feedparser.parse(url)
        for a in feed['items']:
            title = a.title
            link = a.link
            published = a.published
            text = scrap_text(link)
            article = {
                'title': title,
                'link': link,
                'published': published,
                'text': text.replace('\xa0',' ')
            }
            article_list.append(article)
            print(article_list)
        return save_data(article_list)
    except Exception as e:
        print('The scraping is failed. Exception:')
        print(e)

